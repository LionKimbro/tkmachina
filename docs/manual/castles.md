# Castles

A castle is a bounded state machine that owns a region of application meaning.

## The castle record

An allocated castle is a dictionary (see `allocate_castle_shell`):

```python
{
    "kind": "castle",
    "id": "castle:3",
    "template_name": "context_panel",
    "parent": <parent castle id or None>,
    "child_name": <name under which the parent knows this child, or None>,
    "state": {...},              # copied from the spec's "state"
    "associates": {name: id},    # this castle's associates by name
    "children": {child_name: id},# child castles by name
    "spots": {name: spot},       # this castle's spots by name
    "placements": {spot: {...}}, # spot -> occupant placement
    "inbox": [],                 # incoming messages, drained on the tick
    "outbox": [],                # outgoing messages, delivered by routes
    "active": False,             # set True at activation
    "handle_fn": <fn or None>,
    "reconcile_fn": <fn or None>,
}
```

The global trace castle additionally carries `"global": True` and
`"headless": True`.

## Castle spec

A `template_fn(build_context)` returns a spec. Recognized keys:

```python
{
    "template_name": "context_panel",   # required (or "name")
    "state": {...},                     # initial owned state
    "associates": [ <associate spec>, ... ],
    "spots": <spot spec tree>,          # optional
    "placements": {spot_name: {"kind": "associate"|"child_castle", "name": ...}},
    "child_castles": [ {"name", "template_fn", "build_context"}, ... ],
    "routes": [ <route spec>, ... ],    # extra routes
    "exports": [ {"name", "target": {"kind": "castle", "template_name"}} ],
    "handle_fn": <fn>,
    "reconcile_fn": <fn>,
}
```

## Handling messages: `handle_fn(castle, message)`

On each tick, `process_castle_messages` drains every active castle's inbox and
calls `handle_fn(castle, message)` for each message. The castle is passed
explicitly (it is not ambient). The handler updates `castle["state"]`, may append
events to `castle["outbox"]`, and may set desired state on its associates
(usually via `rt.target_associate(...)` + `rt.set_desired(...)`).

The handler returns one of:

```python
rt.IGNORED        # do not mark the castle dirty
rt.HANDLED        # handled, but no reconciliation needed
rt.HANDLED_DIRTY  # handled; mark the castle dirty so reconcile_fn runs
None              # treated as HANDLED_DIRTY (convenience default)
```

Any other return value raises `ValueError`. A castle with no `handle_fn` skips
message processing entirely (its inbox is left alone).

## Reconciling: `reconcile_fn(castle)`

A castle is *not* inherently a view projector. After messages are processed,
`reconcile_dirty_castles` calls `reconcile_fn(castle)` once for each dirty castle
that provides one. Reconcile is a free-form derived pass: it may recompute
derived associate state, emit derived messages, update child structures, or do
nothing. Headless and service castles need neither associates nor a
`reconcile_fn`.

> Note: reconcile is the natural home for a per-tick derived/continuity pass —
> reading `observed` facts and updating `desired` — for surfaces (like a future
> canvas) that need more than field-diff projection.

## Emitting messages

A castle emits by appending an event record to its own `outbox`; routes carry it
onward (by default a child castle's outbox routes to its parent's inbox). For
example, the global trace castle appends a `trace_changed` event to its outbox
whenever a trace entry is added.

## Dirty tracking

- `rt.mark_castle_dirty(castle_or_id)` marks a castle for reconciliation.
- `rt.mark_dirty(associate_or_id)` marks an associate for projection.
- `rt.mark_castle_associate_dirty(castle, name)` marks one of a castle's
  associates dirty by name.

Setting desired state through `rt.set_desired` marks the targeted associate dirty
automatically (only when the value actually changes).

## Lifecycle

A castle is allocated inactive, then set `active` at activation. Destruction of a
castle subtree (via structural clearing/replacement or `destroy_all`) deactivates
it, clears its queues, runs its associates' `destroy_fn`s child-first, removes its
routes, revokes its global exports, and unregisters the records.
