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

import re
from fastapi import APIRouter
from backend.models.requests import ChunkRequest
from backend.models.responses import ChunkResponse, ChunkData, ChunkError, MetadataItem
from backend.services.chunker import chunk_text
from backend.services.metadata_extractor import extract_metadata_from_compiled, validate_pattern

router = APIRouter()


@router.post("/chunk", response_model=ChunkResponse)
async def chunk_endpoint(req: ChunkRequest):
    if len(req.markdown) > 0 and req.chunk_overlap >= req.chunk_size:
        return ChunkResponse(
            chunks=[],
            total_chunks=0,
            error=ChunkError(
                code="INVALID_PARAMETERS",
                message=f"chunk_overlap ({req.chunk_overlap}) must be strictly less than chunk_size ({req.chunk_size})",
                pattern_id=None,
            ),
        )

    # Pre-compile patterns once for the entire request
    compiled_patterns = []
    for rp in req.regex_patterns:
        try:
            compiled = re.compile(rp.pattern)
            compiled_patterns.append(({"id": rp.id, "label": rp.label}, compiled))
        except re.error as e:
            return ChunkResponse(
                chunks=[],
                total_chunks=0,
                error=ChunkError(
                    code="INVALID_REGEX",
                    message=f"Pattern '{rp.pattern}' is invalid: {e}",
                    pattern_id=rp.id,
                ),
            )

    raw_chunks = chunk_text(req.markdown, req.chunk_size, req.chunk_overlap)
    chunk_data_list = []

    for raw in raw_chunks:
        metadata = extract_metadata_from_compiled(raw["text"], compiled_patterns)
        
        metadata_items = [MetadataItem(**m) for m in metadata]
        chunk_data_list.append(ChunkData(
            index=raw["index"],
            text=raw["text"],
            char_count=raw["char_count"],
            overlap_start_chars=raw["overlap_start_chars"],
            overlap_end_chars=raw["overlap_end_chars"],
            metadata=metadata_items,
        ))

    return ChunkResponse(
        chunks=chunk_data_list,
        total_chunks=len(chunk_data_list),
        error=None,
    )
