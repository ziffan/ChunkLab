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

from backend.services.chunker import chunk_text

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures")


def load_fixture(name):
    with open(os.path.join(FIXTURES_DIR, name), encoding="utf-8") as f:
        return json.load(f)


def test_normal_fixture():
    fixture = load_fixture("normal.json")
    req = fixture["request"]
    result = chunk_text(req["markdown"], req["chunk_size"], req["chunk_overlap"])
    expected = fixture["expected_response"]["chunks"]

    assert len(result) == len(expected)
    for r, e in zip(result, expected):
        assert r["index"] == e["index"]
        assert r["char_count"] == e["char_count"]
        assert r["overlap_start_chars"] == e["overlap_start_chars"]
        assert r["overlap_end_chars"] == e["overlap_end_chars"]


def test_edge_case_fixture():
    fixture = load_fixture("edge_case.json")
    req = fixture["request"]
    result = chunk_text(req["markdown"], req["chunk_size"], req["chunk_overlap"])

    assert len(result) == 1
    assert result[0]["overlap_start_chars"] == 0
    assert result[0]["overlap_end_chars"] == 0


def test_empty_markdown():
    fixture = load_fixture("empty.json")
    req = fixture["request"]
    result = chunk_text(req["markdown"], req["chunk_size"], req["chunk_overlap"])

    assert result == []


def test_all_chunks_within_size():
    text = "A" * 500
    result = chunk_text(text, 100, 20)
    for chunk in result:
        assert chunk["char_count"] <= 100


def test_overlap_continuity():
    text = "A" * 500
    chunk_size = 100
    chunk_overlap = 20
    result = chunk_text(text, chunk_size, chunk_overlap)

    for i in range(len(result) - 1):
        if result[i]["char_count"] == chunk_size:
            assert result[i]["text"][chunk_size - chunk_overlap:] == result[i + 1]["text"][:chunk_overlap]
