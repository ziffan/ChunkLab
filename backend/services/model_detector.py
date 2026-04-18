import os
import logging

import httpx

logger = logging.getLogger(__name__)

OLLAMA_KNOWN_MODELS = [
    "llama3.1", "llama3", "mistral", "mixtral", "gemma2", "codellama",
    "phi3", "qwen2", "nomic-embed-text", "mxbai-embed-large",
]

LMSTUDIO_KNOWN_MODELS = [
    "nomic-embed-text", "all-MiniLM-L6-v2", "text-embedding-3-small",
]

OPENAI_EMBEDDING_MODELS = [
    "text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002",
]

GEMINI_EMBEDDING_MODELS = [
    "text-embedding-004", "embedding-001",
]

ANTHROPIC_MODELS = [
    "claude-3-haiku-20240307", "claude-3-sonnet-20240229", "claude-3-opus-20240229",
    "claude-3-5-sonnet-20241022",
]


async def detect_ollama_models() -> dict:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{base_url}/api/tags")
            resp.raise_for_status()
            data = resp.json()
            models = [
                {"id": m.get("name", ""), "name": m.get("name", "")}
                for m in data.get("models", [])
            ]
            return {"available": True, "models": models, "error": None}
    except Exception as e:
        logger.debug(f"Ollama not reachable: {e}")
        return {"available": False, "models": [], "error": str(e)}


async def detect_lmstudio_models() -> dict:
    base_url = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{base_url}/v1/models")
            resp.raise_for_status()
            data = resp.json()
            models = [
                {"id": m.get("id", ""), "name": m.get("id", "")}
                for m in data.get("data", [])
            ]
            return {"available": True, "models": models, "error": None}
    except Exception as e:
        logger.debug(f"LM Studio not reachable: {e}")
        return {"available": False, "models": [], "error": str(e)}


async def detect_openai_models(api_key: str | None = None) -> dict:
    key = api_key or os.getenv("OPENAI_API_KEY", "")
    if not key or key == "your-key-here":
        return {"available": False, "models": [], "error": "No API key configured"}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {key}"},
            )
            if resp.status_code == 401:
                return {"available": False, "models": [], "error": "Invalid API key"}
            resp.raise_for_status()
            data = resp.json()
            embedding_models = [
                {"id": m["id"], "name": m["id"]}
                for m in data.get("data", [])
                if "embed" in m.get("id", "").lower()
            ]
            embedding_models.sort(key=lambda x: x["id"])
            return {"available": True, "models": embedding_models, "error": None}
    except Exception as e:
        logger.debug(f"OpenAI models fetch failed: {e}")
        return {"available": False, "models": OPENAI_EMBEDDING_MODELS, "error": str(e)}


async def detect_openrouter_models(api_key: str | None = None) -> dict:
    key = api_key or os.getenv("OPENROUTER_API_KEY", "")
    headers = {}
    if key and key != "your-key-here":
        headers["Authorization"] = f"Bearer {key}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get("https://openrouter.ai/api/v1/models", headers=headers)
            resp.raise_for_status()
            data = resp.json()
            embedding_models = [
                {"id": m.get("id", ""), "name": m.get("id", "")}
                for m in data.get("data", [])
                if "embed" in m.get("id", "").lower()
            ]
            embedding_models.sort(key=lambda x: x["id"])
            return {"available": True, "models": embedding_models, "error": None}
    except Exception as e:
        logger.debug(f"OpenRouter models fetch failed: {e}")
        return {"available": False, "models": [], "error": str(e)}


async def detect_gemini_models(api_key: str | None = None) -> dict:
    key = api_key or os.getenv("GEMINI_API_KEY", "")
    if not key or key == "your-key-here":
        return {"available": False, "models": [], "error": "No API key configured"}
    return {
        "available": True,
        "models": [{"id": m, "name": m} for m in GEMINI_EMBEDDING_MODELS],
        "error": None,
    }


async def detect_anthropic_models(api_key: str | None = None) -> dict:
    key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
    if not key or key == "your-key-here":
        return {"available": False, "models": [], "error": "No API key configured"}
    return {
        "available": True,
        "models": [{"id": m, "name": m} for m in ANTHROPIC_MODELS],
        "error": None,
    }


async def detect_models(provider: str, api_key: str | None = None) -> dict:
    detectors = {
        "ollama": detect_ollama_models,
        "lmstudio": detect_lmstudio_models,
        "openai": lambda: detect_openai_models(api_key),
        "openrouter": lambda: detect_openrouter_models(api_key),
        "gemini": lambda: detect_gemini_models(api_key),
        "anthropic": lambda: detect_anthropic_models(api_key),
    }
    detector = detectors.get(provider)
    if not detector:
        return {"available": False, "models": [], "error": f"Unknown provider: {provider}"}
    result = await detector()
    result["provider"] = provider
    return result
