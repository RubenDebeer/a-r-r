# Study Notes Pipeline — Project Spec

A personal, git-backed knowledge base for turning textbook PDFs into clean,
published study notes — one chapter at a time — managed through Claude Code.

This document is the build brief. Drop it at the repo root as `SPEC.md` and
point Claude Code at it to scaffold and build the project.

---

## 1. Goal

Upload a textbook PDF. As I work through it chapter by chapter, an agent:

1. Reads the PDF table of contents to infer chapter boundaries,
2. Extracts the target chapter in chunks (respecting context-window limits),
3. Writes a summary in my own house style as Markdown,
4. Produces 1–3 figures **as code** (Mermaid, hand-written SVG, or plotted PNG),
5. Files everything into the repo, updates a small progress/glossary state,
   updates `mkdocs.yml` nav, and **auto-commits**.

On `git push`, a GitHub Action builds a static site and publishes it to
GitHub Pages — one site per book.

## 2. Domain

These notes cover **electric circuits and amateur radio concepts**. The source
material is math-, science-, and engineering-heavy. Expect:

- Dense LaTeX: Ohm's law, Kirchhoff's laws, impedance, Fourier analysis, etc.
- Circuit schematics as first-class content (not edge cases).
- Block diagrams: receiver chains, modulation stages, signal flow.
- Occasional real numeric data worth plotting.

## 3. Non-goals (scope guards — do not drift into these)

- **No raster image generation by default.** Figures are diagram-as-code
  (Mermaid/SVG) or, for real data, a plotted PNG. AI-generated illustrations
  are only ever wired in later, explicitly, for decorative banners — never for
  anything that has to be *correct*.
- **No publishing of copyrighted source text.** Summaries are my own condensed
  words, not reproduced passages. The PDF itself is never committed (see §11).
- **No heavy "current state" memory model.** Study notes are append-only; this
  is not the fishtank tank-census problem. Keep the state layer thin (§9).
- **No CI-side generation.** All summarising and figure-making happens locally
  in Claude Code. The Action only *builds and deploys* files that already exist.

## 4. How it works

```
PDF chapter
   → Claude Code skill (summarise + draw figure)   [local]
   → Markdown + SVG written into the repo           [local]
   → mkdocs.yml nav updated                         [local]
   → auto-commit                                    [local]
   → git push                                       [local → GitHub]
   → GitHub Action builds the static site           [GitHub]
   → GitHub Pages serves it                         [GitHub]
```

The boundary is `git push`: everything left of it runs on my machine, where the
model and any tooling live; everything right of it is plain CI with no secrets
and no model access.

## 5. Repository layout

```
study-notes/
├── SPEC.md                         # this file
├── AGENTS.md                       # harness-agnostic agent instructions (§8)
├── CLAUDE.md                       # thin Claude Code wrapper — reads AGENTS.md
├── .claude/                        # Claude Code-specific files
│   ├── commands/
│   │   ├── summarize.md            # /summarize <book> <chapter>
│   │   ├── status.md               # /status
│   │   └── new-source.md           # /new-source <pdf>
│   └── skills/
│       └── chapter-notes/
│           └── SKILL.md            # the summarise + figure skill (§7)
├── .gemini/                        # placeholder for Gemini harness (future)
├── sources/                        # uploaded PDFs — GITIGNORED
│   └── <book-slug>/original.pdf
├── books/                          # one MkDocs site per book
│   └── <book-slug>/
│       ├── docs/
│       │   ├── index.md            # generated book index
│       │   ├── ch01-<slug>.md
│       │   ├── ch02-<slug>.md
│       │   └── figures/            # committed .svg and .png files
│       ├── mkdocs.yml              # auto-updated nav on each chapter commit
│       └── requirements.txt
├── state/                          # thin "what's true now" layer
│   ├── progress.md                 # chapters: done / in progress / queued
│   └── glossary.md                 # key terms accumulated across chapters
└── .github/workflows/
    └── deploy.yml                  # builds + deploys all books on push to main
```

**Harness philosophy:** `AGENTS.md` is the source of truth for agent behaviour.
It is harness-agnostic. Each harness gets its own directory (`.claude/`,
`.gemini/`, etc.) and a thin root-level config file (`CLAUDE.md`, etc.) that
simply instructs the harness to read `AGENTS.md`.

## 6. Core design decisions (and why)

- **Figures are code, not pictures.** Mermaid/SVG are accurate, editable,
  diff cleanly in git, and render natively on Pages. A generated raster diagram
  would happily mislabel a circuit node or garble axis text — worse than no
  figure when the goal is learning.
- **Chapter-by-chapter chunking.** A whole textbook overflows the context
  window; one chapter is the natural, reliable unit of work. The skill reads
  the TOC first to infer boundaries, then reads the chapter in page-range chunks.
- **Thin state layer.** Only two state files. A chapter summary doesn't change
  when the next chapter arrives, so there's no mutable-snapshot tier to maintain.
- **Local generation, dumb CI.** Keeps API keys (if any are ever added) off
  GitHub and makes the Action a pure, secret-free build step.
- **One site per book.** Each book is an independent MkDocs site under
  `books/<book-slug>/`. The deploy workflow loops over all books and deploys
  each to its own GitHub Pages path.
- **Auto-commit.** After a successful chapter run the skill stages and commits
  all changes (chapter `.md`, figures, `progress.md`, `glossary.md`,
  `mkdocs.yml`). The user reviews via `git log` and pushes when ready.

## 7. Figure decision rule (the skill must follow this)

| If the figure is…                                        | Use              | Output                  |
|----------------------------------------------------------|------------------|-------------------------|
| A circuit schematic or component layout                  | Hand-written SVG | `figures/*.svg`         |
| A process, block diagram, sequence, or signal flow       | Mermaid          | inline in the `.md`     |
| A cross-section / custom layout Mermaid can't express    | Hand-written SVG | `figures/*.svg`         |
| A plot of real numeric data                              | matplotlib       | committed `*.png`       |
| Decorative only (banner, hero)                           | skip by default  | —                       |

For this domain (electric circuits, amateur radio):
- **SVG and Mermaid are co-defaults.** Use SVG for circuit schematics (always);
  use Mermaid for block diagrams and flow diagrams.
- Never invent data to make a chart.
- Math goes inline as LaTeX (`$...$` / `$$...$$`), never as a figure.

## 8. The `chapter-notes` skill

**Trigger:** `/summarize <book-slug> <chapter>` (or natural language: "summarise
chapter 4 of <book>").

**Inputs:** the source PDF at `sources/<book-slug>/original.pdf`, a chapter
identifier (number or title).

**Steps:**
1. Read the PDF table of contents to identify chapter boundaries (start/end
   pages). If the TOC is not machine-readable, ask the user for the page range.
2. Extract the target chapter in chunks of ≤20 pages, accumulating the full
   text before writing.
3. Write a summary in the house style (§9) to
   `books/<book-slug>/docs/chNN-<slug>.md`, with YAML front-matter
   (`title`, `chapter`, `source`, `date`).
4. Decide on 1–3 figures using the rule in §7; embed Mermaid inline and/or
   write SVG/PNG files to `books/<book-slug>/docs/figures/`.
5. Append any new key terms (term + one-line definition) to
   `state/glossary.md`, de-duplicating.
6. Update `state/progress.md` (mark this chapter done; note what's next).
7. Update `books/<book-slug>/mkdocs.yml` nav to include the new chapter.
8. Stage all changes and **auto-commit** with a message in the form:
   `docs(<book-slug>): add ch<NN> — <chapter title>`.

**Outputs:** one Markdown chapter file, zero or more SVG/PNG figures, updated
`progress.md`, `glossary.md`, and `mkdocs.yml`.

## 9. House style for summaries (lives in AGENTS.md)

- Lead with a 2–3 sentence "what this chapter is about" orientation.
- Then the key ideas as concise prose with short sub-headings — explanations in
  my own words, not the textbook's phrasing.
- Define every term on first use; also add it to the glossary.
- End each chapter with: "Key takeaways" (3–6 bullets) and "Open questions"
  (things to revisit).
- Use callout blocks (`!!! note`, `!!! warning`) for things to remember.
- Math in LaTeX (`$...$` / `$$...$$`), rendered via MathJax.
- Keep figures few and meaningful — one good diagram beats three decorative ones.
- Do not paste verbatim extracts from the source. Paraphrase and condense.

## 10. State files

`state/progress.md` — a simple table per book:

```
| Chapter | Title | Status      | Notes |
|---------|-------|-------------|-------|
| 1       | ...   | done        |       |
| 2       | ...   | in progress |       |
| 3       | ...   | queued      |       |
```

`state/glossary.md` — accumulating `**term** — one-line definition`, sorted,
de-duplicated. This is the only thing that "grows" across chapters.

## 11. Publishing (MkDocs Material + GitHub Pages)

Each book lives at `books/<book-slug>/`. Its `requirements.txt`:
```
mkdocs-material
```

`mkdocs.yml` (essentials — the skill fills in nav and `site_name`):
```yaml
site_name: <Book Title> — Study Notes
theme:
  name: material
  features: [navigation.sections, navigation.top, content.code.copy]
markdown_extensions:
  - admonition
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.arithmatex:
      generic: true
extra_javascript:
  - https://unpkg.com/mermaid/dist/mermaid.min.js
  - https://polyfill.io/v3/polyfill.min.js?features=es6
  - https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js
```

`.github/workflows/deploy.yml` — on push to `main`, loop over all
`books/*/mkdocs.yml`, build each, and deploy to GitHub Pages under a subpath
per book. No model and no API secrets required. Pin to the latest stable action
versions at build time.

## 12. Copyright & privacy

- `sources/` is gitignored so the textbook PDF is never published.
- The repo is public; published summaries must be genuine condensations in my
  own words — not reproduced paragraphs. The skill must refuse to paste long
  verbatim extracts.
- Add `sources/`, `site/`, and `__pycache__` to `.gitignore` in Phase 0.

## 13. Build plan

**Phase 0 — scaffold**
- Create the folder tree (§5), write `AGENTS.md` from §6, §7, §9.
- Write `CLAUDE.md` as a thin wrapper: "Read `AGENTS.md` for all instructions."
- Write the three slash commands and `chapter-notes/SKILL.md`.
- Write `.gitignore`.

**Phase 1 — one chapter, end to end**
- Put one real PDF in `sources/<book>/original.pdf`.
- Run `/summarize <book> 1`; verify the `.md`, at least one figure, and state
  updates look right.
- Stand up `books/<book>/mkdocs.yml` + `requirements.txt`; `mkdocs serve`
  locally and confirm the chapter, Mermaid, math, and SVG figures all render.
- Add `deploy.yml`; push; confirm the chapter is live on Pages.

**Phase 2 — polish**
- Generated `books/<book>/docs/index.md` book index from `progress.md`.
- `/status` summarises progress across all books.
- `/new-source` registers a new book and scaffolds its `books/<book-slug>/`
  directory.
- Tune the house style on a second chapter.

## 14. Definition of done (v1)

- `/summarize <book> <n>` produces a correctly-styled chapter `.md` with at
  least one accurate Mermaid or SVG figure, updates `progress.md`,
  `glossary.md`, and `mkdocs.yml`, and auto-commits.
- `git push` triggers a build that publishes the new chapter to GitHub Pages
  with working Mermaid diagrams, rendered math, and inline SVG figures.
- No PDF or verbatim copyrighted text is published.
- The CI workflow holds no secrets.
