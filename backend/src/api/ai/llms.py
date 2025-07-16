import os


from langchain_openai import ChatOpenAI
from langchain_openai import AzureChatOpenAI

from dotenv import load_dotenv
load_dotenv()

# Azure OpenAI environment variables
AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

# OpenAI environment variables (fallback)
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL") or None
OPENAI_MODEL_NAME = os.environ.get("OPENAI_MODEL_NAME") or 'gpt-4o-mini'
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not AZURE_OPENAI_KEY:
    raise NotImplementedError("OpenAI API key is required")

def get_openai_llm():
    if not all([AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT]):
        raise EnvironmentError("Missing Azure OpenAI configuration.")

    return AzureChatOpenAI(
        azure_deployment=AZURE_OPENAI_DEPLOYMENT,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
    )
