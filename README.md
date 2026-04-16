# PRISM Logging Standard

**An open standard for logging AI reasoning decisions — value, evidence, and source hierarchies — as structured one-line codes, for regulatory compliance and behavioral auditability.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0-blue.svg)](./CHANGELOG.md)
[![한국어](https://img.shields.io/badge/docs-한국어-red.svg)](./docs/README_KR.md)

---

## What a PRISM log looks like

```
<prism_log>
C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro
</prism_log>
```

A single line. ~60 characters. Contains:

- **C** — Context: domain, scope of impact, reversibility, time horizon
- **V** — Value hierarchy: Schwartz value outranked by Schwartz value
- **E** — Evidence hierarchy: evidence type outranked by evidence type
- **S** — Source hierarchy: source type outranked by source type

The `<` reads as "outranked by." Left = deprioritized. Right = prevailed.

[Full specification →](./SPECIFICATION.md)

---

## Why this exists

AI regulation is shifting from product-level compliance to behavior-level accountability. The EU AI Act's high-risk provisions, taking effect in August 2026, require that operators of high-risk AI systems maintain **auditable records of AI reasoning** — not just latency and token counts, but the values, evidence, and sources that drove each decision. Similar regimes are developing in other jurisdictions.

Current logging frameworks do not capture this. **PRISM Logging Standard does.**

Appending a structured vocabulary to a system prompt makes any modern LLM emit regulation-friendly reasoning codes. No new infrastructure. No API changes. No model retraining.

### A pre-standard in a standards gap

Official harmonised standards for EU AI Act compliance (developed by CEN/CENELEC and related bodies) are still under development at the time of v1.0 publication. Organizations facing the August 2026 deadline cannot wait for final standards to begin structured logging.

PRISM v1.0 is designed as a **pre-standard**: usable today, structurally aligned with the known requirements (Article 12's automatic logging, Article 13's transparency of reasoning, Article 14's human oversight), and modular enough to adapt when official standards converge.

**Modular design:** The vocabulary (domains, Schwartz values, evidence types, source types, scope, reversibility, time) is defined as fixed tables that can be extended or remapped without changing the structural format. If future harmonised standards require different taxonomies, adapting PRISM becomes a vocabulary-update task, not a reimplementation.

---

## Quick start

PRISM v1.0 supports three output modes. Pick based on your model's capabilities:

| Mode | When to use | User sees log? |
|---|---|---|
| **A. Inline tag** | Older models without structured output | No (host strips `<prism_log>` tag) |
| **B. Structured output** | Models with JSON mode (OpenAI, Gemini, Claude) | No (separate JSON field) |
| **C. Tool call** | Models with native tool use (Claude, OpenAI, Gemini) | No (separate tool_use block) |

**Critical:** In all modes, the PRISM log is for audit storage only — it must never be shown to end users. Mode A requires the host to strip the tag. Modes B and C provide the separation natively.

See the system prompt for your chosen mode:

- [`system_prompts/prism_v1_en_inline.md`](./system_prompts/prism_v1_en_inline.md) — Mode A
- [`system_prompts/prism_v1_en_json.md`](./system_prompts/prism_v1_en_json.md) — Mode B
- [`system_prompts/prism_v1_en_tool.md`](./system_prompts/prism_v1_en_tool.md) — Mode C

### Minimal integration (Mode C, Anthropic Claude)

```python
from anthropic import Anthropic

client = Anthropic()

PRISM_TOOL = {
    "name": "record_prism_log",
    "description": "Record the PRISM log for a substantive decision.",
    "input_schema": {
        "type": "object",
        "required": ["code"],
        "properties": {"code": {"type": "string"}}
    }
}

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=2000,
    system=PRISM_MODE_C_PROMPT,  # from system_prompts/prism_v1_en_tool.md
    tools=[PRISM_TOOL],
    messages=[{"role": "user", "content": user_input}]
)

# User-facing text and audit log are separate blocks
user_facing = ""
prism_code = None
for block in response.content:
    if block.type == "text":
        user_facing += block.text
    elif block.type == "tool_use" and block.name == "record_prism_log":
        prism_code = block.input["code"]

# user_facing → user interface
# prism_code → audit log storage
```

---

## Why code format, not JSON

PRISM logs are deliberately designed as compact codes rather than verbose JSON:

| Property | Code format | JSON format |
|---|---|---|
| Length | ~60 chars | ~300+ chars |
| Privacy | No user content | Risk of leaking context |
| Aggregation | Direct SQL/grep | Requires flattening |
| Cost per call | ~25 output tokens | ~150 output tokens |
| Human-readable at scale | Yes | No |

The log is a **structural fingerprint**, not a summary. Context and content live in your conversation log. The PRISM code captures only what's needed for behavioral auditability.

---

## How PRISM logs map to common compliance needs

Regulators increasingly expect records that answer three questions about every significant AI decision: what was the context, what reasoning drove it, and can it be reviewed after the fact. PRISM logs provide structured evidence for each:

| Compliance need | PRISM field |
|---|---|
| Record of context for each decision | `C:` layer (domain, scope, reversibility, time) |
| Transparency of reasoning priorities | `V:` and `E:` layers |
| Identifiable source trust patterns | `S:` layer |
| Aggregatable evidence for audits | Full code, searchable |
| Drift detection across model versions | Time-series of code distributions |

### Indicative mapping to EU AI Act (for reference)

The following table shows how PRISM fields can contribute to evidence for specific EU AI Act high-risk provisions. **This is an orientation aid, not a compliance claim** — PRISM logs contribute to but do not by themselves satisfy any of these requirements. See [DISCLAIMER.md](./DISCLAIMER.md).

| EU AI Act provision | Requirement focus | PRISM field(s) that contribute |
|---|---|---|
| Art. 12(1) — Automatic logging | Automatic event capture over system lifetime | Full PRISM code emitted per substantive decision |
| Art. 12(2)(a) — Period of use | Record of when the system was operating | Timestamp added by host at log-storage time |
| Art. 12(2) — Traceability | Identification of situations that may produce risks | `C:` layer (domain, scope, reversibility, time) |
| Art. 12(3) — Integrity of logs | Protection against unauthorised modification | Optional SHA-256 integrity helper (see [tools/](./tools/)) |
| Art. 13 — Transparency | Information enabling interpretation of outputs | `V:` and `E:` layers (reported reasoning priorities) |
| Art. 14 — Human oversight | Ability for humans to oversee AI operation | Structured code reviewable by human auditors |
| Art. 15 — Accuracy, robustness | Consistent behaviour under similar conditions | Aggregate analysis of codes across time and versions |

Integrity of logs under Art. 12(3) is supported by the optional `prism-hash` utility ([tools/prism_hash.py](./tools/prism_hash.py)) which generates tamper-evident SHA-256 hashes for each log.

The specification does not claim legal equivalence with any particular regulation. What it provides is **structured evidence** that compliance programs and third-party auditors can reference alongside their own documentation.

---

## What this standard does NOT claim

Being direct about limitations:

- **It does not prove the model "really" reasoned this way.** LLM self-reports can be post-hoc rationalization. PRISM logs are *reported* reasoning, not causal traces.
- **It does not replace independent audits.** Internal logs require external verification to carry regulatory weight.
- **It does not guarantee compliance with any regulation by itself.** It provides structured evidence; compliance depends on the full governance system around it.

These limitations are shared by all reasoning logs (chain-of-thought, attention traces, internal documentation). PRISM logs are the format best positioned for auditability at scale — not a complete solution.

---

## Commercial services (optional)

This standard is free under MIT. Some organizations also need:

- **"PRISM Compliant" certification** — third-party verification that a deployment conforms to the standard
- **Industry benchmark data** — compare a deployment to cross-industry aggregates
- **Auditor training** — certified auditor program
- **Enterprise consulting** — organization-specific value hierarchy design and governance integration

These services are provided by [AI Integrity Organization (AIO)](https://aioq.org). Using the standard does not require purchasing any service.

---

## Theoretical foundation

PRISM is developed and maintained by [AI Integrity Organization (AIO)](https://aioq.org), a Swiss-registered nonprofit.

The standard draws on:

- **Schwartz Value Theory** (Schwartz, 1992, 2012) — 10 universal human values, validated across 80+ cultures
- **Walton Argumentation Schemes** (Walton, 2008) — taxonomy of evidence types in reasoning
- **Source Credibility Theory** (Hovland, Janis & Kelley, 1953; Pornpitakpan, 2004) — source trust hierarchies

Working papers:

- S. Lee (2026a). AI Integrity: Definition, Authority Stack Model, and Enhanced Cascade Mapping Hypothesis. arXiv:cs.AI.
- S. Lee (2026b). The PRISM Framework for Measuring AI Value Hierarchies. arXiv:cs.AI.
- S. Lee (2026c). Measuring AI Value Priorities: Empirical Analysis. arXiv:cs.AI.
- S. Lee (2026d). PRISM Risk Signal Framework: Hierarchy-Based Red Lines for AI Behavioral Risk. SSRN 6449079.

Registered in the [OECD Catalogue of Tools & Metrics for Trustworthy AI](https://oecd.ai).

---

## Repository contents

| File | Purpose |
|---|---|
| [`SPECIFICATION.md`](./SPECIFICATION.md) | Complete v1.0 code specification (includes output mode definitions) |
| [`DISCLAIMER.md`](./DISCLAIMER.md) | Scope, limitations, and non-warranty terms |
| [`system_prompts/prism_v1_en_inline.md`](./system_prompts/prism_v1_en_inline.md) | Mode A prompt — English |
| [`system_prompts/prism_v1_en_json.md`](./system_prompts/prism_v1_en_json.md) | Mode B prompt — English |
| [`system_prompts/prism_v1_en_tool.md`](./system_prompts/prism_v1_en_tool.md) | Mode C prompt — English |
| [`system_prompts/prism_v1_kr_*.md`](./system_prompts/) | Korean versions of all three modes |
| [`examples/`](./examples/) | Real-world log examples across 7 domains |
| [`tests/validate.py`](./tests/validate.py) | Validator with multi-mode extraction |
| [`tools/prism_parser.py`](./tools/prism_parser.py) | Code extraction & structured parsing helper |
| [`tools/prism_hash.py`](./tools/prism_hash.py) | SHA-256 integrity helper (independent & chained hashes) |
| [`docs/integration_guide.md`](./docs/integration_guide.md) | Per-provider integration guide |

---

## License & disclaimer

MIT. Use it, modify it, embed it in commercial products. See [LICENSE](./LICENSE).

**Important:** This standard is a technical specification, not legal advice. Using it does not guarantee compliance with any regulation. See [DISCLAIMER.md](./DISCLAIMER.md) for full scope and limitations.

Attribution appreciated but not required.

---

## Contact

- Issues / suggestions: open a GitHub issue
- Commercial inquiries: 2sk@aioq.org
- Website: [aioq.org](https://aioq.org)

---

한국어 문서: [README_KR.md](./docs/README_KR.md)
