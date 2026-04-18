import re
from typing import Optional, Dict, List, Tuple


def extract_metadata_from_compiled(text: str, compiled_patterns: List[Tuple[Dict, re.Pattern]]) -> List[Dict]:
    metadata_list = []
    
    for p, compiled in compiled_patterns:
        if compiled.groups > 0:
            for m in compiled.finditer(text):
                val = m.group(1)
                if val is not None:
                    metadata_list.append({
                        "pattern_id": p["id"],
                        "label": p["label"],
                        "value": str(val),
                    })
        else:
            for m in compiled.finditer(text):
                metadata_list.append({
                    "pattern_id": p["id"],
                    "label": p["label"],
                    "value": str(m.group(0)),
                })

    return metadata_list


def extract_metadata(text: str, patterns: List[Dict]) -> Tuple[List[Dict], Optional[Dict]]:
    # Legacy wrapper or for single calls
    compiled_patterns = []
    for p in patterns:
        try:
            compiled = re.compile(p["pattern"])
            compiled_patterns.append((p, compiled))
        except re.error as e:
            return ([], {"code": "INVALID_REGEX", "message": f"Pattern '{p['pattern']}' is invalid: {e}", "pattern_id": p["id"]})
            
    return (extract_metadata_from_compiled(text, compiled_patterns), None)


def validate_pattern(pattern: str) -> Tuple[bool, Optional[str]]:
    try:
        re.compile(pattern)
        return (True, None)
    except re.error as e:
        return (False, str(e))
