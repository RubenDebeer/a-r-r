# Skill: chapter-notes

Summarise one chapter from a textbook PDF, produce figures, update state, and auto-commit.

---

## Inputs

- `book-slug` — identifies the book under `sources/` and `books/`
- `chapter` — chapter number or title string

---

## Step 1 — Read the Table of Contents

Open `sources/<book-slug>/original.pdf` and read pages 1–5 using the PDF read tool.

- Locate the table of contents.
- Identify the **start page** and **end page** of the requested chapter.
- If the TOC is image-based, not present, or the chapter boundaries are ambiguous, **stop and ask the user** for the exact page range before continuing.

---

## Step 2 — Extract the Chapter Text

Read the chapter in chunks of **≤20 pages** at a time, accumulating the full text.

- Keep track of which pages have been read.
- Continue until the full chapter is extracted.
- Do not begin writing until the full chapter text is in hand.

---

## Step 3 — Write the Chapter Summary

Determine the chapter number (`NN`, zero-padded to two digits) and a short kebab-case slug from the chapter title.

Create the file `books/<book-slug>/docs/chNN-<slug>.md`.

**Front-matter:**
```yaml
---
title: "<Full Chapter Title>"
chapter: <N>
source: "<book-slug>"
date: "<YYYY-MM-DD>"
---
```

**Body — follow the house style in `AGENTS.md`:**
1. Orientation paragraph (2–3 sentences).
2. Key ideas under short sub-headings, in your own words.
3. Every term defined on first use.
4. Admonition blocks (`!!! note`, `!!! warning`) for things to remember.
5. LaTeX for all mathematics (`$...$` inline, `$$...$$` display).
6. Figures embedded inline (Mermaid) or referenced by filename (SVG/PNG).
7. **Key takeaways** section (3–6 bullets).
8. **Open questions** section.

Do not reproduce verbatim passages from the source.

---

## Step 4 — Produce Figures

Apply the figure decision rule from `AGENTS.md`. Target 1–3 figures per chapter.

**SVG figures** (circuit schematics and layouts that Mermaid cannot express):
- Write to `books/<book-slug>/docs/figures/chNN-<figure-name>.svg`
- Reference in the markdown: `![<caption>](figures/chNN-<figure-name>.svg)`

**Mermaid diagrams** (block diagrams, signal flow, process diagrams):
- Embed inline using a fenced code block:
  ````
  ```mermaid
  graph LR
    ...
  ```
  ````

**matplotlib PNG** (real numeric data from the text only):
- Write Python to `books/<book-slug>/docs/figures/chNN-<figure-name>.py`, execute it, save the PNG output to `books/<book-slug>/docs/figures/chNN-<figure-name>.png`
- Reference in the markdown: `![<caption>](figures/chNN-<figure-name>.png)`
- Never invent data.

**Math** — always inline LaTeX, never a figure.

---

## Step 5 — Update the Glossary

Read `state/glossary.md`.

For each term defined in the chapter summary:
- If the term does not already exist in the glossary, append it as:
  ```
  **<term>** — <one-line definition>
  ```
- Keep the list alphabetically sorted.
- Do not duplicate existing entries.

---

## Step 6 — Update Progress

Read `state/progress.md`.

- Find the table for `<book-slug>`.
- Set the current chapter row status to `done`.
- If a row for the next chapter exists, set it to `in progress`.
- If the next chapter row does not exist yet, add it with status `queued`.

---

## Step 7 — Update MkDocs Nav

Read `books/<book-slug>/mkdocs.yml`.

Add the new chapter to the `nav:` section in chapter order:
```yaml
nav:
  - Home: index.md
  - Chapter 1 — <Title>: ch01-<slug>.md
  - Chapter 2 — <Title>: ch02-<slug>.md   # newly added
```

---

## Step 8 — Auto-Commit

Stage all new and modified files:
- `books/<book-slug>/docs/chNN-<slug>.md`
- `books/<book-slug>/docs/figures/*` (any new figures)
- `books/<book-slug>/mkdocs.yml`
- `state/progress.md`
- `state/glossary.md`

Commit with the message:
```
docs(<book-slug>): add ch<NN> — <chapter title>
```

Do not push. Print the commit hash and a one-line summary of what was produced.
