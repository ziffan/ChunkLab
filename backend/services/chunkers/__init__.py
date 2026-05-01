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

from .fixed import FixedSizeChunker
from .legal_id import LegalStructureChunker
from .markdown_struct import MarkdownStructureChunker
from .recursive import RecursiveCharacterChunker
from .sentence import SentenceChunker
from .sentence_id import IndonesianSentenceSplitter
from .token_aware import TokenAwareChunker

CHUNKER_REGISTRY: dict[str, type] = {
    "fixed": FixedSizeChunker,
    "recursive": RecursiveCharacterChunker,
    "token": TokenAwareChunker,
    "sentence": SentenceChunker,
    "sentence_id": IndonesianSentenceSplitter,
    "markdown": MarkdownStructureChunker,
    "legal_id": LegalStructureChunker,
}

__all__ = [
    "CHUNKER_REGISTRY",
    "FixedSizeChunker",
    "IndonesianSentenceSplitter",
    "LegalStructureChunker",
    "RecursiveCharacterChunker",
    "TokenAwareChunker",
    "SentenceChunker",
    "MarkdownStructureChunker",
]
