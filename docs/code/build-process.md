# Build Process

This note describes the current runtime build process in `src/tkmachina/rt.py`,
centered on `process_build(build)`.

It is an architecture note, not an API reference. It explains what the runtime
currently does when turning a template result into live castle, associate, spot,
route, and widget records.

## Purpose

The build process turns a template result into live runtime structure.

At a high level:

```text
build request
  -> template expansion
  -> castle shell allocation
  -> associate shell allocation
  -> spot allocation
  -> initial spot occupancy
  -> widget construction
  -> layout
  -> route wiring
  -> activation
```

`process_build(build)` is not the whole runtime. It is the construction
ceremony used by normal submitted builds and by scheduled structural building
operations.

## Scope

The build process currently handles:

- expanding one `template_fn(build_context)` into a castle spec
- allocating one root castle and its declared child castles
- registering optional global castle exports
- allocating associates with `desired`, `observed`, and `private` state
- allocating named spots from a spot tree
- resolving initial `placements`
- validating spot occupancy rules from ADR-0012
- constructing Tk widgets through associate type `setup_fn`
- applying grid layout
- wiring default associate-to-castle routes
- appending explicit template routes
- activating the completed build

It does not interpret castle state, process messages, reconcile desired view
state, or project dirty associates. Those happen in later runtime phases.

## Main Entry Point

The main entry point is:

```python
process_build(build)
```

Normal callers do not call this directly. They submit a build request:

```python
rt.submit_build_request(rt.make_build_request(template_fn, build_context))
```

`process_incoming_builds()` later pops requests and calls
`execute_build_request(request)`, which creates an active build record and calls
`process_build(build)` inside a failure boundary.

Scheduled structural operations also call `execute_build_request(...)` when
they need to build a child castle into an already-live parent spot.

## Inputs

`process_build(build)` receives an active build record:

```python
{
    "kind": "active_build",
    "request": request,
    "spec": None,
    "castle_specs": {},
    "castle_ids": [],
    "associate_ids": [],
    "spot_ids": [],
    "route_ids": [],
    "global_export_names": [],
    "status": "active",
}
```

The build request carries:

```python
{
    "kind": "build_request",
    "id": "build:1",
    "template_fn": template_fn,
    "build_context": {...},
    "parent_castle": None,
    "child_name": None,
    "parent_spot": None,
    "activate_when_complete": True,
}
```

`slot` may still appear in request records as a legacy compatibility alias for
`child_name`. New code should use `child_name` and `parent_spot`.

## Key Data Structures

### Build Records

The build record is a transaction-ish ledger for one construction attempt. It
tracks every castle, associate, route, spot, and global export created by that
attempt so failed builds can be cleaned up.

Completed builds move to `completed_builds`. Failed builds move to
`faulty_builds` after cleanup.

### Castle Records

Castle shells are allocated before associates, spots, widgets, and routes:

```python
{
    "kind": "castle",
    "id": castle_id,
    "template_name": spec["template_name"],
    "parent": parent_castle_id,
    "child_name": child_name,
    "state": dict(spec.get("state", {})),
    "associates": {},
    "children": {},
    "spots": {},
    "placements": {},
    "inbox": [],
    "outbox": [],
    "active": False,
    "handle_fn": spec.get("handle_fn"),
    "reconcile_fn": spec.get("reconcile_fn"),
}
```

`children` maps a parent-local child name to a child castle id. `spots` maps a
parent-local spot name to a spot record.

`template_name` is descriptive metadata copied from the castle spec. It is not
the castle's live identity. The runtime id is the identity.

### Associate Records

Associate shells are allocated from `spec["associates"]`:

```python
{
    "kind": "associate",
    "id": associate_id,
    "name": associate_spec["name"],
    "associate_type": associate_spec["associate_type"],
    "host_castle": castle_id,
    "parent_associate": parent_id,
    "children": [],
    "desired": {...},
    "observed": {...},
    "private": {...},
    "events": [...],
    "do_not_listen": [...],
    "effective_events": {...},
    "tk": None,
    "child_tk_parent": None,
    "layout": {...},
    "grid": {...},
    "outbox": [],
    "active": False,
}
```

`desired` is the projection target. `observed` is raw-ish GUI reality reported
by the associate. `private` is projector/widget bookkeeping.

`events` and `do_not_listen` are copied from the associate spec.
`effective_events` is computed from the associate type's `default_events`,
plus `events`, minus `do_not_listen`. Associate setup functions use this set to
avoid binding or emitting semantic events the instance did not ask for.

During transition, `associate_spec["data"]` is still accepted as a fallback
source for `desired` if `desired` is absent.

### Spot Records

Spot records come from the castle spec's `spots` tree:

```python
{
    "kind": "spot",
    "id": spot_id,
    "name": spot_name,
    "host_castle": castle_id,
    "parent_spot": parent_spot_name,
    "children": [],
    "layout": {...},
    "grid": {...},
    "occupant": None,
    "active": False,
}
```

Spots are places. Associates and child castles are beings. Initial
`placements` put beings into places.

### Routes

The build process creates one default route for every associate:

```text
associate.outbox -> host_castle.inbox
```

It also appends explicit route specs from templates, including routes involving
global castles such as `global_trace`.

## Step-By-Step Lifecycle

### 1. Expand Template

`expand_template(build)` calls:

```python
request["template_fn"](request["build_context"])
```

The result is stored as `build["spec"]`.

### 2. Allocate Castle Shells

`allocate_castle_shells(build)` allocates the root castle. If the request has a
`parent_castle`, the new root is attached to that parent's `children` mapping
under `child_name`.

Then `allocate_castle_shell(...)` recursively expands each declared
`child_castles` entry and allocates child castle shells.

### 3. Register Global Exports

`register_global_exports(build)` processes template `exports`. The current
runtime supports exporting castle targets into `global_castles`.

Exports are validated before registration so duplicate names do not partially
register.

### 4. Allocate Associate Shells

`allocate_associate_shells(build)` creates inactive associate records for each
castle's local associate specs.

At this point no Tk widgets exist yet.

### 5. Allocate Spot Records

`allocate_spot_records(build)` walks each castle spec's `spots` tree and
allocates named spot records into the owning castle.

Duplicate spot names within one castle are invalid.

### 6. Apply Initial Placements

`apply_initial_placements(build)` does three things:

```text
assign initial spot occupants
validate spot occupants
apply placement effects to associate parent/grid/layout records
```

Placements can name local associates or child castles:

```python
"placements": {
    "main_window_spot": {"kind": "associate", "name": "main_window"},
    "trace_log_spot": {"kind": "child_castle", "name": "trace_log"},
}
```

ADR-0012 rules are enforced here:

- if a spot has occupied child spots, that spot must have an occupant
- the branching spot occupant must be a local associate
- that associate type must have `can_host_children`
- a placed child castle must expose exactly one root associate
- embedded child roots must be embeddable

### 7. Apply Parent Spot Placement

If a build request came from scheduled structural building, it carries
`parent_castle` and `parent_spot`.

`apply_parent_spot_placement(build)` places the newly built root castle into
that live parent spot. This is how `schedule_building(...)` and
`schedule_replacement(...)` build new child castles into already-live layouts.

### 8. Construct Widgets

`construct_widgets(build)` calls each associate type's `setup_fn`.

The widget parent is resolved from `parent_associate`. Root associates use
`tk_master`. Child associates use the parent associate's `child_tk_parent` when
present, otherwise the parent associate's `tk`.

Constructed associates are marked dirty so their `desired` state will be
projected.

### 9. Apply Layout

`apply_layout(build)` applies child layout configuration and grids widgets.

`layout["columnconfigure"]` and `layout["rowconfigure"]` apply to an
associate's `child_tk_parent` when it has one. `grid` applies to the
associate's concrete Tk widget.

### 10. Wire Routes

`wire_default_routes(build)` creates associate outbox routes to host castle
inboxes.

`append_extra_routes(build)` appends explicit template routes.

### 11. Activate

If `activate_when_complete` is true, `activate_build(build)` marks castles,
spots, associates, and build-created routes active.

Only active castles process messages. Only active associates project dirty
state.

## Runtime Scheduling

The runtime tick currently runs:

```python
process_incoming_builds()
deliver_messages()
process_castle_messages()
reconcile_dirty_castles()
process_structural_requests()
project_dirty_associates()
```

This means normal submitted builds happen before message delivery in a tick.
Scheduled structural operations happen after castle reconciliation and before
associate projection.

ADR-0013 is the current structural scheduling rule: structural requests execute
in queue order as lifecycle operations. A replacement is not split into a
global delete phase and a later global build phase.

## Failure Behavior

`execute_build_request(request)` wraps `process_build(build)` in a failure
boundary.

On failure:

- build status becomes `faulty`
- `cleanup_failed_build(build)` revokes global exports
- failed parent spot placement is detached if needed
- created widgets are destroyed
- build-created runtime records are unregistered
- the build record moves to `faulty_builds`

This is deliberately simple, but it preserves runtime integrity for the current
model.

## Responsibilities And Non-Responsibilities

`process_build(build)` is responsible for construction.

It is not responsible for:

- interpreting messages
- deciding desired associate state from castle state
- projecting dirty associates
- computing an optimal tree edit plan
- preserving descendant structural intent across ancestor replacement
- hiding/showing widgets as a structural operation

Visibility, when supported, should be ordinary associate `desired` state and
projection. It is not build, clearing, or replacement.

## Known Risks / Open Questions

- `slot` still exists as a compatibility request field. New code should prefer
  `child_name` and `parent_spot`.
- Castle specs may still provide `name` as a temporary fallback for
  `template_name`; new templates should use `template_name`.
- Template specs still use direct Python function references and associate type
  dictionaries. This is useful now but not serializable.
- Cleanup and destruction are still simple runtime ceremonies. They are better
  than the first demo version, but not yet a complete resource lifecycle model.
- Scheduled structural operations currently target recorded castle ids and spot
  names. Future address/path semantics may become useful.
- Associate `data` is accepted as a temporary fallback for `desired`; it should
  eventually disappear.
