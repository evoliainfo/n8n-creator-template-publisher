# Changelog

## 1.0.1 - 2026-09-10

- Detect missing or invalid workflow/node identifiers and names before validation.
- Include workflow settings in `--require-functional-match`, while allowing removal of instance-specific `errorWorkflow`.
- Detect hard-coded email addresses across the complete workflow JSON, not only functional node parameters.
- Report pinned data and top-level workflow identifiers for manual review.
- Detect internal/publication suffixes in workflow titles.
- Add five regression tests for validator behavior.
- Clarify that automated QA does not replace manual review or current n8n Creator guidance.

## 1.0.0

- Initial skill, evidence hierarchy, QA checklist, examples, MIT license, and static validator.
