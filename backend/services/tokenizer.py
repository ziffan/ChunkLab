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


def _tiktoken_estimate(texts: list[str]) -> list[int]:
    try:
        import tiktoken

        enc = tiktoken.get_encoding("cl100k_base")
        return [len(enc.encode(t)) for t in texts]
    except ImportError:
        return mock_estimate(texts)


async def _tokenize_ollama(texts: list[str], model_name: str) -> tuple[list[int], str]:
    """Return (counts, method).  method = 'native' | 'tiktoken_proxy'.
    Raises httpx.ConnectError when Ollama is unreachable."""
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = [
            client.post(
                f"{base_url}/api/tokenize",
                json={"model": model_name, "prompt": text},
            )
            for text in texts
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # /api/tokenize was added in Ollama 0.3.x — fall back gracefully for older builds
        for resp in responses:
            if not isinstance(resp, Exception) and resp.status_code == 404:
                logger.info(
                    "/api/tokenize not available; using tiktoken cl100k_base proxy"
                )
                return _tiktoken_estimate(texts), "tiktoken_proxy"
            break

        results = []
        for i, resp in enumerate(responses):
            if isinstance(resp, Exception):
                raise resp
            resp.raise_for_status()
            results.append(resp.json()["count"])

    return results, "native"


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

    if provider == "gemini":
        # Gemini tokenizer API requires auth; approximate with mock.
        # text-embedding-004 uses a SentencePiece tokenizer not yet wrapped here.
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
            counts, method = await _tokenize_ollama(texts, model_name or "llama3.1")
            proxy_error = None
            if method == "tiktoken_proxy":
                proxy_error = TokenizeError(
                    code="OLLAMA_TOKENIZE_UNSUPPORTED",
                    message="Ollama /api/tokenize not available in this version. Using tiktoken cl100k_base as proxy.",
                    original_provider="ollama",
                )
            return TokenizeResponse(
                token_counts=counts,
                model_used=model_name or "llama3.1",
                provider=provider,
                is_mock=False,
                error=proxy_error,
            )
        except Exception:
            counts = mock_estimate(texts)
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            return TokenizeResponse(
                token_counts=counts,
                model_used="mock",
                provider="mock",
                is_mock=True,
                error=TokenizeError(
                    code="PROVIDER_UNAVAILABLE",
                    message=f"Ollama at {base_url} is not reachable. Falling back to mock tokenizer.",
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
