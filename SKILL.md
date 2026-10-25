---
name: quant-trading-model-doc
description: This skill should be used when the user asks to "write a quant model doc", "document this option model", "update the model document", "define the model spec", or before any change to model formulas, calibration parameters, data windows, filters, or fallback rules. Not for generic software engineering design docs, PRDs, API docs, or architecture reviews.
---

# Quant Trading Model Documentation

This skill helps write concise project documentation for option quant trading models.

The goal is not to produce a software engineering design document. The goal is to make the model reproducible, reviewable, and safe to operate.

## Core principle

Document only what affects model output, trading interpretation, fallback behavior, or reproducibility.

Avoid generic sections such as:
- system architecture
- non-functional requirements
- security design
- deployment strategy
- stakeholder mapping
- exhaustive edge-case speculation

Include them only if the user explicitly asks.

## Gate

<HARD-GATE>
No model-affecting change is made until the user approves the document
covering it in this conversation.

Model-affecting includes: editing model code, formulas, calibration
parameters, filters, weighting, bounds, data windows, or fallback rules;
adding or removing an input field; changing an output's meaning, unit, or
scaling; scaffolding a new model project.

Not model-affecting: reading code and documents, running read-only queries,
exploratory backtests and calibration runs, reproducing an existing result
unchanged, profiling, logging, formatting, and refactoring that leaves model
output unchanged.

Refactoring claimed to leave output unchanged requires evidence: state the
input sample and show the outputs match. An unverified claim is
model-affecting.

Two exceptions:
- The user explicitly opts out. The gate closes with the skill for that request.
- The user approves an exploratory run. It stays labelled throwaway; keeping
  any part of it is a new request that returns through this gate.

After approval, hand back to the normal development workflow.
</HARD-GATE>

### Red flags

| Thought | Reality |
|---|---|
| "Let me just run it and see" | Exploring is free. Scratch and notebook code is free. The moment production model code changes, the gate applies. |
| "This change is small" | Size decides how much to write, not whether to pass the gate. All three sizes pass it. |
| "The backtest Sharpe looks great" | Clean section 6 first. A result obtained with data unavailable at prediction time is not a result. |
| "This fallback will never fire" | If it cannot fire, delete it. If it can, state the trigger. A rule nobody has seen fire is undocumented, not safe. |
| "This refactor doesn't change anything" | Then show it: name the input sample and show the outputs match. Accumulation order, index alignment, and interpolation endpoints all move numbers silently. |

## Size the Work

| Size | What to write |
|---|---|
| Parameter tweak | Update the affected fields only |
| Model change | Update every affected section |
| New model | The full structure below |

After any change, re-check sections 6 and 7. Changed bounds move the rejected-fit trigger; a changed lookback or as-of rule moves the information boundary. Both fail silently.

A change includes its deletions. Removing an input, a tenor, an output, or a fallback trigger removes every row, rule, and mapping entry that described it. The document describes the model as it is now, not everything it has ever been.

If the work grows mid-task, say so and step up a size.

The gate applies at every size.

## Workflow

### 1. Discover

Inspect existing code and documentation before drafting. Identify every direct upstream, downstream, referencing, and related document; where this project stores its model documents; the source of truth for each model fact; every namespace in use, every external name the project does not control, and every project-controlled name that violates its namespace convention; and every finite-domain field.

Never speculate about a fact that affects model output, trading interpretation, fallback behavior, or reproducibility. Ask the user instead, and ask before implementing rather than after. For a fact outside that set, supply a default as `PROPOSED` rather than interrupting.

**Complete when:** every model fact is marked as fact, `PROPOSED`, or `TBD`; every output-affecting uncertainty has been asked rather than assumed; and every direct document relationship, namespace, external name, naming exception, and finite-domain field has been identified.

### 2. Document

Write the model document using the structure below, loading `references/document-structure.md` for the field contracts. Cover only facts that affect model output, trading interpretation, fallback behavior, or reproducibility.

Mark every fact in one of three states:

| State | Meaning | Form |
|---|---|---|
| Fact | Supported by the user, the code, or a source document | Written plainly |
| Proposed | Supplied as a default, not yet confirmed | `PROPOSED — <value>, <reason>` |
| Unknown | No basis to supply anything | `TBD` |

Never present a proposed value as a fact. A `PROPOSED` entry without a reason is not valid.

**Complete when:** every applicable section is populated, every finite domain has a complete contract, every project-controlled name follows its namespace convention or has a user-approved exception, and every cross-namespace concept has a Name Mapping entry.

### 3. Builder check

Run this check at the size of the change: skip it for a parameter tweak; for a model change, check the affected sections plus sections 6 and 7; for a new model, check the whole document.

Dispatch a fresh subagent to read the document as a quant who has never seen this project, using `references/builder-check-prompt.md`. The test is whether the model can be rebuilt from this document and its explicitly referenced authoritative contracts, and the section 8 results reproduced. Follow contract references as needed; facts recovered only from code remain documentation gaps.

Sort what it returns into three piles: already answered by the document or the project, put the answer in; minor enough that any competent reader would settle it the same way, settle it and mark it `PROPOSED`; and only the user can answer, bring those in one message. That is the only round of questions the check produces.

Without a subagent tool, read the document as that builder directly.

### 4. Validate

Run `scripts/check_doc.py <document>` first. It decides the mechanical items: missing sections, sections with no body, contract tables with no rows, links that do not resolve, and `PROPOSED` entries carrying no reason. Each proposal is checked within its own table cell or prose line; commas in other cells cannot supply its reason. Non-empty content does not establish semantic completeness. Clear every BLOCKING finding, and carry its OPEN list into step 5.

Then apply the Quality Gate below, which covers what no script can decide.

**Complete when:** the script reports no blocking findings and every Quality Gate item passes.

### 5. Request approval

Hand the document to the user and ask them to approve it. State what changed, list every `PROPOSED` value awaiting confirmation and every remaining `TBD`, and name any call made during the builder check.

Approval is given by the user in this conversation. A document that exists, is complete, or passed the builder check is not thereby approved.

**Complete when:** the user has approved the document. Until then the gate holds.

## Document structure

The document has eleven sections. Full field contracts, tables, and templates are in `references/document-structure.md`. Load it before writing or revising any section.

| # | Section | Covers |
|---|---|---|
| 0 | Document Topology | Direct upstream, downstream, and related documents; where the document is stored |
| 1 | Purpose | What the model produces and how the output is used |
| 2 | Data Inputs | Per-input contract; finite-domain declarations |
| 3 | Data Outputs | Per-output contract; signal, diagnostic, or chart-only |
| 4 | Model Definition | Formulas, variables, estimation target, constraints; Naming Contract |
| 5 | Calibration or Fitting Procedure | Sample, filters, weighting, objective, bounds, convergence, rejected fits |
| 6 | Prediction and Information Boundary | Data available at prediction time; owns the as-of date, same-day rule, and lookback window |
| 7 | Fallback Policy | Ordered deterministic rules, triggers, and user-visible behavior |
| 8 | Validation Examples | At least one worked example |
| 9 | Operational Notes | Only notes that change the result or its interpretation |
| 10 | Non-goals | What the document deliberately does not cover |

## Style rules

- Prefer tables for contracts.
- Prefer formulas for model logic.
- Prefer ordered fallback rules over prose.
- Keep explanations short unless the model assumption is non-obvious.
- Describe the model in the present tense. Do not record what it used to do, or why it changed; version control holds that.
- State each fact once, in the section that owns it, and cite that section elsewhere. A value repeated across sections will be updated in one of them and not the others.
- Do not add defensive engineering sections unless requested.
- If a detail is unknown, write `TBD` under the exact field instead of inventing assumptions. If a default is supplied, write `PROPOSED — <value>, <reason>`.
- If the user provides code and existing docs, extract facts from them before writing new content.

## Quality Gate

`scripts/check_doc.py` has already decided the mechanical items. Verify these by reading:

- Every direct document relationship is in Document Topology, and every editable related document has a reciprocal link.
- Every model concept has one authoritative name; every project-controlled name follows its namespace convention; every cross-namespace concept and every external name appears in the Name Mapping table; and every exception has explicit user approval.
- Every finite-domain field declares its complete allowed values and handling for null, empty, invalid, unknown, deprecated, and future values; every open domain has a validation rule.
- Formulas, time boundaries, calibration rules, and fallback behavior are supported by evidence or marked `TBD`.
- No unresolved fact is written plainly as a fact, and no proposed value is presented as a settled one.
- Sections 6 and 7 have been re-checked against the change just made.