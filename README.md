# Quant Trading Model Doc

An Agent Skill for writing and maintaining options trading model documentation. It makes model inputs, outputs, formulas, calibration procedures, information boundaries, and fallback rules explicit and reproducible.

Use it to document a new model, fill gaps in existing documentation, or update documentation when model parameters or logic change.

[Source on GitHub](https://github.com/LiuXilin-Frankie/quant-trading-model-doc)

## Installation

Run this command from your project directory:

```bash
npx skills add LiuXilin-Frankie/quant-trading-model-doc
```

Add `-g` to install at the user level and use the skill across projects.

## Usage Examples

After installation, ask your agent to:

- "Document this option pricing model based on the existing code."
- "I want to change the model's calibration window. Update the affected documentation first."
- "Check whether another person could reproduce this model from its documentation."

## How It Works

- Reads existing code and documentation, distinguishing confirmed facts, proposed values, and unknowns.
- Updates documentation in proportion to the change, with particular attention to information boundaries and fallback rules.
- Checks documentation completeness and lists items that need confirmation.
- Requests approval of the relevant documentation before changing code that affects model results. Users can explicitly opt out of this approval step.

This skill does not execute trades. Documentation completeness does not establish model correctness.

## Requirements

- **Installation:** Node.js 22.20 or later and npm, which provides `npx`.
- **Usage:** An AI coding tool that supports Agent Skills.
- **Document validation:** Python 3, with no third-party Python packages required.

## Document Validation

From a clone of this repository, run:

```bash
python3 scripts/check_doc.py /path/to/model-document.md
```

The checker reports missing or empty sections, empty tables, broken local file links, and proposed values without reasons. It also lists unresolved items for review. It does not verify formulas or model correctness.

## License

Licensed under the [MIT License](LICENSE).
