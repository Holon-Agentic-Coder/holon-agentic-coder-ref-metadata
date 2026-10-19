---
name: prioritise-beans
description:
  Scans, triages, and prioritises beans across the Holon ecosystem, computing completion progress statistics, excluding
  all completed and scrapped beans, and generating/updating the standardized Active Beans Triage and Prioritisation
  Matrix in .beans/bean-triage-prioritisation.md. Activate this skill whenever the user asks to triage, prioritise,
  rank, or organize beans, or update the active beans matrix.
---

# Prioritise Beans Skill (`prioritise-beans`)

This skill provides an automated workflow to audit, triage, and prioritise all beans in `.beans/`, calculate milestone
completion statistics, and generate a clean, Unix-standard Active Beans Triage and Prioritisation Matrix in
`.beans/bean-triage-prioritisation.md`.

---

## 🎯 Core Invariants & Rules

1. **Exclusion of Completed & Scrapped Beans**:
   - Beans with `status: completed` or `status: scrapped` are **strictly excluded** from the active triage matrix table.
   - They are accounted for exclusively in the Executive Summary statistics and Key Milestones Completed sections.

2. **Clean 4-Digit Bean Numbers**:
   - The matrix table MUST display clean 4-digit bean numbers (`0116`, `0113`, etc.) under the `Bean #` column.
   - Bulky `file:///.../holon-agentic-coder-ref-metadata-XXXX--*.md` links or full filenames are strictly prohibited in
     table cells.

3. **Standardized Column Layout**:
   - The table columns MUST follow this exact sequence:
     ```markdown
     | Priority | Status | Impact | Sizing | Bean # | Title | Domain | Dependencies / Notes |
     ```

4. **Zero Synthetic Benchmarks & Data**:
   - All statistics, metrics, and estimates derive directly from authentic filesystem state in `.beans/`.

---

## 🚀 Execution Workflow

To run the automated bean prioritisation script:

```bash
python3 .agents/skills/prioritise_beans/scripts/prioritise_beans.py
```

### CLI Flags

| Flag          | Description                                                | Default                                |
| :------------ | :--------------------------------------------------------- | :------------------------------------- |
| `--beans-dir` | Directory containing bean markdown files                   | `.beans`                               |
| `--output`    | Explicit output file path                                  | `.beans/bean-triage-prioritisation.md` |
| `--date`      | Target date string (`YYYY-MM-DD`) for title                | Today's UTC date                       |
| `--dry-run`   | Print generated Markdown to stdout without writing to disk | `false`                                |

### Post-Generation Hygiene

After running the generator, always format markdown files with Prettier:

```bash
npx prettier --write ".beans/bean-triage-prioritisation.md"
```
