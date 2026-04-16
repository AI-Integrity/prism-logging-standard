# Integration Guide

How to deploy PRISM logging across major AI model providers using all three output modes.

---

## Overview

PRISM v1.0 supports three output modes:

- **Mode A (inline tag)** — fallback for models without structured output
- **Mode B (structured output)** — JSON object with separated `response` and `prism_log` fields
- **Mode C (tool call)** — dedicated `record_prism_log` tool invoked per decision

All three modes carry the same canonical `code` string. Storage, aggregation, and audit tooling work identically once the code is extracted.

**On UX:** In all modes, the PRISM log is for audit storage only and must never be shown to end users. Mode A requires the host application to strip the `<prism_log>` tag before rendering. Modes B and C provide the separation natively through the API.

**On compatibility:** PRISM v1.0 is designed to work with any modern LLM that follows structured output instructions or supports tool use. Deployments should verify with `tests/validate.py` before treating logs as audit-grade evidence.

---

## Provider recommendations

| Provider | Recommended mode | Rationale |
|---|---|---|
| Anthropic Claude | Mode C | Mature tool use; clean separation |
| OpenAI GPT (recent) | Mode B | Structured Outputs is stable |
| OpenAI GPT (legacy) | Mode C | Function calling for older models |
| Google Gemini | Mode B or C | Both supported; Mode B simpler |
| Self-hosted / Llama | Mode A + grammar | Constrained decoding enforces format |

---

## Anthropic Claude (Mode C — recommended)

```python
from anthropic import Anthropic

client = Anthropic()

PRISM_TOOL = {
    "name": "record_prism_log",
    "description": "Record the PRISM log for a substantive decision. Call exactly once per response when the response contains a substantive decision, recommendation, or refusal.",
    "input_schema": {
        "type": "object",
        "required": ["code"],
        "properties": {
            "code": {
                "type": "string",
                "pattern": "^C:[A-Z]{2}/[IGCPS][RPX][isl] \\| V:[A-Z][a-z]{2}<[A-Z][a-z]{2} \\| E:[A-Z][a-z]{2}<[A-Z][a-z]{2} \\| S:[A-Z][a-z]{2}<[A-Z][a-z]{2}$"
            }
        }
    }
}

# Load PRISM_MODE_C_PROMPT from system_prompts/prism_v1_en_tool.md
response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=2000,
    system=PRISM_MODE_C_PROMPT,
    tools=[PRISM_TOOL],
    messages=[{"role": "user", "content": user_input}]
)

user_facing = ""
prism_code = None
for block in response.content:
    if block.type == "text":
        user_facing += block.text
    elif block.type == "tool_use" and block.name == "record_prism_log":
        prism_code = block.input["code"]
```

**Compatible with:** Claude Sonnet 4 and later, Claude Opus 4 and later.

---

## OpenAI GPT — Mode B (Structured Outputs)

```python
from openai import OpenAI
import json

client = OpenAI()

PRISM_SCHEMA = {
    "type": "object",
    "required": ["response"],
    "additionalProperties": False,
    "properties": {
        "response": {"type": "string"},
        "prism_log": {
            "type": ["object", "null"],
            "required": ["code"],
            "additionalProperties": False,
            "properties": {
                "code": {
                    "type": "string",
                    "pattern": "^C:[A-Z]{2}/[IGCPS][RPX][isl] \\| V:[A-Z][a-z]{2}<[A-Z][a-z]{2} \\| E:[A-Z][a-z]{2}<[A-Z][a-z]{2} \\| S:[A-Z][a-z]{2}<[A-Z][a-z]{2}$"
                }
            }
        }
    }
}

response = client.chat.completions.create(
    model="gpt-5",
    messages=[
        {"role": "system", "content": PRISM_MODE_B_PROMPT},
        {"role": "user", "content": user_input}
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "prism_response",
            "schema": PRISM_SCHEMA,
            "strict": True
        }
    }
)

parsed = json.loads(response.choices[0].message.content)
user_facing = parsed["response"]
prism_code = parsed.get("prism_log", {}).get("code") if parsed.get("prism_log") else None
```

**Compatible with:** Recent GPT-4 and GPT-5 family models that support Structured Outputs.

---

## OpenAI GPT — Mode C (Function Calling) for legacy models

```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": PRISM_MODE_C_PROMPT},
        {"role": "user", "content": user_input}
    ],
    tools=[{
        "type": "function",
        "function": {
            "name": "record_prism_log",
            "description": "Record PRISM log for a substantive decision",
            "parameters": {
                "type": "object",
                "required": ["code"],
                "properties": {"code": {"type": "string"}}
            }
        }
    }],
    tool_choice="auto"
)

msg = response.choices[0].message
user_facing = msg.content or ""
prism_code = None
if msg.tool_calls:
    for call in msg.tool_calls:
        if call.function.name == "record_prism_log":
            args = json.loads(call.function.arguments)
            prism_code = args.get("code")
```

---

## Google Gemini — Mode B

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

**Compatible with:** Gemini 1.5 Pro and later, Gemini 2.x.

---

## Google Gemini — Mode C (Function Calling)

```python
prism_tool = {
    "function_declarations": [{
        "name": "record_prism_log",
        "description": "Record the PRISM log for a substantive decision.",
        "parameters": {
            "type": "object",
            "required": ["code"],
            "properties": {"code": {"type": "string"}}
        }
    }]
}

model = genai.GenerativeModel(
    "gemini-2.0-flash",
    system_instruction=PRISM_MODE_C_PROMPT,
    tools=[prism_tool]
)

response = model.generate_content(user_input)

user_facing = ""
prism_code = None
for part in response.candidates[0].content.parts:
    if hasattr(part, "text") and part.text:
        user_facing += part.text
    if hasattr(part, "function_call") and part.function_call.name == "record_prism_log":
        prism_code = dict(part.function_call.args).get("code")
```

---

## Llama / Self-hosted (Mode A fallback)

```python
import ollama
import re

response = ollama.chat(
    model="llama3.1:70b",
    messages=[
        {"role": "system", "content": PRISM_MODE_A_PROMPT},
        {"role": "user", "content": user_input}
    ]
)

text = response["message"]["content"]

# Extract and strip the log before showing to user
log_match = re.search(r"<prism_log>\s*(.*?)\s*</prism_log>", text, re.DOTALL)
prism_code = log_match.group(1).strip() if log_match else None

# CRITICAL: remove the tag from user-facing text
user_facing = re.sub(r"<prism_log>.*?</prism_log>", "", text, flags=re.DOTALL).strip()
```

**Compatible with:** Llama 3.1 70B and larger. Smaller models (8B, 13B) may hallucinate vocabulary codes; use 70B+ for production, or constrained generation (e.g., llama.cpp grammar) to force valid code structure.

---

## Multi-turn conversations

PRISM logs are per-turn, not per-conversation. Store logs indexed by turn:

```python
conversation_logs = []
for turn in conversation:
    user_facing, prism_code = call_ai(turn.user_message)  # mode-specific
    if prism_code:
        conversation_logs.append({
            "turn_id": turn.id,
            "timestamp": datetime.utcnow().isoformat(),
            "prism_code": prism_code,
            "model_id": "claude-sonnet-4-5",
            "session_id": session.id,
        })
```

Multi-turn analysis reveals **value drift**: does the AI's priority hierarchy shift across turns as context evolves?

---

## Agentic systems

For AI agents that make multiple decisions per user input, emit a PRISM log **per decision point**. Mode C (tool call) is especially well-suited here — the PRISM tool sits alongside other agent tools.

Example sequence:
```
User: "Book me a flight to Tokyo next week"

Decision 1: Dates?          → record_prism_log tool call 1
Decision 2: Direct/layover? → record_prism_log tool call 2
Decision 3: Class?          → record_prism_log tool call 3
Decision 4: Book?           → record_prism_log tool call 4
```

Best practice: call `record_prism_log` **before** other tools in a given turn — the log captures the reasoning that led to the other tool calls.

---

## Storage recommendations

### Short-term (active sessions)

In-memory cache or Redis.

### Long-term (audit compliance)

Append-only log store (S3, GCS, Azure Blob).

**Retention:**
- Align with applicable regulations in your jurisdiction (EU AI Act currently indicates multi-year retention for high-risk systems; other regimes vary)
- When no specific regulation applies, 3–5 years is a common baseline for audit evidence

**Ensure:** immutability, chain-of-custody, cryptographic integrity for legal defensibility.

### Indexable fields

| Field | Index type | Use case |
|---|---|---|
| `prism_code` (full) | Unique | Primary lookup |
| Domain (first 2 chars after `C:`) | B-tree | Aggregation by domain |
| Value hierarchy (V: portion) | B-tree | Value drift analysis |
| Timestamp | B-tree | Time-series queries |
| Model ID | B-tree | Per-model comparisons |

---

## SQL-based auditing

Once PRISM codes are stored, auditing is direct SQL:

```sql
-- Q1: How often does Security outrank Universalism in healthcare?
SELECT COUNT(*) AS count
FROM logs
WHERE prism_code LIKE 'C:MD/%'
  AND prism_code LIKE '%V:Uni<Sec%';

-- Q2: Distribution of value hierarchies by domain
SELECT SUBSTRING(prism_code FROM 'C:(\w{2})/') AS domain,
       SUBSTRING(prism_code FROM 'V:(\w{3}<\w{3})') AS v_pattern,
       COUNT(*) AS n
FROM logs
GROUP BY domain, v_pattern
ORDER BY domain, n DESC;

-- Q3: Reversibility distribution in defense domain
SELECT SUBSTRING(prism_code FROM 'C:DF/\w(\w)') AS reversibility,
       COUNT(*) AS n
FROM logs
WHERE prism_code LIKE 'C:DF/%'
GROUP BY reversibility;

-- Q4: Value drift between model versions
SELECT model_id,
       COUNT(*) FILTER (WHERE prism_code LIKE '%V:Uni<Sec%') * 1.0 / COUNT(*) AS sec_over_uni_rate
FROM logs
WHERE prism_code LIKE 'C:MD/%'
GROUP BY model_id;
```

---

## Common deployment issues

**Model emits wrong codes (e.g., "Self" instead of "Sel")**

Add to prompt:
```
Use ONLY the exact 3-letter codes. Do not abbreviate differently.
Do not use synonyms. Do not use full words.
```

**Model skips the log (Modes A/B) or tool call (Mode C)**

Add:
```
CRITICAL: The PRISM log is an audit requirement for this deployment.
Never skip it for substantive decisions.
If you're unsure, emit the log.
```

**Model invents codes outside the vocabulary**

Keep the full vocabulary inside the system prompt (already included in all prompt files).
Do not reference it externally — the model must see the list every turn.

**Mode A: tag appears in user-facing response**

This is a host-application bug. Ensure `re.sub(r"<prism_log>.*?</prism_log>", "", text)` runs before rendering. Consider moving to Mode B or C to eliminate the issue.

**Mode B: response field contains JSON fragments**

When the model's normal response would contain JSON-like syntax (code examples, config files), instruct it to use code fences inside the `response` string. The `response` is just a string — JSON-in-JSON is fine.

**Mode C: model calls the tool but text response is empty**

This is expected for some providers after a tool call. Send a trivial tool result (e.g., `"ok"`) back to the model so it can continue generating the user-facing text.

---

## Performance overhead

| Aspect | Mode A | Mode B | Mode C |
|---|---|---|---|
| Input tokens | +400-600 | +450-650 | +500-700 |
| Output tokens (per log) | ~25 | ~35 | ~30 |
| Latency increase | +5-10% | +5-10% | +10-15% (extra round-trip) |
| Cost increase | +10-15% | +12-18% | +15-20% |

Mode C has slightly higher latency because the tool call creates an extra API round-trip. For high-volume deployments, consider prompt caching (supported by all major providers).

---

## Audit artifact generation

Stored PRISM codes can generate several kinds of audit artifacts automatically. The examples below are common patterns, not claims about any specific law.

**Automatic per-decision record (e.g., what regimes like EU AI Act Art. 12 expect):**
Each PRISM code is a timestamped, structured record of a decision's reasoning context. Stored alongside the conversation and output, it can support "automatic logging" requirements without additional transformation.

**Periodic transparency reports:**
Aggregate V, E, S distributions into reports on how the deployment has been reasoning over time:
```sql
SELECT DATE_TRUNC('quarter', timestamp) AS quarter,
       SUBSTRING(prism_code FROM 'V:\w{3}<(\w{3})') AS dominant_value,
       COUNT(*) AS n
FROM logs
GROUP BY quarter, dominant_value
ORDER BY quarter, n DESC;
```

**Pre-deployment assessment:**
Run representative synthetic scenarios through a candidate deployment. The distribution of `C:` fields gives a behavioral profile that can be attached to an impact assessment before production rollout.

**Ongoing drift monitoring:**
Set alerts when V hierarchy patterns shift unexpectedly across model or prompt updates.

**Incident review:**
When a specific output is investigated, its PRISM code lets reviewers locate the reasoning fingerprint quickly — which values prevailed, what evidence type the model weighted, what source class it trusted — without re-running the conversation.

---

## Questions?

- GitHub issues: technical questions, bug reports, suggestions
- Email: 2sk@aioq.org — commercial inquiries, compliance consulting
