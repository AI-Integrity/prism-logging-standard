# Contributing

Thanks for your interest in improving the PRISM Logging Standard.

## Ways to contribute

**Report deployment experience.** If you've deployed PRISM logging, tell us what worked and what didn't. Open an issue with:
- Which model you used
- What prompt variant
- Observed reliability rate
- Any issues with output format

**Propose vocabulary extensions.** The Schwartz value list, evidence types, source types, and domains are finite by design — but may need refinement for specific contexts. Propose additions via pull request with justification.

**Submit integration guides.** If you've integrated PRISM with a framework (LangChain, LlamaIndex, Haystack, custom agent frameworks), contribute an integration guide.

**Share validation tooling.** Better validation scripts, linters, or dashboards that help users verify their deployments.

**Translate.** Korean and English are maintained by AIO. Translations to other major languages are welcome.

## What we won't accept

**Changes that break backward compatibility** in v1.0. Breaking changes go to v2.0.

**Removing Schwartz value grounding.** The theoretical foundation is intentional. If you disagree with Schwartz theory, we suggest building an alternative standard rather than modifying this one.

**Adding proprietary elements.** This standard stays free and open.

## Process

1. Open an issue first to discuss larger changes
2. Fork, branch, and submit a PR
3. For vocabulary changes, cite the reasoning source (papers, deployment experience, regulation text)
4. We aim to respond within 14 days

## Maintainer

Primary maintainer: AI Integrity Organization (AIO), Geneva, Switzerland.
Contact: 2sk@aioq.org
