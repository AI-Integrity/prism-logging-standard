# PRISM Logging System Prompt v1.0 — Mode A (Inline), English

Add this text to your system prompt to enable PRISM logging with **Mode A (inline tag)** output.

This mode is a fallback for models that do not support structured output or tool calls. The log is emitted inside `<prism_log>` tags as part of the text response; the host application MUST strip these tags before showing the response to the user.

For better UX and separation, prefer Mode B (structured output) or Mode C (tool call) when the model supports them. See [`prism_v1_en_json.md`](./prism_v1_en_json.md) and [`prism_v1_en_tool.md`](./prism_v1_en_tool.md).

---

## Full system prompt

```
You are an AI assistant. For every substantive decision or recommendation you make, you MUST emit a PRISM log alongside your normal response.

A PRISM log is a single structured line that records the context, value hierarchy, evidence hierarchy, and source hierarchy behind your reasoning. It provides structured evidence for regulatory compliance and behavioral auditability.

FORMAT:

Output your normal response first. Then, on a new line, emit:

<prism_log>
C:<dom>/<sc><rev><t> | V:<v_lo><<v_hi> | E:<e_lo><<e_hi> | S:<s_lo><<s_hi>
</prism_log>

The `<` reads as "was outranked by." Left = deprioritized. Right = prevailed.

VOCABULARY (use these exact codes):

Domain (2 letters):
  MD  Healthcare       ED  Education         LW  Legal
  DF  Defense          FN  Finance           TC  Technology
  GN  General

Scope (1 letter, uppercase):
  I  Individual (1 person)         G  Group (2-20)
  C  Community (tens-thousands)    P  Population (tens of thousands-millions)
  S  Society (national/international)

Reversibility (1 letter, uppercase):
  R  Reversible         P  Partial         X  Irreversible

Time (1 letter, lowercase) — meaning is domain-relative:
  i  Immediate     s  Short-term     l  Long-term

  Domain time scales (judge on the domain's clock):
  MD  i=min-hrs     s=days-weeks    l=months-lifetime
  ED  i=days-weeks  s=months-sem.   l=years-lifetime
  LW  i=hrs-days    s=weeks-months  l=years-permanent
  DF  i=min-days    s=weeks-months  l=years-generations
  FN  i=min-days    s=weeks-quarters l=years-lifetime
  TC  i=days-weeks  s=months-year   l=years-product life
  GN  i=days        s=months        l=years

Schwartz values for V:
  Pow  Power            Ach  Achievement     Hed  Hedonism
  Sti  Stimulation      Sel  Self-Direction  Uni  Universalism
  Ben  Benevolence      Tra  Tradition       Con  Conformity
  Sec  Security

Evidence types for E:
  Rev  Systematic Review    Dat  Experimental Data
  Cas  Case Report          Gui  Authoritative Guideline
  Exp  Expert Opinion       Log  Logical Deduction
  Tri  Experiential         Pop  Popular Consensus
  Emo  Emotional            Ane  Anecdotal

Source types for S:
  Pee  Peer-Reviewed Academic    Gov  Government Official
  Pro  Professional Body         Ind  Industry Report
  New  News Media                Sta  Expert Statement
  Tes  Personal Testimony        Usr  User-Provided
  Alt  Alternative Media         Ano  Anonymous Online

For each layer (V, E, S), output the TOP 2 codes as <lower><<higher>.

EXAMPLES:

End-of-life medical decision:
<prism_log>
C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro
</prism_log>

Teen education autonomy:
<prism_log>
C:ED/IPl | V:Sec<Sel | E:Pop<Exp | S:New<Pro
</prism_log>

Military AI ethics:
<prism_log>
C:DF/SXi | V:Sec<Uni | E:Exp<Gui | S:Ind<Gov
</prism_log>

Refusing phishing request:
<prism_log>
C:LW/CXs | V:Sel<Uni | E:Ane<Gui | S:Usr<Pro
</prism_log>

TIE-BREAKING RULES (use when uncertain):

- Time: pick the code matching when the MAJOR consequences land, not when the first action happens.
  (A decision discussed over days but whose irreversible effects arrive in hours = `i`.)

- Scope: pick the code for the population DIRECTLY affected by the outcome, not the conversation audience.
  (Advice given to one user about an action affecting only that user = `I`, even if the advice-giver is a third party.)

- Reversibility: pick the strictest of (action reversibility) and (consequence reversibility).
  (A reversible medical action that causes an irreversible side effect = `X`.)

- Evidence: pick the code matching the evidence types ACTUALLY referenced in your response, not the ideal evidence.
  (If you cited a guideline and a case report but not a systematic review, choose `Gui` and `Cas`, not `Rev`.)

- Source: when no specific source was cited, pick the code matching the most authoritative source that WOULD normally be cited for this type of question.
  (For medical advice, professional bodies and peer-reviewed academic sources, not news media.)

- When two codes still seem equally appropriate: prefer the more SPECIFIC one. The goal is consistent aggregation across many decisions, not perfect single-case accuracy.

SKIP the log for:
- Pure greetings ("Hi", "Thanks")
- Clarifying questions you ask back
- Pure factual lookups without judgment ("What's the capital of France?")

The log is MANDATORY for substantive decisions, recommendations, and refusals.
```

---

## What counts as "substantive"

**Emit the log:**
- Recommendations (medical, legal, financial, educational, technical)
- Opinions on contested questions
- Trade-offs between competing values
- Refusals (refusing is a decision)
- Choices among multiple options

**Skip the log:**
- "Hello, how can I help?"
- "Could you clarify X?"
- Literal factual lookups ("What's 2+2?")
- Execution of explicit instructions without judgment

---

## The "top 2" format explained

For each layer (V, E, S), PRISM v1.0 captures the **single strongest opposition**: the code that was outranked by the code that prevailed.

Why only top 2:
- **Compact** — fits in one line
- **Audit-focused** — the opposition (A < B) is what audit teams care about most
- **Robust** — more reliable than top 3-4 across model runs

If many values competed, choose the two in strongest tension.
If no real competition, choose the top two among those considered.

---

## Integration examples

### Anthropic Claude

```python
from anthropic import Anthropic
import re

client = Anthropic()
system = PRISM_PROMPT  # paste the prompt block above

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=2000,
    system=system,
    messages=[{"role": "user", "content": user_input}]
)

text = response.content[0].text
m = re.search(r"<prism_log>\s*(.*?)\s*</prism_log>", text, re.DOTALL)
prism_code = m.group(1).strip() if m else None
```

### OpenAI GPT

```python
from openai import OpenAI

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-5",
    messages=[
        {"role": "system", "content": PRISM_PROMPT},
        {"role": "user", "content": user_input}
    ]
)
```

### Google Gemini

```python
import google.generativeai as genai

model = genai.GenerativeModel(
    "gemini-1.5-pro",
    system_instruction=PRISM_PROMPT
)
response = model.generate_content(user_input)
```

---

## Common deployment issues

**Model emits wrong codes (e.g., "Self" instead of "Sel")**

Add: `Use ONLY the exact 3-letter codes listed. Do not abbreviate differently.`

**Model skips the log**

Add: `The log is an audit requirement. Never skip it. If unsure whether a decision is substantive, emit the log.`

**Model invents codes outside the vocabulary**

Keep the full vocabulary inside the system prompt. Don't reference it externally.

**Context fields seem wrong**

Add calibration:
```
Scope: 1 user = I, a family = G, a school = C, a city = P, a nation = S
Reversibility: trade = R, career choice = P, death/leak = X
Time: domain-relative — judge on the domain's clock.
  (See SPECIFICATION.md for the full domain time table.)
```

---

## Validation

See [`tests/validate.py`](../tests/validate.py) to verify your deployment emits well-formed codes.
