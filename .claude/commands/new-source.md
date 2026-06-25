# /new-source

Register a new textbook PDF and scaffold its book directory.

**Usage:** `/new-source <pdf-path> <book-slug>`

- `<pdf-path>` — absolute or relative path to the PDF on the local filesystem
- `<book-slug>` — short lowercase kebab-case identifier for this book (e.g. `arrl-handbook`)

**What to do:**

1. Verify the PDF exists at `<pdf-path>`. If it does not exist, stop and tell the user.
2. Create `sources/<book-slug>/` and copy the PDF to `sources/<book-slug>/original.pdf`.
3. Create the following directory structure:
   ```
   books/<book-slug>/
     docs/
       figures/
     requirements.txt
     mkdocs.yml
   ```
4. Write `books/<book-slug>/requirements.txt`:
   ```
   mkdocs-material
   ```
5. Write `books/<book-slug>/mkdocs.yml` with the standard template:
   ```yaml
   site_name: <book-slug> — Study Notes
   theme:
     name: material
     features:
       - navigation.sections
       - navigation.top
       - content.code.copy
   docs_dir: docs
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
   nav:
     - Home: index.md
   ```
   Replace `<book-slug>` in `site_name` with the actual slug formatted as a readable title.
6. Write `books/<book-slug>/docs/index.md` as a placeholder:
   ```markdown
   # <book-slug>

   Study notes generated chapter by chapter. See progress in `state/progress.md`.
   ```
7. Add a new section to `state/progress.md` for this book with an empty table.
8. Auto-commit all new files:
   ```
   chore: register <book-slug> as new source
   ```
9. Print a confirmation showing the paths created and remind the user to run `/summarize <book-slug> 1` to begin.
