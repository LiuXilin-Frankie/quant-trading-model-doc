# Document Structure

The required structure for a quant model document. Load this before writing or
revising any section. Section 6 owns the as-of date, the same-day rule, and the
lookback window; other sections cite it rather than restating them.


## 0. Document Topology

List every direct document relationship:

| Relationship | Document | Relevant Section | Purpose |
|---|---|---|---|

- Use `Upstream` for specifications this document consumes, `Downstream` for documents that depend on it, `References this document` for citations without dependency, and `Related` for material peer relationships.
- Identify the source of truth for each model, data, and calibration contract. Link to an authoritative contract instead of duplicating it.
- Add reciprocal links: `Upstream` ↔ `Downstream`; `References this document` and `Related` ↔ `Related`. If a related document cannot be edited, record its path and reason as `TBD`.
- Include direct relationships only.
- Store a new model document where this project already stores its model documents. When no convention exists, ask before choosing a location.
- Use GitLab-resolvable relative Markdown links for repository documents. Resolve each target from the directory of the document containing the link, remove its anchor before checking, and confirm the target file exists.
- Derive each reciprocal link independently from its own source document directory; do not infer it by reversing another relative path.

## 1. Purpose

Explain what the model produces and how the output is used.

Keep this section short. Do not write business background unless it changes model interpretation.

## 2. Data Inputs

For each input, specify:

| Field | Meaning | Source | Granularity | Time convention | Required | Missing handling |
|---|---|---|---|---|---|---|

Always clarify, per field:
- timezone
- tenor definition
- moneyness or strike bucket definition
- units and scaling

Section 6 owns the as-of date, the same-day rule, and the lookback window. Record each input's own time convention here and cite section 6 for the boundary itself.

For each finite-domain field, including statuses, categories, enums, flags, option types, tenors, moneyness buckets, instrument categories, model versions, and fallback reasons, declare:
- the complete allowed-value set and meaning of every value
- handling for null, empty, invalid, unknown, deprecated, and future values
- whether each exceptional value enters model calculation or triggers fallback

Examples are not a complete domain. Mark a non-finite field as `Open domain` and define its validation rule.

## 3. Data Outputs

For each output, specify:

| Output | Meaning | Type | Unit | Consumer | Persisted | Used for trading decision |
|---|---|---|---|---|---|---|

State whether the output is:
- final signal
- diagnostic metric
- chart-only value
- intermediate value that should not be persisted

Apply the same finite-domain contract to output statuses, model states, diagnostic flags, prediction categories, and fallback reasons. State whether unknown values may reach downstream consumers and the user-visible behavior of each state.

## 4. Model Definition

Write the model in mathematical form.

For every formula:
- define all variables
- state the estimation target
- state constraints
- state objective function if fitting is used
- state whether the formula is per-date, per-tenor, per-underlying, or cross-sectional

Use LaTeX-style notation when useful.

#### Naming Contract

Record the user-selected naming convention for each affected namespace. Apply it to new or renamed variables. Preserve existing identifiers when documenting unchanged code, and retain external interface and data-source names verbatim.

- Use one authoritative concept name across formulas, code, configuration, data, artifacts, and display labels. Rendering that name in a namespace's own convention is not an alias.
- Provide a Name Mapping table for every concept that appears in more than one namespace. Translation must be mechanical: `asOfDate` ↔ `as_of_date` ↔ $t_0$ ↔ "As-of date".
- Define abbreviations, units, and suffixes consistently. Do not introduce an undeclared alias.
- Record external names — vendor feed columns, exchange fields, upstream schemas — in the Name Mapping table beside the corresponding project names.

## 5. Calibration or Fitting Procedure

Specify:
1. input sample selection
2. filtering rules
3. weighting scheme
4. optimization target
5. parameter bounds
6. convergence rule
7. rejected fit handling

If fitting uses a most liquid tenor, explicitly describe how that tenor is selected and how results are extrapolated to other tenors.

## 6. Prediction and Information Boundary

State clearly what information is allowed at prediction time.

This section owns the as-of date, the same-day rule, and the lookback window. Other sections cite it rather than restating them.

Use this template:

- Prediction date:
- Allowed data:
- Forbidden data:
- Lookback window:
- Same-day data allowed: yes/no
- If no, latest allowed as-of:
- Reason:

This section is mandatory whenever any parameter is estimated from historical data, whether or not the output is presented as a prediction.

## 7. Fallback Policy

Fallback must be written as ordered rules.

Use this structure:

| Priority | Trigger | Action | Output flag | User-visible behavior |
|---|---|---|---|---|

Rules must be deterministic.

Examples of fallback triggers:
- insufficient valid observations
- failed fit
- parameter outside bounds
- stale input data
- missing tenor
- no previous valid model state

Do not write vague fallback language such as "handle gracefully".

## 8. Validation Examples

Include at least one minimal example.

The example should specify:
- input rows
- expected output shape
- one expected numeric or qualitative result
- one fallback case if relevant

## 9. Operational Notes

Only include operational notes that affect model result or user interpretation.

Examples:
- chart interpretation
- known unstable regions
- report display caveats
- manual override convention

## 10. Non-goals

List what this document intentionally does not cover.

This prevents the document from expanding into a generic software engineering spec.
