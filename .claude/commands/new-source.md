Register a new textbook PDF and scaffold its book directory.

Arguments: $ARGUMENTS
(Format: <pdf-path> <book-slug>, e.g. "/path/to/file.pdf my-book")

Steps:
1. Verify the PDF exists at the given path. If it does not exist, stop and tell the user.
2. Create `sources/<book-slug>/` and copy the PDF to `sources/<book-slug>/original.pdf`.
3. Create the following directories and files:
   - `books/<book-slug>/docs/figures/` (directory)
   - `books/<book-slug>/docs/index.md` (placeholder)
   - `books/<book-slug>/book.yml` (nav manifest)
4. Write `books/<book-slug>/book.yml` with this format:
   ```yaml
   site_name: <book-slug> — Study Notes
   nav:
     - Home: index.md
   ```
   Do NOT create `mkdocs.yml` or `requirements.txt` — the build system no longer uses MkDocs.
5. Write a placeholder `books/<book-slug>/docs/index.md`:
   ```markdown
   # <book-slug> — Study Notes

   Study notes generated chapter by chapter. See `state/progress.md` for progress.
   ```
6. Add a new section to `state/progress.md` for this book with an empty chapter table:
   ```markdown
   ## <book-slug>

   | Chapter | Title | Status | Notes |
   |---------|-------|--------|-------|
   ```
7. Auto-commit with the message: `chore: register <book-slug> as new source`
8. Confirm what was created and remind the user to:
   - Run `/summarize <book-slug> 1` to summarise the first chapter.
   - If the book has a full chapter manifest (like the RAE), update the `CHAPTERS` and `PARTS` arrays in `build.py` to include it, then run `python3 build.py` to verify the build.
