# Tasks

This is a lightweight task ledger for design and implementation follow-up items.

## Open

### Investigate Direct Placement Support

- Origin date: 2026-07-03
- Source: ADR-0012 review discussion
- Status: Open

Explore whether TkMachina should eventually support direct placement forms beyond the current `spots` + `placements` model.

The current ADR-0012 rule is that occupied child spots require a parent spot occupant that exposes a child layout parent. Future direct-placement support may allow additional placement modes, but it should not weaken the core castle sovereignty rule:

> A castle may place another castle, but may not lay out through it.

Questions to revisit:

- Are there useful direct-placement cases that do not require an intermediate container associate?
- Can direct placement be expressed without making child castles carry parent layout instructions?
- Would direct placement apply only to local associates, or also to child castle roots?
- How would direct placement interact with Toplevel-root castles?
- What validation would the builder need before accepting such specs?
