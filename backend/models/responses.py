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
