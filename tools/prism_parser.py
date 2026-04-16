"""
PRISM Log parser — independent module for extracting and structuring
PRISM codes from AI responses across all three output modes.

Usage:
    from tools.prism_parser import extract_codes, parse, ParsedLog

    # Extract codes from any source (inline, JSON, tool call)
    codes = extract_codes(response_text)

    # Parse a single code into a structured dict
    parsed = parse("C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro")
    # {
    #   "domain": "MD", "scope": "I", "rev": "X", "time": "i",
    #   "v_lo": "Ben", "v_hi": "Sel",
    #   "e_lo": "Exp", "e_hi": "Gui",
    #   "s_lo": "Usr", "s_hi": "Pro",
    # }

CLI:
    python prism_parser.py "C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro"
    python prism_parser.py --file response.txt
    python prism_parser.py --json '{"response": "...", "prism_log": {"code": "..."}}'
"""
import json
import re
import sys
from typing import Any, Iterable, Optional, List, Dict


PRISM_LOG_PATTERN = re.compile(
    r"C:(?P<domain>\w{2})/(?P<scope>[A-Z])(?P<rev>[A-Z])(?P<time>[a-z])\s*\|\s*"
    r"V:(?P<v_lo>\w{3})<(?P<v_hi>\w{3})\s*\|\s*"
    r"E:(?P<e_lo>\w{3})<(?P<e_hi>\w{3})\s*\|\s*"
    r"S:(?P<s_lo>\w{3})<(?P<s_hi>\w{3})"
)

INLINE_TAG_PATTERN = re.compile(r"<prism_log>\s*(.*?)\s*</prism_log>", re.DOTALL)


def parse(code: str) -> Optional[Dict[str, str]]:
    """
    Parse a PRISM code string into a structured dict.
    Returns None if the code does not match v1.0 format.
    """
    m = PRISM_LOG_PATTERN.match(code.strip())
    return m.groupdict() if m else None


def extract_inline(text: str) -> List[str]:
    """Extract PRISM codes from Mode A (inline <prism_log> tags)."""
    return [m.group(1).strip() for m in INLINE_TAG_PATTERN.finditer(text)]


def extract_from_json(obj: Any) -> List[str]:
    """
    Recursively search a JSON-parsed object for PRISM codes.
    Finds 'code' fields (Mode B/C nested) or direct 'prism_log' string fields.
    """
    results: List[str] = []

    if isinstance(obj, dict):
        # nested: {"prism_log": {"code": "..."}}
        if "code" in obj and isinstance(obj["code"], str):
            if PRISM_LOG_PATTERN.match(obj["code"].strip()):
                results.append(obj["code"].strip())
        # flat: {"prism_log": "..."}
        if "prism_log" in obj and isinstance(obj["prism_log"], str):
            if PRISM_LOG_PATTERN.match(obj["prism_log"].strip()):
                results.append(obj["prism_log"].strip())
        for v in obj.values():
            results.extend(extract_from_json(v))

    elif isinstance(obj, list):
        for item in obj:
            results.extend(extract_from_json(item))

    return results


def extract_codes(source: Any) -> List[str]:
    """
    Extract all PRISM codes from any supported source.

    Accepts:
      - str containing <prism_log> tags (Mode A)
      - str that is valid JSON (Mode B response, Mode C tool_use content)
      - dict or list (already-parsed JSON from an API response)

    Returns deduplicated list of code strings in order found.
    """
    codes: List[str] = []

    if isinstance(source, (dict, list)):
        codes.extend(extract_from_json(source))
    elif isinstance(source, str):
        # Try inline tags first
        codes.extend(extract_inline(source))
        # Try parsing the whole thing as JSON
        stripped = source.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            try:
                obj = json.loads(stripped)
                codes.extend(extract_from_json(obj))
            except json.JSONDecodeError:
                pass
        # Fallback: regex for embedded JSON-ish "code" fields
        if not codes:
            for m in re.finditer(r'\{[^{}]*"code"\s*:\s*"([^"]+)"[^{}]*\}', source):
                candidate = m.group(1).strip()
                if PRISM_LOG_PATTERN.match(candidate):
                    codes.append(candidate)
    else:
        raise TypeError(f"Unsupported source type: {type(source).__name__}")

    # Deduplicate preserving order
    seen = set()
    unique: List[str] = []
    for c in codes:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    return unique


def strip_inline_tag(text: str) -> str:
    """
    Remove <prism_log>...</prism_log> tags from text.
    Use before rendering Mode A responses to end users.
    """
    return INLINE_TAG_PATTERN.sub("", text).strip()


# ---------------- CLI ----------------

def _main():
    args = sys.argv[1:]
    if not args or args[0] in {"-h", "--help"}:
        print(__doc__)
        return

    if args[0] == "--file":
        if len(args) < 2:
            print("Usage: prism_parser.py --file <path>", file=sys.stderr)
            sys.exit(1)
        with open(args[1], "r", encoding="utf-8") as f:
            text = f.read()
        codes = extract_codes(text)
        for c in codes:
            parsed = parse(c)
            print(c)
            if parsed:
                for k, v in parsed.items():
                    print(f"  {k}: {v}")
                print()
        return

    if args[0] == "--json":
        if len(args) < 2:
            print("Usage: prism_parser.py --json '<json string>'", file=sys.stderr)
            sys.exit(1)
        obj = json.loads(args[1])
        codes = extract_codes(obj)
        for c in codes:
            print(c)
        return

    # Single code parse
    code = args[0]
    parsed = parse(code)
    if parsed:
        print(json.dumps(parsed, indent=2))
    else:
        print(f"Invalid PRISM code: {code!r}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    _main()
