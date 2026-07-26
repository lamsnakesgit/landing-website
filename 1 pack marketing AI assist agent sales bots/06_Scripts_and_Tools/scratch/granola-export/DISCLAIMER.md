# Disclaimer

## What this tool is

`granola-export` is a personal data recovery tool. It calls Granola.ai's REST API on behalf of the authenticated user (you), using the auth tokens already stored on your Mac by the Granola desktop application. The tool never logs in, never bypasses authentication, never modifies Granola's behavior, and never makes any request the user could not make by clicking around the app themselves.

## What this tool is for

- Backing up your own meeting notes, transcripts, and AI summaries
- Recovering data hidden by tier-related UI gates (e.g. after a free-tier downgrade)
- Migrating your data to a different tool
- Auditing what data Granola holds about you

## What this tool is NOT for

- Extracting data from accounts you do not own
- Scraping public Granola content at scale
- Building competing services using extracted data
- Any commercial redistribution of extracted content

## Your responsibilities

By using this tool, you affirm that:

- You are operating only against your own Granola account
- You have read and will comply with [Granola's Terms of Service](https://www.granola.ai/policies/terms)
- You will not redistribute extracted data
- You will not use this tool for any purpose that would harm Granola, its users, or any third parties

## Legal context

Personal data portability is recognized in most major jurisdictions:

- **EU**: [GDPR Article 20 — Right to data portability](https://gdpr-info.eu/art-20-gdpr/)
- **California**: [CCPA right to know / right to delete](https://oag.ca.gov/privacy/ccpa)
- **UK**: [UK GDPR Art. 20](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/individual-rights/right-to-data-portability/)
- **Brazil**: [LGPD Art. 18](https://lgpd-brazil.info/chapter_03/article_18)

The tool's design — operating only on the user's own data, via the user's own authenticated session — is consistent with these rights. Whether your specific use complies with applicable law in your jurisdiction depends on your circumstances; consult a lawyer if uncertain.

## On the relationship to Granola

This is a data-portability tool, not a hostile tool. The author has no affiliation with Granola Labs Ltd., positive or negative, beyond being a former user. Granola is a polished, useful product; if it works for you, keep using it.

If Granola wishes to be in touch about this tool, the issue tracker on this repository is the canonical contact path.

## No warranty

This software is provided "as is", without warranty of any kind. The Granola API is undocumented and may change at any time, breaking this tool. The authors are not responsible for data loss, account issues, or any other consequence of using this tool.

If Granola modifies their API in a way that breaks this tool, the tool may stop working without warning. There is no SLA, no support contract, and no guarantee of continued operation. Pull requests and issue reports are how this tool gets fixed when it breaks.

## Contact

Issues at https://github.com/moona3k/granola-export/issues.

Please do **not** use issues to ask how to extract data from accounts you do not own. Such issues will be closed without comment.
