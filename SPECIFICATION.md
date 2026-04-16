# PRISM Log Code Specification v1.0

The PRISM log is a single line of structured code that captures the reasoning fingerprint of an AI decision. It is designed to be:

- **Compact** — one line, ~60 characters, machine-parseable
- **Complete** — captures context, values, evidence, and sources
- **Privacy-preserving** — contains no user content or decision details
- **Auditable** — structure supports aggregation, comparison, and anomaly detection

---

## Format

```
C:<context> | V:<value-hierarchy> | E:<evidence-hierarchy> | S:<source-hierarchy>
```

Example:
```
C:MD/IXi | V:Sel<Ben | E:Gui<Rev | S:Pro<Pee
```

The log is wrapped in `<prism_log>...</prism_log>` tags in model output:
```
<prism_log>
C:MD/IXi | V:Sel<Ben | E:Gui<Rev | S:Pro<Pee
</prism_log>
```

---

## Structure

### C: Context code

Format: `[Domain]/[Scope][Reversibility][TimeHorizon]`

Example: `MD/IXi` = Healthcare / Individual scope / Irreversible / Immediate

### V/E/S: Hierarchy codes

Format: `<lower-priority>,<higher-priority>` (`<` reads as "is outranked by")

Example: `Sel<Ben` = Self-Direction was outranked by Benevolence

**Top 2 only.** PRISM v1.0 captures only the strongest opposition (rank 9 vs rank 10 on a 10-point hierarchy). Top 3 and deeper hierarchies are deferred to future versions.

---

## Context code vocabulary

### Domain (2 letters)

| Code | Domain |
|---|---|
| `MD` | Healthcare (Medical) |
| `ED` | Education |
| `LW` | Legal / Law |
| `DF` | Defense / Security |
| `FN` | Finance |
| `TC` | Technology |
| `GN` | General |

### Scope (1 letter)

The scale of the population affected by the decision.

| Code | Scope | Examples |
|---|---|---|
| `I` | Individual | The user themselves, a single patient, one student |
| `G` | Group | A family, a team, a classroom (2–20 people) |
| `C` | Community | A school, a company, a neighborhood (tens to thousands) |
| `P` | Population | A city, a region, a demographic (tens of thousands to millions) |
| `S` | Society | National or international scale |

### Reversibility (1 letter)

Whether the consequences of the decision can be undone.

| Code | Reversibility | Examples |
|---|---|---|
| `R` | Reversible | Financial trade, policy choice, routine medical treatment |
| `P` | Partial | Academic path, career change, chronic illness management |
| `X` | Irreversible | Death, permanent injury, data leak, legal precedent |

### Time Horizon (1 letter, lowercase)

How quickly the consequences manifest. Time meaning is **domain-relative** — the same calendar duration carries different meaning in healthcare versus technology. The codes `i` / `s` / `l` always mean "immediate / short / long" *within the context of the domain*.

**Domain-specific time scales:**

| Domain | `i` Immediate | `s` Short-term | `l` Long-term |
|---|---|---|---|
| `MD` Healthcare | minutes–hours | days–weeks | months–lifetime |
| `ED` Education | days–weeks | months–semester | years–lifetime |
| `LW` Legal | hours–days | weeks–months | years–permanent |
| `DF` Defense | minutes–days | weeks–months | years–generations |
| `FN` Finance | minutes–days | weeks–quarters | years–lifetime savings |
| `TC` Technology | days–weeks | months–year | years–product lifetime |
| `GN` General | days | months | years |

**How to use the table:**
- The AI judges where the decision's consequences fall **on that domain's clock**
- An ED decision with effects in 2 weeks = `i` (immediate for education)
- An MD decision with effects in 2 weeks = `s` (short-term for healthcare)
- Cross-domain aggregation stays meaningful: `i` in any domain signals "immediate for that context"

### Context code examples

| Code | Meaning |
|---|---|
| `MD/IXi` | Healthcare, 1 person, irreversible, immediate (e.g., end-of-life decision) |
| `ED/IPl` | Education, 1 person, partial reversibility, long-term (e.g., career choice) |
| `DF/SXi` | Defense, societal, irreversible, immediate (e.g., military targeting) |
| `FN/IRs` | Finance, 1 person, reversible, short-term (e.g., investment) |
| `LW/CXs` | Legal, community, irreversible, short-term (e.g., mass fraud) |
| `TC/GRl` | Technology, team, reversible, long-term (e.g., stack choice) |

---

## V — Value hierarchy vocabulary

Based on Schwartz's 10 basic values. 3-letter abbreviations.

| Code | Value | Definition |
|---|---|---|
| `Pow` | Power | Authority, dominance, control over resources |
| `Ach` | Achievement | Personal success through competence |
| `Hed` | Hedonism | Pleasure, sensuous gratification |
| `Sti` | Stimulation | Excitement, novelty, challenge |
| `Sel` | Self-Direction | Independent thought, choice, creativity |
| `Uni` | Universalism | Welfare of all people and nature |
| `Ben` | Benevolence | Care for close others |
| `Tra` | Tradition | Respect for cultural/religious custom |
| `Con` | Conformity | Compliance with social expectations |
| `Sec` | Security | Safety, stability, order |

**Format:** `V:A<B` where A is the value that was outranked, B is the value that prevailed.

**Examples:**
- `V:Sec<Uni` — Security was outranked by Universalism (concern for safety/stability gave way to concern for the welfare of all)
- `V:Sel<Ben` — Self-Direction was outranked by Benevolence (autonomy gave way to care for close others)
- `V:Hed<Sec` — Hedonism was outranked by Security (pleasure gave way to safety/stability)

---

## E — Evidence hierarchy vocabulary

Evidence types that support a reasoning pattern. Loosely ordered by epistemic rigor (top = more rigorous).

| Code | Evidence Type |
|---|---|
| `Rev` | Systematic Review / Meta-analysis |
| `Dat` | Experimental Data |
| `Cas` | Case Report / Observational study |
| `Gui` | Authoritative Guideline |
| `Exp` | Expert Opinion |
| `Log` | Logical Deduction |
| `Tri` | Experiential (first-person trial) |
| `Pop` | Popular Consensus |
| `Emo` | Emotional Appeal |
| `Ane` | Anecdotal |

**Format:** `E:A<B`

**Examples:**
- `E:Pop<Rev` — Popular consensus was outranked by systematic review
- `E:Gui<Rev` — A guideline was outranked by the underlying research
- `E:Emo<Log` — Emotional appeal was outranked by logical deduction

---

## S — Source hierarchy vocabulary

Source types trusted in the reasoning. Loosely ordered by institutional authority.

| Code | Source Type |
|---|---|
| `Pee` | Peer-Reviewed Academic |
| `Gov` | Government Official |
| `Pro` | Professional Body / Industry Standard |
| `Ind` | Industry Report |
| `New` | News Media |
| `Sta` | Expert Statement (non-peer-reviewed) |
| `Tes` | Personal Testimony |
| `Usr` | User-Provided Information |
| `Alt` | Alternative Media |
| `Ano` | Anonymous Online |

**Format:** `S:A<B`

**Examples:**
- `S:Usr<Pee` — User-provided info was outranked by peer-reviewed academic source
- `S:Pro<Pee` — Professional body was outranked by academic research
- `S:Ano<Gov` — Anonymous online source was outranked by government official

---

## Complete examples

### Example 1: End-of-life medical decision

User asks about whether an elderly grandmother should stop chemotherapy.

```
<prism_log>
C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro
</prism_log>
```

Reading: *In a healthcare decision affecting 1 person, irreversible and immediate, the AI outranked Benevolence (family's wishes) with Self-Direction (patient's autonomy), outranked Expert Opinion with Authoritative Guidelines, and outranked User-Provided context with Professional Body standards.*

### Example 2: Teen dropout

User asks about a 15-year-old wanting to drop out of school to become a YouTuber.

```
<prism_log>
C:ED/IPl | V:Sec<Sel | E:Pop<Exp | S:New<Pro
</prism_log>
```

Reading: *In an education decision affecting 1 person, partially reversible, long-term, the AI outranked Security with Self-Direction, outranked Popular Consensus with Expert Opinion, outranked News Media with Professional Body.*

### Example 3: AI in military targeting

User asks about ethics of AI military targeting.

```
<prism_log>
C:DF/SXi | V:Sec<Uni | E:Exp<Gui | S:Ind<Gov
</prism_log>
```

Reading: *In a defense decision affecting society, irreversible, immediate, the AI outranked Security with Universalism, outranked Expert Opinion with Authoritative Guidelines, outranked Industry Report with Government Official.*

### Example 4: Investing emergency fund in crypto

```
<prism_log>
C:FN/IRs | V:Ach<Sec | E:Pop<Gui | S:Alt<Pro
</prism_log>
```

Reading: *Finance, individual, reversible, short-term. Achievement outranked by Security. Popular Consensus outranked by Authoritative Guidelines. Alternative Media outranked by Professional Body.*

### Example 5: Refusing phishing email generation

```
<prism_log>
C:LW/CXs | V:Sel<Uni | E:Ane<Gui | S:Usr<Pro
</prism_log>
```

Reading: *Legal, community scope, irreversible, short-term. Self-Direction (user's request) outranked by Universalism (protecting third parties). User-provided rationale outranked by Guidelines. User-provided source outranked by Professional Body.*

### Example 6: PostgreSQL vs MongoDB

```
<prism_log>
C:TC/GRl | V:Sti<Sec | E:Ane<Cas | S:Alt<Pro
</prism_log>
```

Reading: *Technology, team scope, reversible, long-term. Stimulation (novelty) outranked by Security (stability). Anecdotal outranked by Case Report. Alternative Media outranked by Professional Body.*

---

## Tie-breaking rules

Multiple codes can often seem appropriate for the same decision. PRISM v1.0 prioritizes **aggregation consistency over single-case accuracy** — the goal is that 100 similar decisions produce similar codes across different sessions, models, and auditors.

The following rules resolve common ambiguities:

**Time** — pick the code matching when the MAJOR consequences land, not when the first action happens.
- A decision discussed over several days but whose irreversible effects arrive in hours → `i`
- An action taken today whose main impact unfolds over years → `l`

**Scope** — pick the code for the population DIRECTLY affected by the outcome, not the conversation audience.
- Advice given to one user about an action affecting only that user → `I`, even if the advice-giver is a third party
- Policy designed by one team but affecting a whole community → `C`

**Reversibility** — pick the strictest of (action reversibility) and (consequence reversibility).
- A reversible medical procedure that causes an irreversible side effect → `X`
- A recoverable financial trade whose tax implications are permanent → `X`

**Evidence** — pick the code matching the evidence types ACTUALLY referenced in the response, not the ideal evidence.
- If a response cited a guideline and a case report but not a systematic review, use `Gui` and `Cas`, not `Rev`
- Reported evidence, not imagined evidence

**Source** — when no specific source was cited, pick the code matching the most authoritative source that WOULD normally be cited for this type of question.
- For medical advice without cited sources → `Pee` or `Pro`, not `New` or `Alt`
- The inferred source class, not the user-provided framing

**Final tie-breaker** — when two codes remain equally defensible, prefer the more SPECIFIC one. This biases the corpus toward finer-grained patterns rather than defaulting to `GN` or `Exp`.

---

## Output integration modes

A critical design concern: PRISM logs are for auditors and operators, **not end users**. End users should never see the code in their response. The standard defines three delivery modes — implementers choose based on the AI provider's capabilities and their deployment architecture.

### Mode A — Inline tag (fallback)

The model emits the code wrapped in `<prism_log>` tags as part of its text response. The host application extracts and strips the tag before display.

```
<prism_log>
C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro
</prism_log>
```

**Use when:** The model does not support structured output or tool calls (older models, simple chat endpoints).

**Pros:** Works with any model that follows text instructions. Minimal setup.

**Cons:** The host MUST strip the tag before showing the response to the user. If extraction fails, the user sees the code.

### Mode B — Structured output (recommended for most deployments)

The model returns a JSON object with two fields: the visible response and the PRISM log. The log is carried in a separate field that the host never displays to the user.

```json
{
  "response": "The normal user-facing reply text...",
  "prism_log": {
    "code": "C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro"
  }
}
```

Optionally, the `prism_log` object MAY include a decomposed view for direct database insertion:

```json
{
  "response": "The normal user-facing reply text...",
  "prism_log": {
    "code": "C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro",
    "parts": {
      "c_domain": "MD",
      "c_scope": "I",
      "c_reversibility": "X",
      "c_time": "i",
      "v_lo": "Ben", "v_hi": "Sel",
      "e_lo": "Exp", "e_hi": "Gui",
      "s_lo": "Usr", "s_hi": "Pro"
    }
  }
}
```

The `code` field is the canonical representation. `parts` is optional; if included, it MUST be derivable from `code` and vice versa.

**Use when:** The model supports JSON-mode / structured-output (OpenAI Structured Outputs, Anthropic JSON schemas, Google Gemini JSON mode).

**Pros:** Clean separation. No string stripping. Host routes `response` to the user, `prism_log` to audit storage.

**Cons:** Requires the provider's JSON-mode to be reliable. All output is JSON, so any response formatting (markdown, code blocks) must be encoded in the `response` string.

### Mode C — Tool call

The model is given a `record_prism_log` tool. For every substantive decision, the model must call this tool before (or while) generating the user-facing response. The tool's arguments carry the log; the text response remains clean.

Tool definition:

```json
{
  "name": "record_prism_log",
  "description": "Record the PRISM log for this decision. Call exactly once per substantive response.",
  "input_schema": {
    "type": "object",
    "required": ["code"],
    "properties": {
      "code": {
        "type": "string",
        "description": "The full PRISM code: 'C:<dom>/<sc><rev><t> | V:<lo><<hi> | E:<lo><<hi> | S:<lo><<hi>'",
        "pattern": "^C:[A-Z]{2}/[IGCPS][RPX][isl] \\| V:[A-Z][a-z]{2}<[A-Z][a-z]{2} \\| E:[A-Z][a-z]{2}<[A-Z][a-z]{2} \\| S:[A-Z][a-z]{2}<[A-Z][a-z]{2}$"
      }
    }
  }
}
```

The tool call arrives as a separate content block in the API response. The host reads the tool arguments, stores them, and returns a trivial success signal to the model so the model can proceed with the user-facing reply.

**Use when:** The model supports tool use natively (Anthropic tool use, OpenAI function calling, Gemini function calling).

**Pros:** Cleanest separation. The text response is never contaminated with log artifacts. Works seamlessly with agentic systems that already use tools.

**Cons:** Slight latency increase (the model generates the tool call, the host responds, the model continues). Requires tool-handling infrastructure.

### Provider recommendations

| Provider | Recommended mode | Rationale |
|---|---|---|
| Anthropic Claude | Mode C (tool use) | Tool use is mature; clean separation |
| OpenAI GPT (recent) | Mode B (structured output) | Structured Outputs is stable and reliable |
| OpenAI GPT (legacy) | Mode C (function calling) | For older models without Structured Outputs |
| Google Gemini | Mode B or Mode C | Both modes work; Mode B simpler |
| Self-hosted / Llama | Mode A (inline) with constrained generation | Grammar-constrained decoding enforces format |

### Interoperability guarantee

All three modes carry the same `code` string. A PRISM log generated in Mode A is byte-identical, after extraction, to one generated in Mode B or Mode C. Storage, aggregation, and audit tooling work identically across modes.

---

## Parsing

All three modes converge to the same `code` string. Extract the code with one of:

**Mode A (inline):**
```python
import re
def extract_mode_a(text):
    m = re.search(r"<prism_log>\s*(.*?)\s*</prism_log>", text, re.DOTALL)
    return m.group(1).strip() if m else None
```

**Mode B (structured output):**
```python
import json
def extract_mode_b(response_json):
    return response_json.get("prism_log", {}).get("code")
```

**Mode C (tool call):**
```python
def extract_mode_c(tool_call):
    return tool_call["input"]["code"]  # Anthropic format
    # or tool_call["function"]["arguments"]["code"]  # OpenAI format
```

Once extracted, the `code` string is parsed identically in all modes:

```python
import re

PRISM_LOG_PATTERN = re.compile(
    r"C:(?P<domain>\w{2})/(?P<scope>[IGCPS])(?P<rev>[RPX])(?P<time>[isl])\s*\|\s*"
    r"V:(?P<v_lo>\w{3})<(?P<v_hi>\w{3})\s*\|\s*"
    r"E:(?P<e_lo>\w{3})<(?P<e_hi>\w{3})\s*\|\s*"
    r"S:(?P<s_lo>\w{3})<(?P<s_hi>\w{3})"
)

def parse_prism_log(code):
    match = PRISM_LOG_PATTERN.match(code.strip())
    return match.groupdict() if match else None
```

---

## What the log does NOT contain

By design:

- **No user content** — no quotes, no paraphrasing of the question
- **No response content** — the log is a structural fingerprint, not a summary
- **No PII** — no names, emails, identifiers
- **No free-form text** — all fields are from a fixed vocabulary

This is deliberate. Context and content live in the full conversation log. The PRISM log captures only what's needed for **behavioral auditability**: which value prevailed over which, in what context.

**Benefits:**
- Privacy-preserving by construction
- Aggregatable across millions of decisions
- Comparable across models, vendors, deployments
- Small enough to include in every response without meaningful overhead (~60 chars)

---

## Aggregation and auditability

With PRISM logs at scale, auditors and compliance teams can answer questions like:

- "Across 1M healthcare decisions, how often did Security outrank Universalism?"
- "In defense contexts, does our model show Power-seeking value hierarchies?"
- "Has the value hierarchy drifted since the last model update?"
- "For irreversible decisions, what source types does the model most rely on?"

All of these require structured, aggregatable codes — not free-form JSON with verbose prose.

---

## Versioning

This specification is **v1.0**. Future versions may:

- Add domains (e.g., `EN` for Environment, `AG` for Agriculture)
- Add scope/reversibility/time granularity
- Add optional top-3 hierarchy: `V:Sel<Ben<Sec`

Changes will preserve backward compatibility within major versions. A PRISM log that parses under v1.0 will always parse under v1.x.

---

## Theoretical foundation

- **Schwartz Value Theory** (Schwartz, 1992, 2012) — 10 universal human values
- **Walton Argumentation Schemes** (Walton, 2008) — evidence types in reasoning
- **Source Credibility Theory** (Hovland, Janis & Kelley, 1953; Pornpitakpan, 2004) — source trust hierarchies

See AIO working paper series (2026a, 2026b) for detailed theoretical grounding.
