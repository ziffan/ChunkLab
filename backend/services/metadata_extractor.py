import re


def extract_metadata(text: str, patterns: list[dict]) -> tuple[list[dict], dict | None]:
    metadata_list = []

    for p in patterns:
        try:
            compiled = re.compile(p["pattern"])
        except re.error as e:
            return ([], {"code": "INVALID_REGEX", "message": f"Pattern '{p['pattern']}' is invalid: {e}", "pattern_id": p["id"]})

        if compiled.groups > 0:
            for m in compiled.finditer(text):
                metadata_list.append({
                    "pattern_id": p["id"],
                    "label": p["label"],
                    "value": str(m.group(1)),
                })
        else:
            for m in compiled.finditer(text):
                metadata_list.append({
                    "pattern_id": p["id"],
                    "label": p["label"],
                    "value": str(m.group(0)),
                })

    return (metadata_list, None)


def validate_pattern(pattern: str) -> tuple[bool, str | None]:
    try:
        re.compile(pattern)
        return (True, None)
    except re.error as e:
        return (False, str(e))
