def mock_estimate(texts: list[str]) -> list[int]:
    if not texts:
        return []

    result = []
    for text in texts:
        word_count = len(text.split())
        result.append(max(1, int(word_count * 1.3)))

    return result
