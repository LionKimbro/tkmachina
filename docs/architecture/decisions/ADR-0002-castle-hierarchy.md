# ADR-0002: Castle Hierarchy And Child Castle Mounting

## Status

Accepted.

## Context

The runtime can currently build multiple castles, but they remain effectively
top-level islands.

`make_build_request()` already has `parent_castle` and `slot`, and castle
records already contain `"children": {}`, but the build path does not yet
attach a newly built castle into a parent castle's child structure.

Without this, TkMachina has runtime-owned construction, but not yet composable
castle structure.

The demo needs a small child castle that owns the dynamic trace log display.
The parent demo castle should handle button, reset, and window messages, while
the child trace-log castle should receive `trace_changed` messages from the
global trace castle and update its own label.

This demonstrates that a castle can be inside another castle without being
absorbed into it.

## Decision

TkMachina will support logical parent/child castle hierarchy.

A castle may contain child castles in named slots. When a child castle is built
into a parent slot, the runtime records the relationship both ways:

```python
parent_castle["children"][slot] = child_castle_id
child_castle["parent"] = parent_castle_id
child_castle["slot"] = slot
```

A child castle is a runtime participant in its own right. It may have its own:

- state
- handler
- reconcile function
- associates
- routes
- inbox
- outbox
- children

The parent castle contains the child castle structurally, but does not
automatically interpret the child's messages or control the child's internal
state.

A child castle may also have a visual root associate that is mounted into a
parent associate's layout region. This lets the parent castle reserve a place
in its UI while the child castle owns the associates inside that place.

## Child Castle Declarations

A parent template may declare that a child castle should be built into a named
slot.

The declaration must identify the child template to instantiate, but this ADR
does not decide the long-term representation of that template reference.

In the current Python-only demo, the child declaration may use a direct function
reference:

```python
{
    "kind": "child_castle_spec",
    "slot": "trace_log",
    "template_fn": trace_log_castle_template,
}
```

This is a current implementation detail, not a permanent architectural
commitment.

Longer term, template identity should likely become registry-backed or
otherwise declarative:

```python
{
    "kind": "child_castle_spec",
    "slot": "trace_log",
    "template_ref": "demo.trace_log",
}
```

That future decision belongs to the Serializable Template Boundary ADR.

## Visual Mounting

Some child castles are headless and need no visual mounting.

Other child castles own visible associates and need to appear inside the parent
castle's UI.

For visible child castles, the child declaration may include a mount
description:

```python
{
    "kind": "child_castle_spec",
    "slot": "trace_log",
    "template_fn": trace_log_castle_template,
    "mount": {
        "parent_associate": "main_window",
        "grid": {
            "row": 3,
            "column": 0,
            "sticky": "ew",
            "pady": (14, 0),
        },
    },
}
```

The parent provides the mounting location. The child owns its visual contents.

The preferred pattern is for a visible child castle to have a root visual
associate, such as a frame or panel, and for that root associate to be mounted
into the parent layout.

For the trace-log test case:

```text
demo_castle
  main_window
    priority_button
    count_label
    size_label
    trace_log_castle
      trace_panel
        trace_label
    reset_button
```

The parent should not directly own `trace_label`. The child trace-log castle
should own it.

## Intended Demo Test Case

The demo castle will include a child `trace_log_castle`.

The parent demo castle owns and handles:

- priority button
- count label
- size label
- reset button
- relevant button/reset/window state

The child trace-log castle owns and handles:

- trace panel or trace label
- trace display state
- `trace_changed` messages

The route should be:

```text
global_trace.outbox -> trace_log_castle.inbox
```

not:

```text
global_trace.outbox -> demo_castle.inbox
```

The parent demo castle should not handle `trace_changed`.

## Consequences

This establishes castles as composable runtime participants.

A parent castle can contain a child castle without knowing the child's internal
message vocabulary.

A child castle can receive messages directly from global or external castles.

Logical containment and visual mounting are related but distinct:

- logical containment records parent/child ownership
- visual mounting places the child's root visual associate into the parent's UI

This ADR does not require every child castle to be visual. Headless child
castles remain valid.

This ADR does not require a final serializable template-reference system.
Direct Python `template_fn` references are acceptable in the current demo, but
provisional.

## Non-Goals

This ADR does not decide the final serializable template format.

This ADR does not introduce a general template registry.

This ADR does not define a full layout language.

This ADR does not define subtree replacement or dynamic rebuild semantics.

This ADR does not require parent castles to route, inspect, or mediate all child
castle messages.

## Implementation Status

Implemented in the demo runtime.

## End Notes

### Superseded Visual Mounting Model

ADR-0012 refines this ADR.

The logical parent/child castle hierarchy described here remains accepted: castles may contain child castles, child castles are independent runtime participants, and logical containment is distinct from visual presentation.

However, ADR-0012 supersedes this ADR's `mount` representation for visual child castles. Visual placement should now be expressed by the parent castle's `spots` and `placements`, not by a `mount` block carried on the child castle declaration.

In other words:

```text
ADR-0002 remains authoritative for castle hierarchy.
ADR-0012 is authoritative for layout spots and visual placement.
```

