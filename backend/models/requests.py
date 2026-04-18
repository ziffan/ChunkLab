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

from typing import Literal
from pydantic import BaseModel, Field, model_validator


class RegexPattern(BaseModel):
    id: str = Field(..., min_length=1, max_length=64)
    label: str = Field(..., min_length=1, max_length=64)
    pattern: str = Field(..., min_length=1, max_length=1000)


class ChunkRequest(BaseModel):
    markdown: str = Field(default="", max_length=500000)
    chunk_size: int = Field(default=512, ge=1, le=8192)
    chunk_overlap: int = Field(default=50, ge=0)
    regex_patterns: list[RegexPattern] = Field(default=[], max_length=10)

    @model_validator(mode='after')
    def validate_overlap(self):
        if len(self.markdown) > 0 and self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                f"chunk_overlap ({self.chunk_overlap}) must be strictly less than chunk_size ({self.chunk_size})"
            )
        return self


class TokenizeRequest(BaseModel):
    model_config = {"protected_namespaces": ()}
    texts: list[str] = Field(..., min_length=1, max_length=500)
    provider: Literal["mock", "openai", "gemini", "anthropic", "openrouter", "ollama", "lmstudio"]
    model_name: str | None = Field(default=None, max_length=128)


class RegexTestRequest(BaseModel):
    pattern: str = Field(..., max_length=1000)
    text: str = Field(..., max_length=500000)
