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

import json
import os

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from backend.main import app

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures")


def load_fixture(name):
    with open(os.path.join(FIXTURES_DIR, name), encoding="utf-8") as f:
        return json.load(f)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_chunk_normal(client):
    fixture = load_fixture("normal.json")
    resp = await client.post("/api/chunk", json=fixture["request"])
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_chunks"] == 3
    assert data["error"] is None


@pytest.mark.asyncio
async def test_chunk_error_regex(client):
    fixture = load_fixture("error_regex.json")
    resp = await client.post("/api/chunk", json=fixture["request"])
    assert resp.status_code == 200
    data = resp.json()
    assert data["error"] is not None
    assert data["error"]["code"] == "INVALID_REGEX"


@pytest.mark.asyncio
async def test_chunk_empty(client):
    fixture = load_fixture("empty.json")
    resp = await client.post("/api/chunk", json=fixture["request"])
    assert resp.status_code == 200
    data = resp.json()
    assert data["chunks"] == []
    assert data["error"] is None


@pytest.mark.asyncio
async def test_tokenize_mock(client):
    payload = {
        "texts": ["hello world", "test text"],
        "provider": "mock",
    }
    resp = await client.post("/api/tokenize", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_mock"] is True


@pytest.mark.asyncio
async def test_regex_test_valid(client):
    payload = {"pattern": r"\d+", "text": "abc123def456"}
    resp = await client.post("/api/regex/test", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_valid"] is True
    assert data["match_count"] == 2


@pytest.mark.asyncio
async def test_regex_test_invalid(client):
    payload = {"pattern": "[bad", "text": "x"}
    resp = await client.post("/api/regex/test", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_valid"] is False
