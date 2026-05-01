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

from backend.services.chunkers import CHUNKER_REGISTRY


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[dict]:
    """Backward-compatible entry point — dispatches to FixedSizeChunker."""
    chunker = CHUNKER_REGISTRY["fixed"]()
    return chunker.chunk(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)


def chunk_by_strategy(text: str, strategy: str, **params) -> list[dict]:
    """Dispatch to any registered strategy by name."""
    chunker_cls = CHUNKER_REGISTRY.get(strategy)
    if chunker_cls is None:
        raise ValueError(
            f"Unknown chunking strategy: '{strategy}'. Available: {list(CHUNKER_REGISTRY)}"
        )
    return chunker_cls().chunk(text, **params)
