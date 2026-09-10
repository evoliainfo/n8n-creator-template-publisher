# Creator submission QA checklist

## A. Baseline
- [ ] Correct/latest workflow baseline selected.
- [ ] Business behavior understood before editing.
- [ ] Functional node count recorded.
- [ ] Sticky count recorded.
- [ ] Connection graph recorded.

## B. Naming
- [ ] Public workflow title is descriptive and action-oriented.
- [ ] No `FINAL`, `Approved`, `Community Final`, or internal version suffix.
- [ ] Functional node names are descriptive.
- [ ] Filename is lowercase hyphenated slug with `.json`.
- [ ] No spaces or `%20` in filename.

## C. Sticky notes
- [ ] One main overview sticky near workflow start.
- [ ] Main sticky contains `How it works`.
- [ ] Main sticky contains `Setup steps`.
- [ ] Main sticky contains `Customization`.
- [ ] Section stickies map to logical stages.
- [ ] Each section sticky is concise and specific.
- [ ] Long explanations are not repeated across stickies.
- [ ] No invented character/word threshold is claimed.
- [ ] No sticky-to-sticky overlap.

## D. Integrity
- [ ] JSON parses.
- [ ] Unique node IDs.
- [ ] Unique node names.
- [ ] Every connection source exists.
- [ ] Every connection target exists.
- [ ] All `$('...')` / `$("...")` references exist.
- [ ] All `$node[...]` references exist.
- [ ] All `$items(...)` references exist.
- [ ] Renamed nodes have all references updated.
- [ ] Documentation matches actual behavior/statuses.

## E. Community safety
- [ ] No API keys/tokens.
- [ ] No credentials objects bound to the author's instance.
- [ ] No `meta.instanceId`.
- [ ] No private email recipient.
- [ ] No private Sheet/database/document ID.
- [ ] No private webhook ID unless intentionally safe.
- [ ] No private client domain/brand in a generic template.
- [ ] No instance-specific errorWorkflow ID.
- [ ] Required configuration uses explicit placeholders.
- [ ] `templateCredsSetupCompleted` is false for the public export.
- [ ] Workflow is inactive for handoff unless current n8n guidance says otherwise.

## F. Production behavior
- [ ] Duplicate/idempotency strategy reviewed.
- [ ] Empty-result path reviewed.
- [ ] Retry behavior reviewed.
- [ ] Rate-limit/polling behavior reviewed when applicable.
- [ ] Validation occurs before irreversible side effects where practical.
- [ ] Partial failure/recovery behavior documented.
- [ ] Sensitive data handling reviewed.

## G. Current guidance
- [ ] Current Creator Hub instructions checked.
- [ ] Official n8n sticky/naming guidance checked.
- [ ] Any new reviewer feedback incorporated.
- [ ] Facts, assumptions, and internal decisions clearly separated.

## Decision
- [ ] All applicable HARD GATES pass.
- [ ] Candidate can be called “submission-ready”.
