# Copyright [2026] Ziffan (Ziffany Firdinal)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
import asyncio
import httpx

from backend.models.responses import TokenizeResponse, TokenizeError
from backend.mocks.mock_tokenizer import mock_estimate

logger = logging.getLogger(__name__)


async def _tokenize_ollama(texts: list[str], model_name: str) -> list[int]:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = []
        for text in texts:
            tasks.append(client.post(
                f"{base_url}/api/tokenize",
                json={"model": model_name or "llama3.1", "prompt": text},
            ))
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        results = []
        for i, resp in enumerate(responses):
            if isinstance(resp, Exception):
                logger.error(f"Error tokenizing chunk {i}: {resp}")
                # Fallback to character-based estimate if one fails? 
                # Or just raise. Let's raise for now to be consistent with previous behavior.
                raise resp
            resp.raise_for_status()
            results.append(resp.json()["count"])

    return results


async def estimate_tokens(
    texts: list[str],
    provider: str,
    model_name: str | None,
    mock_mode: bool,
) -> TokenizeResponse:
    if mock_mode or provider == "mock":
        counts = mock_estimate(texts)
        return TokenizeResponse(
            token_counts=counts,
            model_used="mock",
            provider="mock",
            is_mock=True,
            error=None,
        )

    if provider in ("openai", "openrouter", "lmstudio"):
        try:
            import tiktoken
            enc = tiktoken.get_encoding("cl100k_base")
            counts = [len(enc.encode(t)) for t in texts]
            return TokenizeResponse(
                token_counts=counts,
                model_used=model_name or "cl100k_base",
                provider=provider,
                is_mock=False,
                error=None,
            )
        except ImportError:
            counts = mock_estimate(texts)
            return TokenizeResponse(
                token_counts=counts,
                model_used="mock",
                provider="mock",
                is_mock=True,
                error=TokenizeError(
                    code="PROVIDER_UNAVAILABLE",
                    message="tiktoken is not installed. Falling back to mock tokenizer.",
                    original_provider=provider,
                ),
            )

    if provider in ("gemini", "anthropic"):
        counts = mock_estimate(texts)
        return TokenizeResponse(
            token_counts=counts,
            model_used="mock",
            provider="mock",
            is_mock=True,
            error=None,
        )

    if provider == "ollama":
        try:
            counts = await _tokenize_ollama(texts, model_name or "llama3.1")
            return TokenizeResponse(
                token_counts=counts,
                model_used=model_name or "llama3.1",
                provider=provider,
                is_mock=False,
                error=None,
            )
        except Exception:
            counts = mock_estimate(texts)
            return TokenizeResponse(
                token_counts=counts,
                model_used="mock",
                provider="mock",
                is_mock=True,
                error=TokenizeError(
                    code="PROVIDER_UNAVAILABLE",
                    message=f"Ollama at {os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')} is not reachable. Falling back to mock tokenizer.",
                    original_provider="ollama",
                ),
            )

    counts = mock_estimate(texts)
    return TokenizeResponse(
        token_counts=counts,
        model_used="mock",
        provider="mock",
        is_mock=True,
        error=None,
    )
