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

from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


_SAMPLE_CHUNKS = [
    {"index": 0, "text": "The quick brown fox."},
    {"index": 1, "text": "A slow lazy dog."},
    {"index": 2, "text": "Fast running animals."},
]

_SAMPLE_REQUEST = {
    "query": "fast animals",
    "chunks": _SAMPLE_CHUNKS,
    "top_k": 3,
}


# ---------------------------------------------------------------------------
# Graceful degrade — retrieval unavailable
# ---------------------------------------------------------------------------


class TestRetrieveUnavailable:
    @pytest.mark.asyncio
    async def test_returns_503_when_unavailable(self, client):
        with patch(
            "backend.routers.retrieve.retriever_svc.is_available", return_value=False
        ):
            resp = await client.post("/api/retrieve", json=_SAMPLE_REQUEST)
        assert resp.status_code == 503
        data = resp.json()
        assert data["error"] == "RETRIEVAL_UNAVAILABLE"
        assert "requirements-retrieval.txt" in data["message"]

    @pytest.mark.asyncio
    async def test_503_body_has_message(self, client):
        with patch(
            "backend.routers.retrieve.retriever_svc.is_available", return_value=False
        ):
            resp = await client.post("/api/retrieve", json=_SAMPLE_REQUEST)
        assert "message" in resp.json()


# ---------------------------------------------------------------------------
# Happy path — mocked retriever
# ---------------------------------------------------------------------------


_MOCK_RESULTS = [
    {"index": 2, "score": 0.91, "text": "Fast running animals."},
    {"index": 0, "score": 0.65, "text": "The quick brown fox."},
    {"index": 1, "score": 0.31, "text": "A slow lazy dog."},
]


class TestRetrieveAvailable:
    @pytest.mark.asyncio
    async def test_returns_200_with_results(self, client):
        with patch(
            "backend.routers.retrieve.retriever_svc.is_available", return_value=True
        ), patch(
            "backend.routers.retrieve.retriever_svc.retrieve",
            return_value=_MOCK_RESULTS,
        ):
            resp = await client.post("/api/retrieve", json=_SAMPLE_REQUEST)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_available"] is True
        assert len(data["results"]) == 3

    @pytest.mark.asyncio
    async def test_results_sorted_by_score_desc(self, client):
        with patch(
            "backend.routers.retrieve.retriever_svc.is_available", return_value=True
        ), patch(
            "backend.routers.retrieve.retriever_svc.retrieve",
            return_value=_MOCK_RESULTS,
        ):
            resp = await client.post("/api/retrieve", json=_SAMPLE_REQUEST)
        results = resp.json()["results"]
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    @pytest.mark.asyncio
    async def test_result_schema(self, client):
        with patch(
            "backend.routers.retrieve.retriever_svc.is_available", return_value=True
        ), patch(
            "backend.routers.retrieve.retriever_svc.retrieve",
            return_value=_MOCK_RESULTS[:1],
        ):
            resp = await client.post("/api/retrieve", json=_SAMPLE_REQUEST)
        r = resp.json()["results"][0]
        assert "index" in r and "score" in r and "text" in r

    @pytest.mark.asyncio
    async def test_model_used_in_response(self, client):
        with patch(
            "backend.routers.retrieve.retriever_svc.is_available", return_value=True
        ), patch(
            "backend.routers.retrieve.retriever_svc.retrieve",
            return_value=_MOCK_RESULTS,
        ):
            resp = await client.post("/api/retrieve", json=_SAMPLE_REQUEST)
        assert resp.json()["model_used"] == "intfloat/multilingual-e5-large"

    @pytest.mark.asyncio
    async def test_empty_chunks_returns_422(self, client):
        payload = {"query": "test", "chunks": [], "top_k": 5}
        resp = await client.post("/api/retrieve", json=payload)
        assert resp.status_code == 422
