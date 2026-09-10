# Usage examples

## Example 1 — Prepare a workflow for Creator Hub

```text
Read SKILL.md and apply it to ./workflow.json.

Goals:
- preserve business logic;
- rename vague functional nodes where needed;
- update all internal node-name references;
- add Creator-style sticky notes;
- remove instance-specific credentials and identifiers;
- generate a clean public JSON;
- run the static validator;
- report FACTS, ASSUMPTIONS, DECISIONS, and QA.
```

## Example 2 — Documentation-only pass

```text
Apply SKILL.md to candidate.json using original.json as the functional baseline.
Do not change functional behavior.

Then run:

python3 scripts/validate_creator_template.py candidate.json   --baseline original.json   --require-functional-match   --report candidate-qa.json
```

## Example 3 — Reviewer feedback

```text
n8n returned reviewer feedback for this workflow.
Treat the reviewer message as DIRECT REVIEWER GUIDANCE.
Update only what is necessary, then rerun the full QA.
Do not convert reviewer feedback into a universal rule unless n8n states it officially.
```
