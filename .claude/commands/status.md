# /status

Print a progress summary across all registered books.

**Usage:** `/status`

**What to do:**

1. Read `state/progress.md`.
2. For each book found, count chapters by status: `done`, `in progress`, `queued`.
3. Print a clean summary table:

```
Book              Done   In Progress   Queued
--------------    ----   -----------   ------
arrl-handbook       3         1           12
...
```

4. If `state/progress.md` is empty or no books are registered, say so clearly.
