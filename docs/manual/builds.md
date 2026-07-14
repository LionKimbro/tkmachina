# Builds and Structural Changes

A castle world is created by a **build**. Builds also mount child castles into
spots, and **structural requests** let a running castle swap what fills one of
its spots.

## Templates

A build starts from a `template_fn(build_context)` that returns a castle spec
dict (see [castles](castles.md#castle-spec)). The spec may nest child castles via
`child_castles`. Templates are plain functions, so specs can be parameterized by
`build_context`.

## Submitting a build

```python
request = rt.make_build_request(
    template_fn,
    build_context=None,
    parent_castle=None,     # for mounting into a parent
    child_name=None,        # name under the parent (required if parent_castle given)
    parent_spot=None,       # which parent spot to occupy
    activate_when_complete=True,
)
rt.submit_build_request(request)
```

Incoming build requests are executed at the start of each tick by
`process_incoming_builds`.

## Build phases

`process_build` runs these phases in order (each appends a trace entry):

1. `expand_template` — call `template_fn(build_context)` to get the spec.
2. `allocate_castle_shells` — create castle records (and nested child castles),
   attaching children to parents by `child_name`.
3. `register_global_exports` — register `exports` into `global_castles`.
4. `allocate_associate_shells` — create associate records from each castle's
   `associates`.
5. `allocate_spot_records` — create the spot tree from each castle's `spots`.
6. `apply_initial_placements` — assign spot occupants from `placements`,
   validate them, and attach occupants (associate widgets to their parent).
7. `apply_parent_spot_placement` — if mounting, place this build's root castle
   into the parent castle's `parent_spot`.
8. `construct_widgets` — call each associate type's `setup_fn(associate, parent)`
   and mark the associate dirty.
9. `apply_layout` — apply `columnconfigure`/`rowconfigure` and `.grid(...)` from
   the resolved `layout`/`grid`.
10. `wire_default_routes` — associate->host-castle and child->parent routes.
11. `append_extra_routes` — the spec's declared `routes`.
12. `activate_build` — set castles, spots, associates, and this build's routes
    active.

If any phase raises, the build is marked faulty, `cleanup_failed_build` removes
its partial records (widgets, routes, exports, placement), and the request lands
in `faulty_builds`.

## Structural requests: clear, build, replace

A running castle can change a spot's occupancy. Target the castle, then schedule
work on a spot name:

```python
rt.target_castle(castle)
rt.schedule_clearing("inspector")
rt.schedule_building("inspector", template_fn, build_context=None, child_name=None)
rt.schedule_replacement("inspector", template_fn, build_context=None, child_name=None)
```

Scheduled requests are executed once per tick by `process_structural_requests`
(after handlers/reconcile, before projection):

- **clearing** — destroy the child castle occupying the spot and empty it.
  Clearing an *associate*-occupied spot is not implemented.
- **building** — build a new child castle into an empty spot (via a normal build
  request with `parent_castle` + `parent_spot`).
- **replacement** — clear then build, in one request.

Structural failures are caught and traced rather than crashing the tick; a failed
replacement clears the old occupant and traces the build failure.

## Destruction

Destroying a child castle subtree (`destroy_castle_subtree`) deactivates the
castles, clears their queues, removes their routes, revokes their global exports,
runs their associates' `destroy_fn`s child-first, detaches them from parents, and
unregisters the records (including pruning them from completed builds).
