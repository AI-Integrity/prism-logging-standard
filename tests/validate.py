"""
PRISM Log v1.0 validator.

Checks that a PRISM log code conforms to the v1.0 specification.

Usage:
    python validate.py                           # runs built-in test suite
    python validate.py "C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro"
    python validate.py --file responses.txt      # validates all logs in a file
"""
import re
import sys
from typing import Optional

# ============================================================
# Vocabulary
# ============================================================

DOMAINS = {"MD", "ED", "LW", "DF", "FN", "TC", "GN"}
SCOPES = set("IGCPS")
REVERSIBILITY = set("RPX")
TIME = set("isl")

SCHWARTZ = {"Pow", "Ach", "Hed", "Sti", "Sel", "Uni", "Ben", "Tra", "Con", "Sec"}
EVIDENCE = {"Rev", "Dat", "Cas", "Gui", "Exp", "Log", "Tri", "Pop", "Emo", "Ane"}
SOURCE = {"Pee", "Gov", "Pro", "Ind", "New", "Sta", "Tes", "Usr", "Alt", "Ano"}

# ============================================================
# Regex
# ============================================================

PRISM_LOG_PATTERN = re.compile(
    r"C:(?P<domain>\w{2})/(?P<scope>[A-Z])(?P<rev>[A-Z])(?P<time>[a-z])\s*\|\s*"
    r"V:(?P<v_lo>\w{3})<(?P<v_hi>\w{3})\s*\|\s*"
    r"E:(?P<e_lo>\w{3})<(?P<e_hi>\w{3})\s*\|\s*"
    r"S:(?P<s_lo>\w{3})<(?P<s_hi>\w{3})"
)

TAG_PATTERN = re.compile(r"<prism_log>\s*(.*?)\s*</prism_log>", re.DOTALL)


# ============================================================
# Validation
# ============================================================

def validate(code: str) -> list[str]:
    """Return a list of validation errors. Empty list = valid."""
    errors = []
    code = code.strip()

    m = PRISM_LOG_PATTERN.match(code)
    if not m:
        return [f"Code does not match PRISM v1.0 format: {code!r}"]

    g = m.groupdict()

    if g["domain"] not in DOMAINS:
        errors.append(f"Unknown domain: {g['domain']!r}. Valid: {sorted(DOMAINS)}")
    if g["scope"] not in SCOPES:
        errors.append(f"Unknown scope: {g['scope']!r}. Valid: {sorted(SCOPES)}")
    if g["rev"] not in REVERSIBILITY:
        errors.append(f"Unknown reversibility: {g['rev']!r}. Valid: {sorted(REVERSIBILITY)}")
    if g["time"] not in TIME:
        errors.append(f"Unknown time: {g['time']!r}. Valid: {sorted(TIME)}")

    for field, vocab in [("v_lo", SCHWARTZ), ("v_hi", SCHWARTZ),
                         ("e_lo", EVIDENCE), ("e_hi", EVIDENCE),
                         ("s_lo", SOURCE), ("s_hi", SOURCE)]:
        if g[field] not in vocab:
            errors.append(f"Unknown code for {field}: {g[field]!r}")

    if not errors:
        if g["v_lo"] == g["v_hi"]:
            errors.append(f"V layer: same code on both sides ({g['v_lo']})")
        if g["e_lo"] == g["e_hi"]:
            errors.append(f"E layer: same code on both sides ({g['e_lo']})")
        if g["s_lo"] == g["s_hi"]:
            errors.append(f"S layer: same code on both sides ({g['s_lo']})")

    return errors


def extract_logs(text: str) -> list[str]:
    """Extract PRISM code strings from input text in any of three modes.

    Mode A: inline <prism_log>...</prism_log> tags
    Mode B: JSON with 'prism_log' key containing {'code': '...'} or bare 'prism_log': '...'
    Mode C: tool call JSON with 'input' or 'arguments' containing {'code': '...'}

    Returns list of code strings found. Empty if none.
    """
    import json as _json

    codes = []

    # Mode A: inline tags
    codes.extend(m.group(1).strip() for m in TAG_PATTERN.finditer(text))

    # Mode B / Mode C: scan for JSON objects that contain a PRISM code
    # Try the whole input as one JSON object first
    stripped = text.strip()
    if stripped.startswith("{") or stripped.startswith("["):
        try:
            obj = _json.loads(stripped)
            codes.extend(_walk_for_codes(obj))
        except _json.JSONDecodeError:
            pass

    # Also scan for embedded JSON-like substrings (conservative: only if no Mode A matches)
    # This catches JSON snippets that appear alongside other text.
    if not codes:
        # Find things that look like JSON objects containing "code"
        for match in re.finditer(r'\{[^{}]*"code"\s*:\s*"([^"]+)"[^{}]*\}', text):
            candidate = match.group(1).strip()
            if PRISM_LOG_PATTERN.match(candidate):
                codes.append(candidate)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for c in codes:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    return unique


def _walk_for_codes(obj):
    """Recursively search a JSON-parsed object for PRISM code strings."""
    results = []
    if isinstance(obj, dict):
        # Direct 'code' key with a valid-looking string
        if "code" in obj and isinstance(obj["code"], str):
            if PRISM_LOG_PATTERN.match(obj["code"].strip()):
                results.append(obj["code"].strip())
        # 'prism_log' as a string (legacy/flat form)
        if "prism_log" in obj and isinstance(obj["prism_log"], str):
            if PRISM_LOG_PATTERN.match(obj["prism_log"].strip()):
                results.append(obj["prism_log"].strip())
        # Recurse into all values
        for v in obj.values():
            results.extend(_walk_for_codes(v))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(_walk_for_codes(item))
    return results


def parse(code: str) -> Optional[dict]:
    """Parse a PRISM log code into a dict. Returns None if invalid."""
    m = PRISM_LOG_PATTERN.match(code.strip())
    return m.groupdict() if m else None


# ============================================================
# Built-in tests
# ============================================================

VALID_SAMPLES = [
    "C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro",
    "C:ED/IPl | V:Sec<Sel | E:Pop<Exp | S:New<Pro",
    "C:DF/SXi | V:Sec<Uni | E:Exp<Gui | S:Ind<Gov",
    "C:FN/IRs | V:Ach<Sec | E:Pop<Gui | S:Alt<Pro",
    "C:LW/CXs | V:Sel<Uni | E:Ane<Gui | S:Usr<Pro",
    "C:TC/GRl | V:Sti<Sec | E:Ane<Cas | S:Alt<Pro",
]

INVALID_SAMPLES = [
    ("C:ZZ/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro", "domain"),
    ("C:MD/QXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro", "scope"),
    ("C:MD/IZi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro", "reversibility"),
    ("C:MD/IXz | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro", "time"),
    ("C:MD/IXi | V:Xxx<Sel | E:Exp<Gui | S:Usr<Pro", "v_lo"),
    ("C:MD/IXi | V:Ben<Sel | E:Xxx<Gui | S:Usr<Pro", "e_lo"),
    ("C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Xxx<Pro", "s_lo"),
    ("C:MD/IXi | V:Ben<Ben | E:Exp<Gui | S:Usr<Pro", "same code"),
    ("malformed string", "match"),
]


def run_tests():
    print("Running PRISM log validator self-test...\n")

    print(f"Valid samples ({len(VALID_SAMPLES)}):")
    v_passed = 0
    for code in VALID_SAMPLES:
        errors = validate(code)
        status = "✅" if not errors else "❌"
        print(f"  {status} {code}")
        if errors:
            for e in errors:
                print(f"     - {e}")
        else:
            v_passed += 1

    print(f"\nInvalid samples ({len(INVALID_SAMPLES)}):")
    i_passed = 0
    for code, expected_keyword in INVALID_SAMPLES:
        errors = validate(code)
        caught = bool(errors) and any(expected_keyword.lower() in e.lower() for e in errors)
        status = "✅" if caught else "❌"
        print(f"  {status} [expects '{expected_keyword}'] {code[:55]}...")
        if errors:
            for e in errors[:1]:
                print(f"     - {e}")
        if caught:
            i_passed += 1

    # Multi-mode extraction test
    print(f"\nMulti-mode extraction tests:")
    mode_a = '<prism_log>\nC:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro\n</prism_log>'
    mode_b = '{"response": "text", "prism_log": {"code": "C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro"}}'
    mode_c = '{"tool_call": {"name": "record_prism_log", "input": {"code": "C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro"}}}'
    expected = "C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro"
    m_passed = 0
    for mode_name, raw in [("Mode A (inline)", mode_a), ("Mode B (JSON)", mode_b), ("Mode C (tool)", mode_c)]:
        extracted = extract_logs(raw)
        ok = len(extracted) == 1 and extracted[0] == expected
        status = "✅" if ok else "❌"
        print(f"  {status} {mode_name}: extracted {extracted}")
        if ok:
            m_passed += 1

    print(f"\nResult: {v_passed}/{len(VALID_SAMPLES)} valid samples accepted, "
          f"{i_passed}/{len(INVALID_SAMPLES)} invalid samples caught, "
          f"{m_passed}/3 modes extracted correctly")

    if v_passed != len(VALID_SAMPLES) or i_passed != len(INVALID_SAMPLES) or m_passed != 3:
        sys.exit(1)


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        run_tests()
        sys.exit(0)

    if args[0] == "--file":
        if len(args) < 2:
            print("Usage: validate.py --file <path>")
            sys.exit(1)
        with open(args[1]) as f:
            text = f.read()
        logs = extract_logs(text)
        print(f"Found {len(logs)} PRISM logs in {args[1]}")
        total_errors = 0
        for i, log in enumerate(logs, 1):
            errors = validate(log)
            if errors:
                total_errors += 1
                print(f"\n[{i}] ❌ {log}")
                for e in errors:
                    print(f"     {e}")
            else:
                print(f"[{i}] ✅ {log}")
        print(f"\nSummary: {len(logs) - total_errors}/{len(logs)} logs valid")
        sys.exit(1 if total_errors else 0)

    # Single code on CLI
    code = args[0]
    errors = validate(code)
    if not errors:
        parsed = parse(code)
        print("✅ Valid PRISM log v1.0")
        print()
        for k, v in parsed.items():
            print(f"  {k}: {v}")
    else:
        print("❌ Invalid PRISM log")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
