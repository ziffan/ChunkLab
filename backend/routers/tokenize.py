import os

from fastapi import APIRouter
from backend.models.requests import TokenizeRequest
from backend.models.responses import TokenizeResponse
from backend.services.tokenizer import estimate_tokens

router = APIRouter()


@router.post("/tokenize", response_model=TokenizeResponse)
async def tokenize_endpoint(req: TokenizeRequest):
    mock_mode = os.getenv("MOCK_MODE", "true").lower() == "true"
    return await estimate_tokens(req.texts, req.provider, req.model_name, mock_mode)
