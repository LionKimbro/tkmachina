# Tasks

This is a lightweight task ledger for design and implementation follow-up items.

## Open

### Prepare Manual Image And Diagram Assets

- Origin date: 2026-07-05
- Source: manual-html first snapshot
- Status: Open

Review the visual placeholders in `docs/manual-html/` and decide which images
or diagrams should become real assets.

Wishlist:

- A friendly front-door project image for the manual home page.
- An optional Lion/project portrait or personal project image.
- A diagram showing raw Tk callbacks compared with TkMachina's modeled runtime.
- A diagram showing castle -> associate -> Tk widget boundaries.
- A diagram showing child castle bubble-up routing.
- A diagram showing desired -> projection -> widget and widget -> observed /
  event flow.

### Design And Implement Text Associate Family

- Origin date: 2026-07-05
- Source: guidance3 / ADR-0015
- Status: Open

Design Text-backed associates as a family of semantic promises rather than one
monolithic `Text` wrapper.

Candidate public associates to consider:

- `plain_text_editor`
- `log_view`
- `rich_text_view`
- `code_editor`

Do not implement until the manual and associate reference format have been used
to clarify the desired/observed/events contract for each candidate.

### Design And Implement Tree Associate Family

- Origin date: 2026-07-05
- Source: guidance3 / ADR-0015
- Status: Open

Design Treeview-backed associates as multiple semantic contracts where needed.

Candidate public associates to consider:

- `tree_view`
- `single_select_table`
- `multi_select_table`
- `sortable_table`

Avoid creating one giant configurable tree/table associate before the public
promises are clear.

### Design And Implement Canvas Associate Family

- Origin date: 2026-07-05
- Source: guidance3 / ADR-0015
- Status: Open

Investigate whether Canvas should be one associate or a family of associates.

Candidate public associates to consider:

- `canvas_drawing_surface`
- `vector_canvas`
- `scene_canvas`
- `diagram_canvas`

Canvas may need an operation model or scene model rather than simple full-state
projection.

### Review Naming Case Policy

- Origin date: 2026-07-05
- Source: implementation follow-up
- Status: Open

Check the project for inconsistent use of kebab-case, snake_case, and other
name styles across files, docs, runtime records, event names, and public APIs.

Define the intended policy before changing names. In particular, decide where
Python `snake_case` is required, where document/file `kebab-case` is preferred,
and whether semantic event names should consistently remain `snake_case`.

### Implement ADR-0010 Runtime Invariant Tests

- Origin date: 2026-07-05
- Source: ADR-0010 Test Harness
- Status: Open
- Progress: Initial fake-associate invariant suite added in
  `tests/run_runtime_invariants.py` on 2026-07-05.

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
- Progress: Initial hosted Tk test added in `guitests/test_runtime_hosted.py`
  on 2026-07-05.

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

## Completed

### Implement Frame Associate

- Origin date: 2026-07-05
- Completed date: 2026-07-05
- Source: manual/guidance3 follow-up
- Status: Completed

Implemented a `frame` associate as a simple embeddable container associate that
can host child spots without introducing a larger widget family design question.

The implementation includes hosted Tk coverage in
`guitests/test_frame_associate_hosted.py`.

### Implement LabelFrame Associate

- Origin date: 2026-07-05
- Completed date: 2026-07-05
- Source: Frame associate follow-up
- Status: Completed

Implemented a `label_frame` associate as an embeddable labeled container
associate that can host child spots.

The implementation shares the ordinary frame container projection path for
child hosting, padding, width, and height. It also models caption text through
`desired["text"]` and `observed["text"]`.

The implementation includes hosted Tk coverage in
`guitests/test_label_frame_associate_hosted.py`.
