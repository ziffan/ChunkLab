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
from backend.services.chunker import chunk_by_strategy, chunk_text
from backend.services.metadata_extractor import extract_metadata_from_compiled
from backend.services.quality_metrics import (
    boundary_quality,
    information_density,
    is_complete,
)
from backend.services.md_metadata import md_path_metadata

router = APIRouter()


@router.post("/chunk", response_model=ChunkResponse)
async def chunk_endpoint(req: ChunkRequest):
    if (
        req.strategy == "fixed"
        and len(req.markdown) > 0
        and req.chunk_overlap >= req.chunk_size
    ):
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

    if req.strategy == "fixed":
        raw_chunks = chunk_text(req.markdown, req.chunk_size, req.chunk_overlap)
    else:
        try:
            sp = dict(req.strategy_params)
            if req.strategy == "recursive":
                sp.setdefault("chunk_size", req.chunk_size)
                sp.setdefault("chunk_overlap", req.chunk_overlap)
            raw_chunks = chunk_by_strategy(req.markdown, req.strategy, **sp)
        except ValueError as e:
            return ChunkResponse(
                chunks=[],
                total_chunks=0,
                error=ChunkError(
                    code="INVALID_PARAMETERS", message=str(e), pattern_id=None
                ),
            )
    chunk_data_list = []

    for raw in raw_chunks:
        metadata = extract_metadata_from_compiled(raw["text"], compiled_patterns)

        # legal_id supplies its own structural metadata; skip md_path for this strategy
        if req.strategy == "legal_id":
            legal_items = [
                MetadataItem(pattern_id="_legal_section", label="section",      value=raw.get("_legal_section", "")),
                MetadataItem(pattern_id="_legal_path",    label="legal_path",   value=raw.get("_legal_path",    "")),
                MetadataItem(pattern_id="_legal_unit",    label="unit",         value=raw.get("_legal_unit",    "")),
                MetadataItem(pattern_id="_legal_number",  label="pasal_number", value=raw.get("_legal_number",  "")),
            ]
            all_metadata = [m for m in legal_items if m.value] + [
                MetadataItem(**m) for m in metadata
            ]
        else:
            path_item = md_path_metadata(req.markdown, raw["text"])
            all_metadata = ([MetadataItem(**path_item)] if path_item else []) + [
                MetadataItem(**m) for m in metadata
            ]
        chunk_data_list.append(
            ChunkData(
                index=raw["index"],
                text=raw["text"],
                char_count=raw["char_count"],
                overlap_start_chars=raw["overlap_start_chars"],
                overlap_end_chars=raw["overlap_end_chars"],
                metadata=all_metadata,
                boundary_quality=boundary_quality(raw["text"]),
                information_density=information_density(raw["text"]),
                is_complete=is_complete(raw["text"]),
            )
        )

    return ChunkResponse(
        chunks=chunk_data_list,
        total_chunks=len(chunk_data_list),
        error=None,
    )
