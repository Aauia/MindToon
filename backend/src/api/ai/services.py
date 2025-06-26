import os, math, requests
from PIL import Image
from io import BytesIO
from api.ai.llms import get_openai_llm
from api.ai.schemas import (
    EmailMessageSchema, ScenarioSchema, ComicPanelsResponseSchema,
    ComicPanelsWithImagesResponseSchema, ComicPanelWithImageSchema, ComicsPageSchema
)



def generate_email_message(query:str)->EmailMessageSchema:
    llm_base = get_openai_llm()
    llm = llm_base.with_structured_output(EmailMessageSchema)

    messages = [
        (
            "system",
            "You are a helpful assistant for research and composing plaintext emails. Do not use markdown in your responses.",
        ),
        (
            "human",
            f"Create an email about the benefits of {query}. Do not use markdown in your response, only plaintext.",
        ),
    ]

    return llm.invoke(messages)


def generate_scenario(prompt: str) -> ScenarioSchema:
    llm_base = get_openai_llm()
    llm = llm_base.with_structured_output(ScenarioSchema)

    messages = [
        (
            "system",
            "You are a creative assistant. Given a user's prompt, first discover the most fitting genre (e.g., sci-fi, fantasy, mystery, etc.), then generate a fascinating, detailed scenario based on the user's text. Respond only with the genre and the scenario, no markdown, only plaintext.",
        ),
        (
            "human",
            f"Prompt: {prompt}",
        ),
    ]

    return llm.invoke(messages)


def generate_comics_page(user_text: str, genre: str = None, art_style: str = None) -> ComicsPageSchema:
    llm_base = get_openai_llm()

    if not genre or not art_style:
        llm = llm_base.with_structured_output(ScenarioSchema)
        messages = [
            ("system", "You are a creative assistant. Given a user's prompt, identify the most fitting genre and consistent art style."),
            ("human", f"Prompt: {user_text}"),
        ]
        scenario_info = llm.invoke(messages)
        genre = genre or getattr(scenario_info, 'genre', 'fantasy')
        art_style = art_style or getattr(scenario_info, 'art_style', 'comic book style')

    scenario_llm = llm_base.with_structured_output(ScenarioSchema)
    scenario_msg = [
        ("system", "You are a creative assistant. Given a user's prompt, generate a scenario for the given genre."),
        ("human", f"Prompt: {user_text}\nGenre: {genre}"),
    ]
    scenario_obj = scenario_llm.invoke(scenario_msg)
    scenario = getattr(scenario_obj, 'scenario', user_text)

    panels_llm = llm_base.with_structured_output(ComicPanelsResponseSchema)
    panels_msg = [
        ("system", f"You are a comic writer. Break the scenario into comic panels with prompts in style: '{art_style}', '{genre}'."),
        ("human", f"Scenario: {scenario}"),
    ]
    panels_response = panels_llm.invoke(panels_msg)

    api_key = os.environ.get("OPENAI_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    url = "https://api.openai.com/v1/images/generations"
    panels_with_images = []

    for panel in panels_response.panels:
        prompt = f"{panel.image_prompt}, {art_style}, {genre}"
        data = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024"
        }
        response = requests.post(url, headers=headers, json=data)
        image_url = None
        if response.status_code == 200:
            result = response.json()
            image_url = result["data"][0]["url"] if result.get("data") else None

        panels_with_images.append(ComicPanelWithImageSchema(
            panel=panel.panel,
            image_prompt=prompt,
            image_url=image_url,
            dialogue=panel.dialogue
        ))

    return ComicsPageSchema(
        genre=genre,
        art_style=art_style,
        panels=panels_with_images
    )

def combine_panel_images_to_sheet(panel_image_urls, output_path="static/comic_sheet.png", layout="auto"):
    images = [Image.open(BytesIO(requests.get(url).content)) for url in panel_image_urls]
    width, height = images[0].size
    n = len(images)
    columns = 1 if n <= 3 else 2
    rows = math.ceil(n / columns)
    sheet = Image.new('RGB', (width * columns, height * rows), color=(255, 255, 255))
    for idx, img in enumerate(images):
        x = (idx % columns) * width
        y = (idx // columns) * height
        sheet.paste(img, (x, y))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sheet.save(output_path)
    return f"/{output_path}"
