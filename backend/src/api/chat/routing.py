from typing import List
from fastapi import APIRouter, Depends, Body
from sqlmodel import Session, select
from .models import ChatMessage, ChatMessagePayload, ChatMessageListItem, ComicsPage, ComicsPageCreate
from api.db import get_session
from api.ai.schemas import EmailMessageSchema, ScenarioSchema, ComicPanelsResponseSchema, ComicPanelsWithImagesResponseSchema, ComicsPageSchema
from api.ai.services import generate_email_message, generate_scenario, generate_comics_page, combine_panel_images_to_sheet
from pydantic import BaseModel
from fastapi.responses import JSONResponse

router = APIRouter()

# ComicsPagePayload must be defined before use in endpoints
class ComicsPagePayload(BaseModel):
    message: str
    genre: str | None = None
    art_style: str | None = None

#/api/chats/
@router.get("/")
def chat_health():
    return {"status": "ok"}

#/api/chats/recent/
@router.get("/recent",response_model=List[ChatMessageListItem])
def chat_list_messages(session: Session = Depends(get_session)):
    query = select(ChatMessage)  # sql - query
    results = session.exec(query).fetchall()[:10]
    return results

#http post -> payload = {"message":"Hello world"} -> {"message":"hello world", "id": 1}
#curl -X POST -d '{"message":"Hello world"}' -H "Content-Type:application/json"  http://localhost:8080/api/chats


@router.post("/scenario/", response_model=ScenarioSchema)
def create_scenario(payload: ChatMessagePayload):
    response = generate_scenario(payload.message)
    return response


@router.get("/recent", response_model=List[ChatMessageListItem])
def chat_list_messages(session: Session = Depends(get_session)):
    query = select(ChatMessage)
    results = session.exec(query).fetchall()[:10]
    return results

@router.post("/scenario/comic/full", summary="Generate full comic (panels + sheet)")
def create_comics_full(payload: ComicsPagePayload = Body(...)):
    comics_page: ComicsPageSchema = generate_comics_page(
        user_text=payload.message,
        genre=payload.genre,
        art_style=payload.art_style
    )

    panel_image_urls = [panel.image_url for panel in comics_page.panels]
    sheet_url = combine_panel_images_to_sheet(panel_image_urls)

    result = comics_page.dict()
    result["sheet_url"] = sheet_url
    return JSONResponse(content=result)


@router.post("/scenario/comic/sheet/")
def create_comics_sheet(payload: ComicsPagePayload = Body(...), session: Session = Depends(get_session)):
    comics_page = generate_comics_page(payload.message, payload.genre, payload.art_style)
    panel_image_urls = [panel.image_url for panel in comics_page.panels]
    sheet_url = combine_panel_images_to_sheet(panel_image_urls)
    # Save to database
    db_obj = ComicsPage(
        user_message=payload.message,
        genre=comics_page.genre,
        art_style=comics_page.art_style,
        scenario=" ".join([p["image_prompt"] for p in [panel.dict() for panel in comics_page.panels]]),
        panels=[panel.dict() for panel in comics_page.panels],
        sheet_url=sheet_url
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    # Return comics page info + sheet url + db id
    result = comics_page.dict()
    result["sheet_url"] = sheet_url
    result["id"] = db_obj.id
    return JSONResponse(content=result)

@router.get("/scenario/comic/sheet/{comic_id}/", response_model=ComicsPageSchema)
def get_comics_sheet(comic_id: int, session: Session = Depends(get_session)):
    db_obj = session.get(ComicsPage, comic_id)
    if not db_obj:
        return JSONResponse(content={"error": "Not found"}, status_code=404)
    return ComicsPageSchema(
        genre=db_obj.genre,
        art_style=db_obj.art_style,
        panels=db_obj.panels,
        invalid_request=False,
        sheet_url=db_obj.sheet_url
    )
