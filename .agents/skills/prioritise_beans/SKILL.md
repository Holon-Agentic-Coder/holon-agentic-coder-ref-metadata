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
| `--dry-run`   | Print generated Markdown to stdout without writing to disk | `false`                                |

### Post-Generation Hygiene

After running the generator, always format markdown files with Prettier:

```bash
npx prettier --write ".beans/bean-triage-prioritisation.md"
```

### Generator Maintenance (Required, Not Optional)

`scripts/prioritise_beans.py` carries the Executive Summary lead-in and the **Key Milestones Completed** narrative as
inline data. The generator will happily emit that narrative verbatim, so a run that only refreshes the statistics ships
a stale history. Every run MUST therefore:

1. Add the newly completed beans to the milestones narrative (numbered items 1..N) and bump the
   `Key Milestones Completed (Beans AAAA – BBBB)` heading range.
2. Add or refresh an entry in the `overrides` map for each bean that stays active, so its Impact / Sizing / Domain /
   Notes cells read as a triage judgement rather than a truncated first paragraph.
3. Nest milestone sub-bullets under items 10 and above with **four** spaces of indent (the ordered-item content column
   is 4 characters wide from `10.` onwards); three spaces makes Prettier detach the bullets into a loose sibling list.
4. Reformat the script with the repository's own configuration and run the harness tests:
   ```bash
   uvx ruff format .agents/skills/prioritise_beans/scripts/prioritise_beans.py
   uvx ruff check .agents/skills/prioritise_beans/scripts/prioritise_beans.py
   uv run pytest -q
   ```

The `**Last Updated:**` date of the pre-existing document is read back and reported as the previous triage checkpoint,
so regenerate once per checkpoint — a second run on the same day reports that same day as the previous checkpoint.
