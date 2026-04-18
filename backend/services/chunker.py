def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[dict]:
    if len(text) == 0:
        return []

    step = chunk_size - chunk_overlap
    start = 0
    chunks = []

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        char_count = len(chunk)
        overlap_start = 0 if start == 0 else min(chunk_overlap, char_count)
        next_start = start + step
        overlap_end = 0
        if next_start < len(text):
            overlap_end = min(chunk_overlap, max(0, end - next_start))

        chunks.append({
            "index": len(chunks),
            "text": chunk,
            "char_count": char_count,
            "overlap_start_chars": overlap_start,
            "overlap_end_chars": overlap_end,
        })
        start = next_start

    return chunks
