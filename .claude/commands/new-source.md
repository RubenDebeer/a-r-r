Register a new textbook PDF and scaffold its book directory.

Arguments: $ARGUMENTS
(Format: <pdf-path> <book-slug>, e.g. "/path/to/file.pdf my-book")

Steps:
1. Verify the PDF exists at the given path. If it does not exist, stop and tell the user.
2. Create `sources/<book-slug>/` and copy the PDF to `sources/<book-slug>/original.pdf`.
3. Create `books/<book-slug>/docs/figures/`, `books/<book-slug>/requirements.txt`, `books/<book-slug>/mkdocs.yml`, and `books/<book-slug>/docs/index.md`.
4. Write `books/<book-slug>/requirements.txt` containing just `mkdocs-material`.
5. Write `books/<book-slug>/mkdocs.yml` using the standard MkDocs Material template with Mermaid and MathJax enabled, site_name set to "<book-slug> — Study Notes", and nav containing only `Home: index.md`.
6. Write a placeholder `books/<book-slug>/docs/index.md`.
7. Add a new section to `state/progress.md` for this book with an empty chapter table.
8. Auto-commit: `chore: register <book-slug> as new source`.
9. Confirm what was created and remind the user to run `/summarize <book-slug> 1`.
