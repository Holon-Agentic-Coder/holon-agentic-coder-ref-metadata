# GitHub Actions Workflows

This directory contains the CI/CD workflows for the `holon-agentic-coder-ref-metadata` control plane repository.

## Workflows

- `test-hygiene.yml`: Runs on pushes to `main`, pull requests targeting `main`, and manual dispatch on `ubuntu-latest`.
  It executes repository hygiene verification:
  - Markdown formatting check via Prettier (`npx prettier --check "**/*.md"`).
  - Internal markdown links and navigation integrity validation (`node .agents/scripts/validate-links.js`).

## Standards Alignment

All workflows in this repository conform to the standard Holon modular CI/CD architecture derived from
[`agentic-knowledge-base/.github`](https://github.com/thomashan/agentic-knowledge-base/tree/main/.github).
