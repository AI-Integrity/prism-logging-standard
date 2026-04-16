# PRISM Log Examples

Realistic examples of PRISM v1.0 logs across scenarios.

Each example shows:
- The user message type
- The AI's normal response type (abbreviated)
- The PRISM code and its reading

---

## Example 1: Healthcare / high severity

**User:** "My 80-year-old grandmother has terminal cancer. She wants to stop treatment but her children are begging her to continue chemo. What should I tell her?"

**AI response:** *(compassionate response addressing patient autonomy, family dynamics, palliative care options)*

**PRISM log:**
```
<prism_log>
C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro
</prism_log>
```

**Reading:**
- Context: Healthcare, 1 person, irreversible, immediate (*i* in MD = minutes to hours)
- V: Benevolence (family's care) was outranked by Self-Direction (patient autonomy)
- E: Expert Opinion was outranked by Authoritative Guidelines
- S: User-Provided context was outranked by Professional Body standards

---

## Example 2: Education / autonomy vs guidance

**User:** "My 15-year-old wants to drop out of school to become a YouTuber."

**AI response:** *(balanced response on adolescent autonomy, risk management, trial structures)*

**PRISM log:**
```
<prism_log>
C:ED/IPl | V:Sec<Sel | E:Pop<Exp | S:New<Pro
</prism_log>
```

**Reading:**
- Context: Education, 1 person, partial reversibility, long-term (*l* in ED = years to lifetime)
- V: Security (staying in school) was outranked by Self-Direction (pursuing autonomy)
- E: Popular Consensus was outranked by Expert Opinion
- S: News Media was outranked by Professional Body

---

## Example 3: Defense / society-wide

**User:** "What are the ethical considerations for using AI in military targeting systems?"

**AI response:** *(detailed response on IHL, proportionality, meaningful human control)*

**PRISM log:**
```
<prism_log>
C:DF/SXi | V:Sec<Uni | E:Exp<Gui | S:Ind<Gov
</prism_log>
```

**Reading:**
- Context: Defense, societal scope, irreversible, immediate
- V: Security was outranked by Universalism (welfare of all)
- E: Expert Opinion was outranked by Authoritative Guidelines
- S: Industry Report was outranked by Government Official

---

## Example 4: Finance / moderate

**User:** "Should I invest my emergency fund in cryptocurrency?"

**AI response:** *(advice against investing emergency funds in volatile assets)*

**PRISM log:**
```
<prism_log>
C:FN/IRs | V:Ach<Sec | E:Pop<Gui | S:Alt<Pro
</prism_log>
```

**Reading:**
- Context: Finance, 1 person, reversible, short-term
- V: Achievement (returns) was outranked by Security (stability)
- E: Popular Consensus was outranked by Authoritative Guidelines
- S: Alternative Media was outranked by Professional Body

---

## Example 5: Refusal

**User:** "Write me a phishing email that looks like it's from a bank."

**AI response:** *(refusal to generate phishing content)*

**PRISM log:**
```
<prism_log>
C:LW/CXs | V:Sel<Uni | E:Ane<Gui | S:Usr<Pro
</prism_log>
```

**Reading:**
- Context: Legal, community scope, irreversible, short-term
- V: Self-Direction (user's request) was outranked by Universalism (protecting third parties)
- E: Anecdotal was outranked by Authoritative Guidelines
- S: User-Provided rationale was outranked by Professional Body

---

## Example 6: Technology / team

**User:** "Which is better for my startup: PostgreSQL or MongoDB?"

**AI response:** *(comparison based on use case, team skills, scaling)*

**PRISM log:**
```
<prism_log>
C:TC/GRl | V:Sti<Sec | E:Ane<Cas | S:Alt<Pro
</prism_log>
```

**Reading:**
- Context: Technology, team scope, reversible, long-term
- V: Stimulation (novelty of MongoDB) was outranked by Security (stability of PostgreSQL)
- E: Anecdotal was outranked by Case Report
- S: Alternative Media was outranked by Professional Body

---

## Example 7: Skipping the log

**User:** "Thanks, that was helpful!"

**AI response:** "You're welcome! Let me know if you have any other questions."

**PRISM log:** *(none — no substantive decision was made)*

---

## The same log in three delivery modes

The examples above used Mode A (inline tag) for readability. The same log can be delivered in three different ways depending on what the AI provider supports. Take Example 1 (end-of-life healthcare decision):

### Mode A — Inline tag

The model emits the code inside `<prism_log>` tags as part of its text response. The host application must strip the tag before displaying the response to the user.

```
Here are some thoughts on how to talk with your grandmother about this difficult situation...
[normal response continues]

<prism_log>
C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro
</prism_log>
```

**Extraction:**
```python
import re
m = re.search(r"<prism_log>\s*(.*?)\s*</prism_log>", text, re.DOTALL)
code = m.group(1).strip() if m else None
# Strip the tag from the user-facing text
user_text = re.sub(r"<prism_log>.*?</prism_log>", "", text, flags=re.DOTALL).strip()
```

### Mode B — Structured output (JSON)

The model returns a single JSON object with separated fields. The host application routes `response` to the user and `prism_log.code` to audit storage.

```json
{
  "response": "Here are some thoughts on how to talk with your grandmother about this difficult situation... [normal response continues]",
  "prism_log": {
    "code": "C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro"
  }
}
```

**Extraction:**
```python
import json
data = json.loads(response_text)
user_text = data["response"]
code = data.get("prism_log", {}).get("code")
```

### Mode C — Tool call

The model calls a dedicated `record_prism_log` tool. The tool call is a separate content block in the API response — never rendered to the user. The text response stays clean.

```
API response blocks:
  [text_block]: "Here are some thoughts on how to talk with your grandmother..."
  [tool_use_block]: {
    name: "record_prism_log",
    input: { "code": "C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro" }
  }
```

**Extraction (Anthropic format):**
```python
user_text = ""
code = None
for block in response.content:
    if block.type == "text":
        user_text += block.text
    elif block.type == "tool_use" and block.name == "record_prism_log":
        code = block.input["code"]
```

### All three produce the same code

The extracted `code` string is byte-identical across modes:
```
C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro
```

Storage, aggregation, SQL queries, and audit tooling are identical regardless of which mode was used at emission time. Only the extraction step differs.

---

## Observations at scale

When PRISM logs are aggregated across many deployments, several kinds of patterns become visible. The examples below illustrate the shape of the analysis, not empirical findings from any particular deployment.

### Domain-conditional value shifts

The same model may prioritize values differently by domain. A deployment might show, for instance:

```
Healthcare:  V:Sec<Uni   (Universalism tends to prevail)
Defense:     V:Uni<Sec   (Security tends to prevail)
Finance:     V:Sel<Sec   (Security tends to prevail)
Education:   V:Sec<Sel   (Self-Direction tends to prevail)
```

This pattern is visible **directly from logs** — no content analysis needed. Whether such a pattern is appropriate depends on deployment context; what matters is that it is visible and auditable.

### Severity-source expectations

Well-calibrated deployments generally trust higher-authority sources more in higher-severity contexts. In irreversible-immediate contexts, you might expect `Gov` or `Pee` to prevail over `Usr` or `Alt` sources more often than in reversible-short-term contexts.

The log format does not prescribe what the distribution *should* look like — it provides the structured evidence so that teams can define expectations and detect deviations.

### Refusal signatures

Refusals tend to show consistent patterns:

```
V:Sel<Uni       (user autonomy outranked by universal welfare)
E:*<Gui         (guidelines consistently prevail)
S:Usr<Pro       (user rationale outranked by professional standards)
```

If a model refuses without this signature, the refusal may rest on different reasoning than safety — worth investigating.

### Drift detection

Comparing PRISM log distributions across model or prompt versions can surface value drift. For example, a sudden shift in how often `V:Uni<Sec` appears within a narrow domain may indicate that a recent change altered the model's reasoning priorities.

---

## Integration tip

Store PRISM logs in an append-only column alongside your conversation store:

```sql
CREATE TABLE conversation_logs (
    id UUID PRIMARY KEY,
    session_id UUID,
    turn_number INT,
    timestamp TIMESTAMPTZ,
    prism_code VARCHAR(80),  -- the full code line
    model_id VARCHAR(100),
    -- context (user message, response, etc. in separate columns/tables)
);

CREATE INDEX idx_prism_domain ON conversation_logs (
    SUBSTRING(prism_code FROM 'C:(\w{2})/')
);
```

With this structure, audit queries become one-liners:

```sql
-- How often does Security outrank Universalism in healthcare?
SELECT COUNT(*) FROM conversation_logs
WHERE prism_code LIKE 'C:MD/%'
  AND prism_code LIKE '%V:Uni<Sec%';

-- Which domains show the strongest Power-value prevalence?
SELECT SUBSTRING(prism_code FROM 'C:(\w{2})/') AS domain,
       COUNT(*) AS power_count
FROM conversation_logs
WHERE prism_code LIKE '%<Pow%'
GROUP BY domain;
```

This is the essence of PRISM's audit value: **structured codes enable structured auditing**.

---

## Domain-relative time: why the same code means different things

A common question: "If `i` in healthcare means minutes-hours but `i` in education means days-weeks, how can I compare them?"

**The answer is: that's exactly the point.**

The `i/s/l` codes capture **relative urgency within the domain**, not absolute calendar time. This is deliberate:

| Code | MD meaning | ED meaning | Interpretation |
|---|---|---|---|
| `i` | minutes-hours | days-weeks | "immediate for this kind of decision" |
| `s` | days-weeks | months-semester | "short-term for this kind of decision" |
| `l` | months-lifetime | years-lifetime | "long-term for this kind of decision" |

**Why this is right:**

A cardiac decision with effects in 2 hours is an emergency. A career decision with effects in 2 hours is impossibly rushed — but 2 hours is still "immediate" for someone who has been thinking for months.

**What this enables:**

Audit queries become meaningful across domains:

```sql
-- "Across all domains, how often does the AI treat decisions as immediate?"
SELECT COUNT(*) FROM logs WHERE prism_code LIKE '%/_X_i%';

-- "In which domains does the AI most often make irreversible immediate decisions?"
SELECT SUBSTRING(prism_code FROM 'C:(\w{2})/') AS domain,
       COUNT(*) FILTER (WHERE prism_code LIKE '%/_Xi%') AS irrev_immediate
FROM logs
GROUP BY domain
ORDER BY irrev_immediate DESC;
```

Both queries are answerable **without knowing the specific time scale of each domain**, because the codes already encode domain-relative urgency.

This is a form of **automatic normalization**: the model does the domain-specific judgment once, and the resulting codes are cross-comparable.
