# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Read `AGENTS.md` at the repo root before doing anything else. It is the source of truth for all agent behaviour in this repo: house style, figure rules, skill steps, state file formats, and commit conventions. It is harness-agnostic.

Claude Code-specific files live in `.claude/`:
- `.claude/commands/` — slash commands (`/summarize`, `/status`, `/new-source`)
- `.claude/skills/chapter-notes/` — the chapter summarisation skill
