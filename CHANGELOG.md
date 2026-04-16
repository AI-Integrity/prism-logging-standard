# Changelog

## v1.0 — 2026-04-16 (Initial public release)

First public release of the PRISM Logging Standard.

### Design

- **Format:** single-line structured code, ~60 chars
- **Privacy-preserving:** no user content, no response content, no PII
- **Aggregation-first:** designed for SQL/grep-based auditing at scale
- **UX-aware:** three delivery modes keep the log out of end-user views

### Three output modes

- **Mode A — Inline tag:** `<prism_log>...</prism_log>` in text response. Fallback for models without structured output. Host application strips the tag before display.
- **Mode B — Structured output:** JSON object with separated `response` and `prism_log` fields. Recommended for models with mature JSON-mode support (OpenAI Structured Outputs, Gemini).
- **Mode C — Tool call:** Dedicated `record_prism_log` tool invoked per decision. Cleanest separation. Recommended for Anthropic Claude and agentic systems.

All three modes produce a byte-identical PRISM code string. Storage, aggregation, and audit tooling work identically across modes.

### Tie-breaking rules

The standard includes explicit tie-breaking rules to maximize aggregation consistency across sessions, models, and auditors:

- Time: pick when MAJOR consequences land, not when first action happens
- Scope: pick population DIRECTLY affected by the outcome
- Reversibility: pick the stricter of action vs. consequence reversibility
- Evidence: pick codes matching evidence ACTUALLY referenced
- Source: pick the most authoritative source that would normally apply
- Final tiebreaker: prefer the more SPECIFIC code

### Included

- [`SPECIFICATION.md`](./SPECIFICATION.md) — complete v1.0 code specification including three output modes
- System prompts for each mode × two languages (6 files total)
- Validator with self-tests (extracts codes from all three modes)
- Integration guide for Anthropic, OpenAI, Google, Llama
- Example logs across 7 domains
- MIT License

### Vocabulary (v1.0)

- **Domains:** 7 (MD, ED, LW, DF, FN, TC, GN)
- **Scope:** 5 levels (I, G, C, P, S)
- **Reversibility:** 3 levels (R, P, X)
- **Time horizon:** 3 levels (i, s, l), domain-relative
- **Schwartz values:** 10 (Pow, Ach, Hed, Sti, Sel, Uni, Ben, Tra, Con, Sec)
- **Evidence types:** 10 (Rev, Dat, Cas, Gui, Exp, Log, Tri, Pop, Emo, Ane)
- **Source types:** 10 (Pee, Gov, Pro, Ind, New, Sta, Tes, Usr, Alt, Ano)

### Theoretical foundation

- Schwartz Value Theory (Schwartz, 1992, 2012)
- Walton Argumentation Schemes (Walton, 2008)
- Source Credibility Theory (Hovland, Janis & Kelley, 1953; Pornpitakpan, 2004)

### Regulatory context

Designed with common auditability requirements in mind, including the EU AI Act's logging and transparency provisions (Articles 12, 13, 14). Not claimed as a legal equivalent for any specific regulation.

---

## Future versions

Planned considerations for v1.1 (non-breaking):
- Additional domains for specialized deployments (EN environment, AG agriculture)
- More calibration examples in prompts
- Additional language translations

Planned for v2.0 (if warranted, breaking changes allowed):
- Optional top-3 hierarchy field
- Multi-turn context field
- Confidence decomposition
- Domain-specific sub-codes

Backward compatibility guarantee: any PRISM log valid under v1.0 remains valid under all v1.x versions. The `code` string format is stable across all three delivery modes — only the wrapping differs.
