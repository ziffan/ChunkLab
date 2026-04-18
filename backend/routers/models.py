from fastapi import APIRouter, Query
from backend.services.model_detector import detect_models

router = APIRouter()


@router.get("/models")
async def list_models(
    provider: str = Query(..., description="Provider ID: ollama, lmstudio, openai, etc."),
    api_key: str | None = Query(None, description="Optional API key override"),
):
    return await detect_models(provider, api_key)
