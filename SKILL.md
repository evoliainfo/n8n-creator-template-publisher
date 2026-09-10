---
name: n8n-creator-template-publisher
description: Prepare, sanitize, document, rename, and statically validate n8n workflow JSON files for Creator Hub submission using current n8n guidance plus proven accepted submission patterns. Use when a workflow must be made Creator-ready, community-safe, resubmitted after review, or checked before upload.
version: 1.0.1
---

# n8n Creator Template Publisher

## Purpose

Turn an existing n8n workflow into a Creator Hub / community submission candidate without silently changing its business logic.

This skill is for **workflow templates**. Do not apply package/npm rules for community nodes unless the user is actually publishing a custom node package.

## Source hierarchy

Always separate evidence by authority:

1. **CURRENT OFFICIAL** — current n8n Creator Hub instructions, official n8n documentation, and official n8n workflow guidance.
2. **DIRECT REVIEWER GUIDANCE** — messages sent by n8n reviewers/support and supplied by the user.
3. **PROVEN ACCEPTANCE PATTERN** — workflows that the user confirms were accepted by n8n.
4. **INTERNAL DECISION** — conservative rules chosen to reduce rejection risk.

Never present levels 3 or 4 as an official n8n requirement.

Because Creator standards change, verify current official information at the time of a new submission whenever web access is available. If it cannot be verified, say so and do not claim current compliance.

## Known current evidence

Last web verification of the official public sources listed below: **2026-09-10**.

### CURRENT OFFICIAL
The official n8n workflow **“Auto-generate sticky notes and rename nodes”** says it follows n8n sticky-note and naming guidelines required for publication. Its documented behavior:
- parses nodes, connections, and spatial layout;
- groups nodes into logical clusters;
- generates descriptive sticky notes;
- resolves sticky-note overlaps;
- can rename nodes to descriptive names.

Reference:
https://n8n.io/workflows/13868-auto-generate-sticky-notes-and-rename-nodes/

### DIRECT REVIEWER GUIDANCE
A reviewer response supplied by the user states:
- n8n is changing minimum and maximum sticky-note text standards;
- sticky notes should remain concise and scannable;
- longer explanations/walkthroughs should move out of the sticky note, with short video suggested when useful;
- section stickies should give concise but specific information about what each workflow step does.

**Important:** no numeric text limit was supplied. Never invent one.

### PROVEN ACCEPTANCE PATTERN
The user has confirmed acceptance of:
- an Instagram Carousel workflow;
- a Google Maps LeadGen workflow.

Both accepted submissions support this pattern:
- one main overview sticky;
- multiple section stickies aligned to logical workflow stages;
- descriptive functional node names;
- section stickies that explain the block in one concise, specific description;
- community-safe exports without user credential bindings or exposed secrets.

## Mandatory operating method

### 1. Identify the correct baseline

Before editing:
- inspect the workflow name, nodes, connections, settings, credentials, IDs, placeholders, expressions, code, and sticky notes;
- look for a newer/hardened version before working from an older export;
- if multiple versions exist, prefer the latest version that is functionally stronger unless the user explicitly names a different baseline.

Report:
- **FACTS**
- **ASSUMPTIONS**
- **DECISIONS**

Do not build or rewrite functionality merely because a template is being prepared for Creator Hub.

### 2. Preserve functional integrity

For documentation/naming-only work:
- preserve functional node IDs;
- preserve functional node types and typeVersions;
- preserve parameters and execution settings;
- preserve connection topology;
- preserve retry/error behavior;
- preserve trigger behavior;
- preserve workflow status semantics.

Renaming a node requires updating:
- connection source keys;
- connection targets;
- `$('Node Name')`;
- `$("Node Name")`;
- `$node["Node Name"]`;
- `$items("Node Name")`;
- any other explicit node-name references in expressions or Code nodes.

Never assume a rename is cosmetic until all references are verified.

If community sanitization requires changing private brand-specific prompts, URLs, recipients, or configuration, classify it explicitly as a **community-generalization change**, not as “logic unchanged”.

### 3. Workflow title and filename

Use a human-readable workflow title that describes the outcome and major integrations.

Preferred marketplace pattern:
`<Action + outcome> with <major integrations>`

Examples of style:
- `Find, enrich and qualify Google Maps leads with Apify, Outscraper, Gemini and Notion`
- `Create SEO WordPress blog drafts with Gemini and Google Sheets`

Do not add internal suffixes such as:
- `FINAL`
- `Community Final`
- `Approved`
- `v2`
- `Hardened`

unless the user explicitly wants them in the public title.

For the downloadable JSON filename:
- lowercase;
- hyphen-separated;
- ASCII-safe where practical;
- no spaces;
- no `%20`;
- no internal status suffix.

Example:
`create-seo-wordpress-blog-drafts-with-gemini-and-google-sheets.json`

### 4. Functional node naming

Functional nodes must be immediately understandable on the canvas.

Prefer:
- `Read Blog Queue from Sheets`
- `Check if Post Exists`
- `Generate Article with Gemini`
- `Finalize Draft in Sheets`

Avoid default or opaque names such as:
- `HTTP Request`
- `Code`
- `Code1`
- `Set`
- `If`
- `Node 12`
- `Feature image`
- temporary/non-English development labels when the template is published in English.

Generic names are acceptable for Sticky Note nodes because the visible sticky content is what users read.

### 5. Sticky-note architecture

Use the proven Creator pattern unless current official guidance says otherwise.

#### Main sticky
Place one overview sticky near the upper-left/start of the workflow.

Internal standard:
- default/yellow main sticky;
- clear workflow title;
- `### How it works`;
- `### Setup steps`;
- `### Customization`.

The main sticky may be longer than section stickies, but it must remain scannable. Do not turn it into a full manual.

Do not add a `What it does` section by default when `How it works` already explains the workflow.

#### Section stickies
Create section stickies for logical workflow stages, not mechanically for every node.

Internal proven pattern:
- white section sticky (`color: 7`) when compatible with current n8n rendering;
- `## <specific stage title>`;
- one concise, specific description of what that block does.

Good:
`## Check existing draft`

`Looks up WordPress by slug and branches based on whether a matching post already exists.`

Bad:
- vague text such as “Processes the data”;
- implementation essays;
- repeated setup instructions;
- AI-generated walls of text;
- generic descriptions that could fit any workflow.

If a concept needs a long walkthrough, move it to the Creator description, installation documentation, or a short video rather than expanding every sticky.

### 6. Layout

- Preserve a clear left-to-right or otherwise obvious execution flow.
- Group section stickies around the nodes they describe.
- Avoid sticky-to-sticky overlap.
- Avoid placing the main sticky over functional nodes.
- After any rename/re-layout pass, recheck visual grouping.

Do not treat Creator Portal preview transformations for paid templates as changes to the actual stored workflow; n8n may generate a separate truncated/repositioned preview.

### 7. Community safety and sanitization

Before producing a public JSON, scan every node, parameter, setting, prompt, URL, code block, credential reference, webhook field, and metadata object.

Hard gate: do not ship:
- API keys or tokens;
- passwords or secrets;
- credential bindings from the user's instance;
- private email recipients;
- private spreadsheet/database IDs;
- `meta.instanceId`;
- private webhook IDs unless explicitly required and safe;
- client/private domains or brand-specific data when the template is intended to be generic;
- error-workflow IDs tied to the user's instance;
- hidden personal identifiers.

Use explicit placeholders where configuration is required, for example:
- `<__PLACEHOLDER_VALUE__Notification email address__>`
- `<__PLACEHOLDER_VALUE__WordPress posts REST endpoint, e.g. https://example.com/wp-json/wp/v2/posts__>`

For a community export, prefer:
`"meta": { "templateCredsSetupCompleted": false }`

Keep the workflow inactive unless current Creator instructions explicitly require otherwise.

### 8. Behavioral truthfulness

Documentation must match the workflow exactly.

Examples:
- If WordPress creates `status: draft`, describe it as creating a draft, not publishing.
- If the Sheet ends in `DraftReady`, do not call it `Published`.
- If AI runs only for high-fit leads, say so.
- If a notification is non-blocking (`continueRegularOutput`), do not imply the workflow fails when email fails.

Treat wording/behavior mismatches as hard failures because they mislead template users.

### 9. Production-quality checks

Creator formatting does not replace workflow engineering quality.

Check, where applicable:
- duplicate prevention / idempotency;
- retry behavior;
- API rate-limit awareness;
- bounded polling;
- partial side-effect state;
- safe resume/recovery behavior;
- validation before irreversible side effects;
- explicit empty-result handling;
- error behavior;
- sensitive data handling.

Do not add unconfirmed infrastructure or dependencies only to satisfy this checklist. Report gaps separately.

### 10. Pre-submit QA gates

A Creator candidate must pass all applicable HARD GATES:

- valid JSON;
- unique node IDs;
- unique node names;
- all connection sources resolve;
- all connection targets resolve;
- all explicit node-name references resolve;
- no secrets;
- no credential bindings;
- no private instance metadata;
- no unintended private identifiers;
- workflow behavior and documentation agree;
- public workflow title follows descriptive naming;
- public filename is a clean slug;
- functional nodes use descriptive names;
- sticky notes describe logical stages specifically;
- no sticky/sticky overlap;
- workflow is not accidentally active;
- current n8n guidance has been checked when possible.

For a documentation-only or rename-only pass, also require:
- same functional node IDs;
- same connection topology by functional node ID;
- no unintended changes to parameters or execution behavior.

Do not label the workflow “ready to submit” if a hard gate fails.

## Required response format when applying this skill

Use these headings when materially useful:

**FACTS**
What is directly observed in the workflow or current n8n guidance.

**ASSUMPTIONS**
Anything not confirmed.

**DECISIONS**
What will be changed and why.

**QA**
What passed, what failed, and whether the file is submission-ready.

Keep the user informed about any functional change. Never hide a change inside a “cleanup”.

## Output artifacts

When asked to prepare a submission, produce:
1. the Creator-ready `.json`;
2. a machine-readable QA report `.json`;
3. optionally a concise change report if functional/generalization changes were required.

Use a clean slug filename derived from the public workflow title.

## Dynamic rule

This skill is intentionally conservative, but not frozen.

If current n8n official guidance or a new direct reviewer message conflicts with this skill:
1. current official/direct reviewer guidance wins;
2. update the skill's evidence notes;
3. preserve old accepted patterns as historical evidence, not current law.
