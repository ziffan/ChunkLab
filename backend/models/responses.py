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

from pydantic import BaseModel


class ChunkError(BaseModel):
    code: str
    message: str
    pattern_id: str | None


class MetadataItem(BaseModel):
    pattern_id: str
    label: str
    value: str


class ChunkData(BaseModel):
    index: int
    text: str
    char_count: int
    overlap_start_chars: int
    overlap_end_chars: int
    metadata: list[MetadataItem]


class ChunkResponse(BaseModel):
    chunks: list[ChunkData]
    total_chunks: int
    error: ChunkError | None


class TokenizeError(BaseModel):
    code: str
    message: str
    original_provider: str


class TokenizeResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    token_counts: list[int]
    model_used: str
    provider: str
    is_mock: bool
    error: TokenizeError | None


class RegexMatch(BaseModel):
    value: str
    start: int
    end: int


class RegexError(BaseModel):
    code: str
    message: str


class RegexTestResponse(BaseModel):
    is_valid: bool
    match_count: int
    matches: list[RegexMatch]
    truncated: bool
    error: RegexError | None


class HealthResponse(BaseModel):
    status: str
    version: str
