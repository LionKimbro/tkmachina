# Tasks

This is a lightweight task ledger for design and implementation follow-up items.

## Open

### Implement ADR-0010 Runtime Invariant Tests

- Origin date: 2026-07-05
- Source: ADR-0010 Test Harness
- Status: Open

Create fast runtime tests that exercise RT behavior without depending on real
Tk widgets where possible.

Initial coverage targets:

- Build a template and verify castle, associate, spot, route, and placement
  records are allocated correctly.
- Verify failed builds clean up partially created runtime records and move the
  request into the failed-build list.
- Verify `destroy_all()` or its successor clears active runtime records,
  queues, routes, castles, associates, spots, and placements.
- Verify route delivery moves associate-originated events to the intended
  castle inbox.
- Verify castle handlers and reconcilers update desired associate state and
  mark associates dirty only when values change.
- Verify dirty projection skips inactive or destroyed associates.
- Verify structural clearing, building, and replacement execute in scheduled
  order.
- Verify multiple builds remain isolated and do not cross-route messages.

Use fake associate types for these tests so the runtime invariants can be
checked directly and quickly.

### Implement ADR-0010 Hosted Tk Lifecycle Tests

- Origin date: 2026-07-05
- Source: ADR-0010 Test Harness
- Status: Open

Create event-loop-native Tk tests for behavior that requires the real Tk
lifecycle. These tests may use `tkintertester` or a compatible harness.

Initial coverage targets:

- Verify real widget setup and projection for core associate types.
- Verify Tk callbacks emit associate outbox events and RT routes them through
  the normal message phases.
- Verify `after(...)` timing and the fixed runtime heartbeat behave as
  expected under test control.
- Verify window close and teardown destroy widgets and deactivate associated
  runtime records.
- Verify structural replacement destroys old widgets before building and
  projecting replacements.
- Verify destroyed or inactive associates do not continue to emit events or
  project onto Tk widgets.

Keep the harness outside core RT semantics. Add stable RT inspection helpers
only where tests need them and the helpers are generally useful for debugging.

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
