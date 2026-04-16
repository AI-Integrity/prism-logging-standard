# PRISM Logging System Prompt v1.0 — Mode C (Tool Call), English

Use this mode when the model supports native tool use / function calling (Anthropic Claude tool use, OpenAI function calling, Gemini function calling).

In this mode, the model calls a dedicated `record_prism_log` tool for every substantive decision. The tool call is a separate block in the API response and is never shown to users. The text response remains clean.

This is the **cleanest separation** of three modes and is the recommended approach for Anthropic Claude and agentic systems.

---

## Tool definition

The host application registers this tool with the model:

```json
{
  "name": "record_prism_log",
  "description": "Record the PRISM log for a substantive decision. Call this exactly once per response when the response contains a substantive decision, recommendation, or refusal. Do not call for pure greetings, clarifying questions, or trivial factual lookups.",
  "input_schema": {
    "type": "object",
    "required": ["code"],
    "additionalProperties": false,
    "properties": {
      "code": {
        "type": "string",
        "description": "The full PRISM code in the exact format: 'C:<dom>/<sc><rev><t> | V:<v_lo><<v_hi> | E:<e_lo><<e_hi> | S:<s_lo><<s_hi>'",
        "pattern": "^C:[A-Z]{2}/[IGCPS][RPX][isl] \\| V:[A-Z][a-z]{2}<[A-Z][a-z]{2} \\| E:[A-Z][a-z]{2}<[A-Z][a-z]{2} \\| S:[A-Z][a-z]{2}<[A-Z][a-z]{2}$"
      }
    }
  }
}
```

---

## System prompt

```
You are an AI assistant. For every substantive decision or recommendation in your response, you MUST call the `record_prism_log` tool exactly once before completing the response.

The tool records the PRISM log — a structured code summarizing the context, value hierarchy, evidence hierarchy, and source hierarchy behind your reasoning. The log is for audit and is never shown to users.

Do NOT mention the tool call in your user-facing text. Do NOT include PRISM codes in your text response. The log exists solely as tool call arguments.

Call `record_prism_log` only for substantive responses (recommendations, opinions on contested questions, value trade-offs, refusals, choices among options). Do NOT call for pure greetings, clarifying questions, or trivial factual lookups.

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

EXAMPLES of when to call the tool (followed by a normal text response):

- Medical decision advice → call with code like "C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro"
- Investment advice → call with code like "C:FN/IRs | V:Sti<Sec | E:Pop<Gui | S:Alt<Pro"
- Refusing a harmful request → call with code like "C:LW/IXs | V:Sel<Uni | E:Emo<Gui | S:Usr<Gov"

EXAMPLES of when NOT to call:
- "Hi" → no tool call, just respond
- "Thanks!" → no tool call
- "What's the capital of France?" → no tool call
- "Can you clarify what you mean?" → no tool call

TIE-BREAKING RULES (use when uncertain):
- Time: pick when MAJOR consequences land, not when first action happens
- Scope: pick the population DIRECTLY affected, not the conversation audience
- Reversibility: pick the stricter of (action reversibility) and (consequence reversibility)
- Evidence: pick codes matching evidence ACTUALLY referenced in your response
- Source: when no source was cited, pick the most authoritative source that WOULD be cited
- Final tiebreaker: prefer the more SPECIFIC code
```

---

## Anthropic Claude integration

```python
from anthropic import Anthropic

client = Anthropic()

PRISM_TOOL = {
    "name": "record_prism_log",
    "description": "Record the PRISM log for a substantive decision...",
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

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=2000,
    system=PRISM_MODE_C_PROMPT,
    tools=[PRISM_TOOL],
    messages=[{"role": "user", "content": user_input}]
)

# Extract tool call and text response
user_facing = ""
prism_code = None
for block in response.content:
    if block.type == "text":
        user_facing += block.text
    elif block.type == "tool_use" and block.name == "record_prism_log":
        prism_code = block.input["code"]

# Return a trivial tool result so the model can continue
if prism_code:
    continuation = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        system=PRISM_MODE_C_PROMPT,
        tools=[PRISM_TOOL],
        messages=[
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": response.content},
            {"role": "user", "content": [{
                "type": "tool_result",
                "tool_use_id": <tool_use_id>,
                "content": "ok"
            }]}
        ]
    )
    # Append text from continuation if needed
```

---

## OpenAI integration

```python
from openai import OpenAI
import json

client = OpenAI()

PRISM_TOOL = {
    "type": "function",
    "function": {
        "name": "record_prism_log",
        "description": "Record the PRISM log for a substantive decision...",
        "parameters": {
            "type": "object",
            "required": ["code"],
            "properties": {
                "code": {"type": "string"}
            }
        }
    }
}

response = client.chat.completions.create(
    model="gpt-5",
    messages=[
        {"role": "system", "content": PRISM_MODE_C_PROMPT},
        {"role": "user", "content": user_input}
    ],
    tools=[PRISM_TOOL],
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

## Google Gemini integration

```python
import google.generativeai as genai

prism_tool = {
    "function_declarations": [{
        "name": "record_prism_log",
        "description": "Record the PRISM log for a substantive decision...",
        "parameters": {
            "type": "object",
            "required": ["code"],
            "properties": {
                "code": {"type": "string"}
            }
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

## Critical UX rule

**The tool call MUST NEVER be rendered in the user-facing UI.** The host application must:

1. Extract text blocks → show to user
2. Extract tool calls → route to audit storage
3. Keep the two pipelines separate

This is cleaner than Mode B because the separation is enforced by the API itself.

---

## Agentic systems note

In agentic systems that already use multiple tools, `record_prism_log` becomes one of many tools. Best practice:

- Call `record_prism_log` **before** other tools in a given turn — the PRISM log captures the reasoning that led to the other tool calls
- For multi-step agent loops, record a PRISM log **per decision point**, not just at the final output

---

## Validation

See [`tests/validate.py`](../tests/validate.py) — it accepts PRISM codes from any mode and verifies the code string.
