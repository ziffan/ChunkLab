from fastapi import APIRouter
from backend.models.requests import ChunkRequest
from backend.models.responses import ChunkResponse, ChunkData, ChunkError, MetadataItem
from backend.services.chunker import chunk_text
from backend.services.metadata_extractor import extract_metadata, validate_pattern

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

    for rp in req.regex_patterns:
        is_valid, err_msg = validate_pattern(rp.pattern)
        if not is_valid:
            return ChunkResponse(
                chunks=[],
                total_chunks=0,
                error=ChunkError(
                    code="INVALID_REGEX",
                    message=f"Pattern '{rp.pattern}' is invalid: {err_msg}",
                    pattern_id=rp.id,
                ),
            )

    raw_chunks = chunk_text(req.markdown, req.chunk_size, req.chunk_overlap)
    chunk_data_list = []

    for raw in raw_chunks:
        patterns_as_dicts = [{"id": rp.id, "label": rp.label, "pattern": rp.pattern} for rp in req.regex_patterns]
        metadata, meta_error = extract_metadata(raw["text"], patterns_as_dicts)

        if meta_error is not None:
            return ChunkResponse(
                chunks=[],
                total_chunks=0,
                error=ChunkError(
                    code=meta_error["code"],
                    message=meta_error["message"],
                    pattern_id=meta_error["pattern_id"],
                ),
            )

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
