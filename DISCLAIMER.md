# Disclaimer

The PRISM Logging Standard is a technical specification and a set of supporting tools for recording structured reasoning logs from AI systems. It is not legal advice and is not a certified compliance product.

## No guarantee of regulatory compliance

Use of this standard does not by itself guarantee compliance with any specific regulation, including but not limited to:

- **EU AI Act** (Regulation (EU) 2024/1689)
- **Other AI, data protection, or audit regulations** in any jurisdiction

Regulatory compliance depends on the full governance system around an AI deployment, including data handling, retention, access control, security, human oversight processes, impact assessments, and organization-specific policies. PRISM logs provide one component of the structured evidence that compliance programs and third-party auditors can reference.

## Not a substitute for legal or professional advice

Organizations deploying AI systems subject to regulatory oversight should consult qualified legal counsel, compliance professionals, and relevant certification bodies in their jurisdiction. Final determinations of compliance with any regulation must be made by appropriately qualified experts.

## Use at your own risk

The standard and all accompanying code, prompts, validators, and documentation are provided "AS IS," without warranty of any kind, express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, non-infringement, or fitness for any regulatory purpose.

In no event shall AI Integrity Organization (AIO) or the contributors be liable for any claim, damages, regulatory finding, or other liability arising from, out of, or in connection with the standard or its use.

## Scope of what PRISM logs capture

PRISM logs record **reported** reasoning — the values, evidence types, and source types a model reports as having driven its decision. They do not prove that the model's internal computation followed that reasoning. This is a limitation shared by all self-reported reasoning logs, including chain-of-thought traces.

Auditors and operators should treat PRISM logs as structured, aggregatable evidence — not as infallible causal records.

## Relationship to commercial services

AI Integrity Organization (AIO) offers optional commercial services (certification, analytics, training, consulting) that can supplement use of this free and open standard. None of those services are required to use the standard. Conversely, neither AIO's services nor the standard itself is marketed as a guarantee of regulatory compliance.

---

*Questions about this disclaimer: open a GitHub issue. Questions about applying the standard to a specific regulatory context: consult qualified legal counsel in your jurisdiction.*
