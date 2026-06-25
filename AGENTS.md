# AGENTS.md

Harness-agnostic agent instructions for the study notes pipeline. This file is the source of truth. Each harness (Claude Code, Gemini, etc.) has its own thin wrapper that points here.

---

## Project Overview

This repo turns textbook PDFs into published study notes, one chapter at a time. The domain is **electric circuits and amateur radio** — expect dense mathematics, circuit schematics, block diagrams, and signal-processing concepts. An agent reads a chapter from a PDF, writes a summary in the house style below, produces 1–3 figures, updates the state files, updates the MkDocs nav, and auto-commits. On `git push`, a GitHub Action builds and deploys one MkDocs site per book to GitHub Pages.

---

## Repository Layout

```
books/<book-slug>/
  docs/
    index.md               # generated book index
    chNN-<slug>.md         # chapter summary files
    figures/               # .svg and .png figure files
  mkdocs.yml               # auto-updated nav
  requirements.txt         # mkdocs-material

sources/<book-slug>/       # GITIGNORED — PDF source files
  original.pdf

state/
  progress.md              # chapter status per book
  glossary.md              # accumulating key terms

.claude/                   # Claude Code harness files
.gemini/                   # Gemini harness files (future)
```

---

## Figure Decision Rule

Apply this rule when deciding how to represent a concept visually:

| Figure type | Tool | Output location |
|---|---|---|
| Circuit schematic or component layout | Hand-written SVG | `books/<slug>/docs/figures/<name>.svg` |
| Block diagram, signal flow, system architecture | Mermaid (inline) | Inline in the `.md` file |
| Process, sequence, tree, or relationship | Mermaid (inline) | Inline in the `.md` file |
| Cross-section or custom layout Mermaid cannot express | Hand-written SVG | `books/<slug>/docs/figures/<name>.svg` |
| Plot of real numeric data from the text | matplotlib PNG | `books/<slug>/docs/figures/<name>.png` |
| Decorative / banner / hero | Skip | — |

**Rules:**
- SVG and Mermaid are co-defaults for this domain. Use SVG for any circuit schematic (always); use Mermaid for flow and block diagrams.
- Math belongs inline as LaTeX (`$...$` or `$$...$$`), never as a figure.
- Never invent data to produce a chart. Only plot values explicitly stated in the source text.
- Aim for 1–3 figures per chapter. One accurate diagram beats three decorative ones.

---

## House Style for Chapter Summaries

Every chapter file must follow this structure:

1. **Orientation** (2–3 sentences): what this chapter is about and why it matters.
2. **Key ideas** as concise prose under short sub-headings, written in my own words — not the textbook's phrasing.
3. Every term defined on first use. Also add it to `state/glossary.md`.
4. Use callout blocks for things to remember:
   - `!!! note "..."` for important clarifications
   - `!!! warning "..."` for common mistakes or gotchas
5. Math in LaTeX: inline `$...$`, display `$$...$$`, rendered via MathJax.
6. **Key takeaways** section: 3–6 bullets summarising the chapter.
7. **Open questions** section: things to revisit or investigate further.

**Hard rules:**
- Do not paste verbatim extracts from the source. Paraphrase and condense.
- Do not reproduce copyrighted text.
- Keep the language direct and in first person where helpful ("the key insight here is…").

---

## Chapter-Notes Skill Steps

When `/summarize <book-slug> <chapter>` is triggered, execute these steps in order:

1. **Read the TOC.** Open `sources/<book-slug>/original.pdf` and read the first 5 pages to locate the table of contents and identify the start/end pages of the requested chapter. If the TOC is image-based or not machine-readable, ask the user for the page range before continuing.

2. **Extract the chapter.** Read the chapter pages in chunks of ≤20 pages, accumulating the full text before writing anything.

3. **Write the chapter summary.** Create `books/<book-slug>/docs/chNN-<slug>.md` with YAML front-matter and the summary in the house style above.

   Front-matter format:
   ```yaml
   ---
   title: "<Chapter Title>"
   chapter: <N>
   source: "<book-slug>"
   date: "<YYYY-MM-DD>"
   ---
   ```

4. **Produce figures.** Apply the figure decision rule. Write SVG and PNG files to `books/<book-slug>/docs/figures/`. Embed Mermaid diagrams inline in the `.md` file.

5. **Update the glossary.** Append any new terms to `state/glossary.md` as `**term** — one-line definition`. Keep the list sorted alphabetically and de-duplicated.

6. **Update progress.** In `state/progress.md`, mark the current chapter as `done` and the next chapter as `in progress` (if it exists).

7. **Update MkDocs nav.** Add the new chapter file to the `nav:` section of `books/<book-slug>/mkdocs.yml` in chapter order.

8. **Auto-commit.** Stage all changed and new files, then commit with the message:
   ```
   docs(<book-slug>): add ch<NN> — <chapter title>
   ```

---

## State File Formats

### `state/progress.md`

One table per book:

```markdown
## <book-slug>

| Chapter | Title | Status      | Notes |
|---------|-------|-------------|-------|
| 1       | ...   | done        |       |
| 2       | ...   | in progress |       |
| 3       | ...   | queued      |       |
```

Valid status values: `done`, `in progress`, `queued`.

### `state/glossary.md`

Alphabetically sorted list, one term per line:

```markdown
**term** — one-line definition
```

No duplicates. If a term already exists, do not add it again.

---

## Commit Message Convention

| Action | Format |
|---|---|
| New chapter | `docs(<book-slug>): add ch<NN> — <chapter title>` |
| Register new book | `chore: register <book-slug> as new source` |
| Manual fix | `fix(<book-slug>): <short description>` |

---

## Renderer Portability Note

Content is plain Markdown. The only renderer-specific syntax used is:
- Admonition blocks (`!!! note`, `!!! warning`) — MkDocs Material syntax
- `mkdocs.yml` per book

If the renderer changes, update admonition syntax and replace `mkdocs.yml` per book. All other content (Markdown, SVG, PNG) is portable.
