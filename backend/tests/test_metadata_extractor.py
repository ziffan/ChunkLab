from backend.services.metadata_extractor import extract_metadata, validate_pattern


def test_date_regex_extracts_value():
    text = "Date: 2024-01-15"
    patterns = [{"id": "p1", "label": "Date", "pattern": r"\d{4}-\d{2}-\d{2}"}]
    metadata, error = extract_metadata(text, patterns)

    assert error is None
    assert len(metadata) == 1
    assert metadata[0]["value"] == "2024-01-15"


def test_author_capture_group():
    text = "Author: Alice"
    patterns = [{"id": "p1", "label": "Author", "pattern": r"Author:\s*(\w+)"}]
    metadata, error = extract_metadata(text, patterns)

    assert error is None
    assert len(metadata) == 1
    assert metadata[0]["value"] == "Alice"


def test_invalid_pattern_returns_error():
    text = "some text"
    patterns = [{"id": "p1", "label": "Bad", "pattern": "[unclosed"}]
    metadata, error = extract_metadata(text, patterns)

    assert metadata == []
    assert error is not None
    assert error["code"] == "INVALID_REGEX"
    assert error["pattern_id"] == "p1"


def test_validate_pattern_valid():
    is_valid, err_msg = validate_pattern(r"\d+")
    assert is_valid is True
    assert err_msg is None


def test_validate_pattern_invalid():
    is_valid, err_msg = validate_pattern("[unclosed")
    assert is_valid is False
    assert err_msg is not None
    assert len(err_msg) > 0
