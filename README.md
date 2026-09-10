# n8n Creator Template Publisher

A reusable skill and static QA toolkit for preparing n8n workflow JSON files for Creator Hub submission. Current public n8n guidance referenced by the skill was last checked on 2026-09-10.

It helps turn an existing n8n workflow into a cleaner, safer, better-documented submission candidate without silently changing its business logic.

## What it does

The skill checks and guides:

- public workflow naming
- descriptive node naming
- Creator-style sticky notes
- node-reference integrity after renaming
- connection integrity
- public-safe sanitization
- removal of credential bindings and instance-specific metadata
- consistency between documentation and actual workflow behavior
- clean JSON filenames
- static pre-submission QA

It intentionally does **not** claim that passing automated QA guarantees acceptance by n8n. The validator covers machine-checkable gates; private IDs/domains, pinned sample data, behavioral truthfulness, and current Creator guidance still require manual review. Creator standards can evolve, so current official guidance and reviewer feedback always take precedence.

## Repository structure

```text
n8n-creator-template-publisher/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── references/
│   ├── acceptance-evidence.md
│   └── qa-checklist.md
├── scripts/
│   └── validate_creator_template.py
├── tests/
│   └── test_validator.py
└── examples/
    └── README.md
```

## How to use the skill with an AI coding/automation agent

Give the agent access to this repository and instruct it to read `SKILL.md` before modifying a workflow.

Example instruction:

> Read `SKILL.md` and apply the n8n Creator Template Publisher process to `my-workflow.json`. Preserve the workflow's functional behavior unless a change is explicitly required. Produce a Creator-ready JSON and a QA report.

The skill tells the agent how to separate:
- current official n8n guidance
- direct reviewer guidance
- proven accepted patterns
- internal conservative decisions

## Run the validator manually

Requirements:
- Python 3
- no third-party Python packages required

Run the regression tests:

```bash
python3 -m unittest discover -s tests -v
```

Basic validation:

```bash
python3 scripts/validate_creator_template.py my-workflow.json
```

Write the QA report to a file:

```bash
python3 scripts/validate_creator_template.py my-workflow.json \
  --report my-workflow-qa.json
```

Compare a Creator candidate against the original workflow:

```bash
python3 scripts/validate_creator_template.py candidate.json \
  --baseline original.json \
  --require-functional-match \
  --report candidate-qa.json
```

`--require-functional-match` is useful when the intended changes are only documentation, layout, sanitization, or node renaming.

## Recommended workflow

1. Export the workflow from n8n.
2. Keep the original export untouched.
3. Apply the instructions in `SKILL.md`.
4. Save the public candidate with a clean slug filename.
5. Run the validator.
6. Review any functional or generalization changes manually.
7. Re-check current n8n Creator guidance.
8. Submit to n8n.

## Example filename

Workflow title:

```text
Create SEO WordPress blog drafts with Gemini and Google Sheets
```

Public JSON:

```text
create-seo-wordpress-blog-drafts-with-gemini-and-google-sheets.json
```

Avoid filenames such as:

```text
Workflow FINAL v2.json
Community Approved.json
workflow%20final.json
```

## Important

This project is a pre-submission quality and adaptation tool. Final approval remains with n8n.

## License

MIT License. See [`LICENSE`](LICENSE).
