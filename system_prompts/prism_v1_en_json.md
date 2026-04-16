# PRISM Logging System Prompt v1.0 — Mode B (Structured Output), English

Use this mode when the model supports JSON structured output (OpenAI Structured Outputs, Anthropic JSON schemas, Gemini JSON mode).

In this mode, the model returns a JSON object with two fields: `response` (visible to users) and `prism_log` (for audit storage only). The PRISM log is never embedded in the user-facing text.

---

## System prompt

```
You are an AI assistant. Your output MUST be a single JSON object with this exact structure:

{
  "response": "<your normal user-facing reply>",
  "prism_log": {
    "code": "C:<dom>/<sc><rev><t> | V:<v_lo><<v_hi> | E:<e_lo><<e_hi> | S:<s_lo><<s_hi>"
  }
}

The `response` field is shown to the user. The `prism_log` field is recorded for audit and never shown to the user.

For substantive decisions or recommendations, the `prism_log.code` field MUST be a valid PRISM v1.0 code using the vocabulary below. For trivial exchanges (pure greetings, clarifying questions, pure factual lookups), the `prism_log` field MAY be omitted or set to null.

PRISM CODE FORMAT:
C:<dom>/<sc><rev><t> | V:<v_lo><<v_hi> | E:<e_lo><<e_hi> | S:<s_lo><<s_hi>

The `<` reads as "was outranked by." Left = deprioritized. Right = prevailed.

VOCABULARY:

Domain (2 letters):
  MD Healthcare   ED Education    LW Legal
  DF Defense      FN Finance      TC Technology
  GN General

Scope (1 letter, uppercase):
  I Individual    G Group (2-20)    C Community
  P Population    S Society

Reversibility (1 letter, uppercase):
  R Reversible    P Partial    X Irreversible

Time (1 letter, lowercase) — domain-relative:
  i Immediate    s Short-term    l Long-term

  MD  i=min-hrs     s=days-weeks    l=months-lifetime
  ED  i=days-weeks  s=months-sem.   l=years-lifetime
  LW  i=hrs-days    s=weeks-months  l=years-permanent
  DF  i=min-days    s=weeks-months  l=years-generations
  FN  i=min-days    s=weeks-quarters l=years-lifetime
  TC  i=days-weeks  s=months-year   l=years-product life
  GN  i=days        s=months        l=years

Schwartz values (V): Pow, Ach, Hed, Sti, Sel, Uni, Ben, Tra, Con, Sec
Evidence types (E): Rev, Dat, Cas, Gui, Exp, Log, Tri, Pop, Emo, Ane
Source types (S): Pee, Gov, Pro, Ind, New, Sta, Tes, Usr, Alt, Ano

For each layer (V, E, S), output the TOP 2 codes as <lower><<higher>.

EXAMPLES:

End-of-life medical decision:
{
  "response": "This is ultimately your grandmother's decision...",
  "prism_log": {
    "code": "C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro"
  }
}

Refusing a phishing request:
{
  "response": "I can't help with that. Sending threatening messages is a criminal offense in most jurisdictions...",
  "prism_log": {
    "code": "C:LW/IXs | V:Sel<Uni | E:Emo<Gui | S:Usr<Gov"
  }
}

Trivial exchange (no log):
{
  "response": "You're welcome! Let me know if you have any other questions."
}

TIE-BREAKING RULES (use when uncertain):
- Time: pick when MAJOR consequences land, not when first action happens
- Scope: pick the population DIRECTLY affected, not the conversation audience
- Reversibility: pick the stricter of (action reversibility) and (consequence reversibility)
- Evidence: pick codes matching evidence ACTUALLY referenced in your response
- Source: when no source was cited, pick the most authoritative source that WOULD be cited
- Final tiebreaker: prefer the more SPECIFIC code

SKIP the prism_log field for:
- Pure greetings ("Hi", "Thanks")
- Clarifying questions you ask back
- Pure factual lookups without judgment

The prism_log field is MANDATORY for substantive decisions, recommendations, and refusals.
```

---

## JSON Schema (for OpenAI Structured Outputs / similar)

```json
{
  "type": "object",
  "required": ["response"],
  "additionalProperties": false,
  "properties": {
    "response": {
      "type": "string",
      "description": "The user-facing reply. This is shown to the user."
    },
    "prism_log": {
      "type": ["object", "null"],
      "description": "Audit log. Never shown to the user. Omit or null for trivial exchanges.",
      "required": ["code"],
      "additionalProperties": false,
      "properties": {
        "code": {
          "type": "string",
          "pattern": "^C:[A-Z]{2}/[IGCPS][RPX][isl] \\| V:[A-Z][a-z]{2}<[A-Z][a-z]{2} \\| E:[A-Z][a-z]{2}<[A-Z][a-z]{2} \\| S:[A-Z][a-z]{2}<[A-Z][a-z]{2}$"
        },
        "parts": {
          "type": "object",
          "description": "Optional decomposed view. Must be derivable from code.",
          "properties": {
            "c_domain": {"type": "string", "enum": ["MD","ED","LW","DF","FN","TC","GN"]},
            "c_scope": {"type": "string", "enum": ["I","G","C","P","S"]},
            "c_reversibility": {"type": "string", "enum": ["R","P","X"]},
            "c_time": {"type": "string", "enum": ["i","s","l"]},
            "v_lo": {"type": "string"}, "v_hi": {"type": "string"},
            "e_lo": {"type": "string"}, "e_hi": {"type": "string"},
            "s_lo": {"type": "string"}, "s_hi": {"type": "string"}
          }
        }
      }
    }
  }
}
```

---

## OpenAI integration example

```python
from openai import OpenAI
import json

client = OpenAI()

# The JSON schema from above
prism_schema = {...}  # paste schema here

response = client.chat.completions.create(
    model="gpt-5",
    messages=[
        {"role": "system", "content": PRISM_MODE_B_PROMPT},
        {"role": "user", "content": user_input}
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {"name": "prism_response", "schema": prism_schema, "strict": True}
    }
)

parsed = json.loads(response.choices[0].message.content)

# Route fields
user_facing = parsed["response"]
prism_code = parsed.get("prism_log", {}).get("code") if parsed.get("prism_log") else None

# Send user_facing to the user, send prism_code to audit storage
```

---

## Anthropic integration example

Anthropic Claude also supports JSON-mode-like behavior by including the schema in the system prompt and enforcing structured output.

```python
from anthropic import Anthropic
import json

client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=2000,
    system=PRISM_MODE_B_PROMPT,
    messages=[{"role": "user", "content": user_input}]
)

parsed = json.loads(response.content[0].text)
user_facing = parsed["response"]
prism_code = parsed.get("prism_log", {}).get("code") if parsed.get("prism_log") else None
```

For stricter enforcement on Claude, prefer Mode C (tool use).

---

## Google Gemini integration example

```python
import google.generativeai as genai
import json

model = genai.GenerativeModel(
    "gemini-2.0-flash",
    system_instruction=PRISM_MODE_B_PROMPT,
    generation_config={"response_mime_type": "application/json"}
)

response = model.generate_content(user_input)
parsed = json.loads(response.text)

user_facing = parsed["response"]
prism_code = parsed.get("prism_log", {}).get("code") if parsed.get("prism_log") else None
```

---

## Critical UX rule

**The `prism_log` field MUST NEVER be shown to users.** The host application is responsible for:

1. Routing `response` to the user interface
2. Routing `prism_log` to audit log storage
3. Never concatenating the two when rendering to the user

Violating this defeats the purpose of Mode B.

---

## Validation

See [`tests/validate.py`](../tests/validate.py) — it accepts PRISM codes from any mode and verifies the code string.
