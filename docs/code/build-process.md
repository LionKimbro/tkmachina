# Build Process

This note describes the current runtime build process in
`src/tkmachina/rt.py`, centered on `process_build(build)`.

It is an architecture note, not an API reference. The runtime is still evolving,
so this document focuses on what the build process means, what it currently
guarantees, and where the design is still provisional.

## Purpose

The build process turns an inert-ish template result into live runtime records
and Tk widgets.

At a high level:

```text
build request
  -> template expansion
  -> castle shell allocation
  -> associate shell allocation
  -> Tk widget construction
  -> layout application
  -> default route wiring
  -> activation
```

The important design move is timing: live construction belongs to the runtime,
not to template functions. A template describes what should exist; `RT` decides
when that description becomes live records, widgets, routes, and active
participants.

## Scope

The current build process supports a small castle hierarchy demo:

- one top-level castle spec
- child castle specs declared by the top-level castle
- parent/slot attachment between castles
- optional visual mounting of a child castle's root associate
- nested associate specs
- parent-before-child associate construction
- Tk widget creation through associate type setup functions
- grid layout
- default routes from every associate outbox to the host castle inbox
- activation of castles, associates, and routes

It does not yet support multiple sibling top-level castles in one template,
destroy/rebuild reconciliation, validation, or a final serializable child
template reference format.

## Main Entry Point

The main entry point is:

```python
process_build(build)
```

It is called by `process_incoming_builds()`, not directly by the demo.

`process_incoming_builds()` drains `incoming_builds`, wraps each build request
in an active build record, appends that record to `active_builds`, and then
calls `process_build(build)` inside a `try`/`except`.

If `process_build(build)` succeeds, the build record moves to
`completed_builds`. If it raises, the build record moves to `faulty_builds` and
stores an error string.

## Inputs

`process_build(build)` receives an active build record shaped like this:

```python
{
    "kind": "active_build",
    "request": build_request,
    "spec": None,
    "castle_specs": {},
    "castle_mounts": {},
    "castle_ids": [],
    "associate_ids": [],
    "route_ids": [],
    "status": "active",
}
```

The nested `build_request` is created by `make_build_request(...)` and contains:

- `kind`
- `id`
- `template_fn`
- `build_context`
- `parent_castle`
- `slot`
- `activate_when_complete`

`template_fn`, `build_context`, `parent_castle`, `slot`, and
`activate_when_complete` have direct behavior in the current build path.

## Key Data Structures

### Build Queues

`RT` owns four build queues/lists:

- `incoming_builds`
- `active_builds`
- `completed_builds`
- `faulty_builds`

The build process assumes requests enter through `incoming_builds` via
`submit_build_request(build_request)`.

### Runtime Registries

Build creates and mutates these runtime registries:

- `castles`
- `associates`
- `routes`
- `trace`
- `dirty_associates`

`dirty_associates` is touched during widget construction because newly
constructed associates are marked dirty so their desired data is projected.

### ID Counters

`make_id(kind)` uses `_next_ids` to assign IDs for:

- `build`
- `castle`
- `associate`
- `route`

The build process depends on these IDs as registry keys and route endpoints.

### Castle Records

`allocate_castle_shells(build)` creates one castle record:

```python
{
    "kind": "castle",
    "id": castle_id,
    "name": spec["name"],
    "state": dict(spec.get("state", {})),
    "associates": {},
    "children": {},
    "inbox": [],
    "outbox": [],
    "active": False,
    "handle_fn": spec.get("handle_fn"),
}
```

The castle is registered in `RT.castles` and its ID is appended to
`build["castle_ids"]`.

### Associate Records

`allocate_associate_shell(...)` creates associate records from nested associate
specs:

```python
{
    "kind": "associate",
    "id": associate_id,
    "name": associate_spec["name"],
    "associate_type": associate_spec["associate_type"],
    "host_castle": castle_id,
    "parent_associate": parent_id,
    "children": [],
    "data": dict(associate_spec.get("data", {})),
    "tk": None,
    "child_tk_parent": None,
    "layout": dict(associate_spec.get("layout", {})),
    "grid": dict(associate_spec.get("grid", {})),
    "outbox": [],
    "active": False,
}
```

Associates are registered in `RT.associates`, added to the host castle's
`associates` mapping by name, and appended to `build["associate_ids"]`.

### Routes

`wire_default_routes(build)` creates one route for every associate:

```python
{
    "kind": "route",
    "id": route_id,
    "from_kind": "associate",
    "from_id": associate_id,
    "from_box": "outbox",
    "to_kind": "castle",
    "to_id": castle_id,
    "to_box": "inbox",
    "active": False,
}
```

Routes are appended to `RT.routes` and their IDs are recorded in
`build["route_ids"]`.

## Step-by-Step Lifecycle

### 1. Submit a build request

The demo calls:

```python
build_request = rt.make_build_request(...)
rt.submit_build_request(build_request)
```

`submit_build_request(...)` appends the request to `incoming_builds` and writes
a trace line.

### 2. Runtime tick processes incoming builds

`runtime_tick()` calls `process_incoming_builds()` before message delivery,
castle message processing, and dirty associate projection.

This means builds are currently processed at the beginning of a tick.

### 3. Active build record is created

For each request in `incoming_builds`, `process_incoming_builds()` creates an
active build record with empty ID lists and `spec` set to `None`.

The active build record is appended to `active_builds` before `process_build`
runs.

### 4. Expand template

`expand_template(build)` calls:

```python
request["template_fn"](request["build_context"])
```

The returned spec is stored in `build["spec"]`.

In the current demo, `demo_template(build_context)` returns a parent castle spec
with a child `trace_log_castle` declaration and nested associate specs. The
parent's top-level associate is `main_window`, and its children include
`priority_button`, `count_label`, `size_label`, and `reset_button`.

### 5. Allocate castle shell

`allocate_castle_shells(build)` reads `build["spec"]`, creates the parent
castle record, recursively expands declared child castle templates, registers
castle records in `RT.castles`, and records their IDs in `build["castle_ids"]`.

If a castle is built into a parent slot, the relationship is recorded both
ways:

```python
parent_castle["children"][slot] = child_castle_id
child_castle["parent"] = parent_castle_id
child_castle["slot"] = slot
```

Castles are inactive at this point.

### 6. Allocate associate shells

`allocate_associate_shells(build)` walks each built castle's `associates` list.
For each associate spec, it calls `allocate_associate_shell(...)`.

If a child castle has a visual mount, its single root associate is mounted under
the requested parent associate and receives the mount's grid options.

`allocate_associate_shell(...)` is recursive. It allocates a shell for the
current associate, then recursively allocates shells for any child specs in
`associate_spec["children"]`.

This recursion gives the build process its current nesting structure. Parent
associate IDs are recorded in child associates, and parent associates record
child IDs in their `children` list.

All associates are inactive at this point and have `tk` set to `None`.

### 7. Construct widgets

`construct_widgets(build)` iterates through `build["associate_ids"]` in the
order associates were allocated.

For each associate:

1. `get_widget_parent(build, associate)` resolves the Tk parent.
2. The associate type's `setup_fn` is called.
3. The associate is marked dirty.
4. A trace line is appended.

Top-level associates use the global `RT.tk_master`, which is created by
`setup_tk_bootstrap()` before build processing. Child associates use either
their parent associate's `child_tk_parent` or the parent's `tk` widget.

For example, `setup_window_associate(...)` creates a `tk.Toplevel`, creates a
content frame, stores the Toplevel in `associate["tk"]`, and stores the content
frame in `associate["child_tk_parent"]`. Later children are constructed inside
that content frame.

### 8. Apply layout

`apply_layout(build)` iterates through all associates again.

For an associate with `child_tk_parent`, its `layout` dictionary is applied to
that child host. Currently this supports `columnconfigure` and `rowconfigure`.

If an associate has a non-empty `grid` dictionary, `associate["tk"].grid(...)`
is called with those options.

This means a parent associate can configure the layout behavior of the host it
provides to children, while each child associate carries its own grid placement.

### 9. Wire default routes

`wire_default_routes(build)` creates a default associate-to-castle route for
every associate in the build.

These routes are inactive until activation. Once active, `deliver_messages()`
drains each associate's `outbox` into the host castle's `inbox`.

### 10. Append extra routes

`append_extra_routes(build)` walks each built castle spec and materializes its
declared route specs.

### 11. Activate

If `build["request"]["activate_when_complete"]` is true,
`activate_build(build)` marks castles, associates, and build-created routes as
active.

Only active castles process messages. Only active routes deliver messages. Only
active associates are projected by `project_dirty_associates()`.

### 12. Build completion or fault

If all phases complete, `process_incoming_builds()` marks the build as
completed and moves it from `active_builds` to `completed_builds`.

If a phase raises, the build is marked faulty, receives an `error` field, and
moves to `faulty_builds`.

## How Templates Are Interpreted

Templates are expanded by calling a Python function with `build_context`.

The current demo template returns a dictionary with:

- `kind`
- `name`
- `state`
- `handle_fn`
- `associates`

The build process expects the spec to contain enough data to allocate one
castle and zero or more associates. It does not currently validate the `kind`
fields.

Associates are interpreted recursively. Each associate spec can contain:

- `kind`
- `name`
- `associate_type`
- `data`
- `layout`
- `grid`
- `children`

The current template is not fully inert in a strict data-only sense. It contains
function objects such as `handle_fn` and `associate_type` dictionaries whose
values include setup/project/destroy functions. This is acceptable for the
current experiment, but it is an important design tension if templates are meant
to become pure data later.

## Runtime Participation

### `RT`

`RT` owns the timing and registries:

- it receives build requests
- it expands templates
- it creates live records
- it calls associate setup functions
- it applies layout
- it creates routes
- it activates records
- it later delivers messages and projects dirty associates

### Castles

During build, castles are allocated as inactive records. They do not create Tk
widgets. They receive a `handle_fn` from the template and are given inbox/outbox
queues.

After activation, active castles process messages in
`process_castle_messages()`.

### Associates

During build, associates are first allocated as inactive records with no Tk
widget. Later, `construct_widgets(build)` calls each associate type's `setup_fn`
to create or attach the actual Tk widget.

Associate types live in `src/tkmachina/associates.py`. Current types include:

- `WINDOW_ASSOCIATE_TYPE`
- `BUTTON_ASSOCIATE_TYPE`
- `LABEL_ASSOCIATE_TYPE`

### Widgets

Tk widgets are created only in associate setup functions.

The build process itself does not know how to create a button, label, or
Toplevel. It knows how to call the associate type's `setup_fn` with an
appropriate parent.

### Routes

Routes are runtime-owned records. During build, default routes are created from
every associate outbox to the host castle inbox.

## Invariants

### Before Build

These conditions should hold before `process_build(build)` runs:

- `build["request"]` is a build request.
- `build["spec"]` is `None`.
- `build["castle_ids"]`, `build["associate_ids"]`, and `build["route_ids"]` are
  empty lists.
- `setup_tk_bootstrap()` has been called before any top-level Tk associate is
  constructed.
- The build request has a callable `template_fn`.

### During Build

The process assumes:

- template expansion happens before shell allocation
- castle shell allocation happens before associate shell allocation
- associate shell allocation happens before widget construction
- parent associates are allocated and constructed before their children
- routes are created before activation
- records remain inactive until `activate_build(build)`

### After Successful Build

After successful activation:

- created castle IDs exist in `RT.castles`
- created associate IDs exist in `RT.associates`
- created route IDs correspond to active routes in `RT.routes`
- created castles are active if `activate_when_complete` was true
- created associates are active if `activate_when_complete` was true
- created routes are active if `activate_when_complete` was true
- constructed associates have `tk` set to a concrete widget
- newly constructed associates have been marked dirty at least once

## Ordering Notes

Ordering is central to the current design.

`process_build(build)` currently orders phases like this:

```python
expand_template(build)
allocate_castle_shells(build)
allocate_associate_shells(build)
construct_widgets(build)
apply_layout(build)
wire_default_routes(build)
append_extra_routes(build)
activate_build(build)
```

Important ordering assumptions:

- `build["spec"]` exists before any allocation.
- `build["castle_ids"][0]` exists before associate allocation.
- Associate allocation is recursive and parent-first.
- Widget construction follows `build["associate_ids"]`, which currently
  preserves parent-before-child order.
- A child widget can only be constructed correctly if its parent associate has
  already had a chance to set `child_tk_parent` or `tk`.
- Layout is applied after widgets exist.
- Routes are inactive until all widget/layout work is complete.
- Activation comes last.

## Responsibilities And Non-Responsibilities

### Build Responsibilities

`process_build(build)` is responsible for coordinating the transition from a
build request to live inactive records, then to active records.

It owns the order of the build phases.

It is responsible for ensuring records are registered before later phases depend
on them.

It is responsible for ensuring widgets are constructed before layout is applied.

It is responsible for ensuring routes are wired before activation.

### Template Responsibilities

The template describes what should exist.

In the current code, the template also supplies function references and
associate type dictionaries. This is convenient but not pure data.

Templates should not create live castles, associates, widgets, or routes.

### Associate Type Responsibilities

Associate types own widget-specific construction, projection, and destruction.

The build process does not know how a button, label, or window works; it only
calls the functions named by the associate type.

### Castle Responsibilities

Castles own local state and local meaning.

The build process gives a castle its initial state and handler reference, but it
does not interpret castle messages.

### What Should Not Happen During Build

The build process should not:

- process castle inbox messages
- deliver semantic events
- call castle handlers
- interpret user interactions
- project dirty associates as a separate phase
- let templates create live Tk widgets
- let templates directly mutate runtime registries
- activate partial builds
- treat route delivery as active before `activate_build(build)`

## Known Risks / Open Questions

### Template Inertness Is Partial

The design says templates should be inert. The current template returns function
objects in `handle_fn` and associate type dictionaries containing setup,
project, and destroy functions.

That may be fine for this Python experiment, but it is not a pure serializable
spec. A future design may need a registry lookup by symbolic type name instead
of embedding function objects.

### Castle Hierarchy Is Minimal

`allocate_castle_shells(build)` supports one top-level castle and recursive
child castle declarations.

Multiple sibling top-level castle specs are not implemented.

### `parent_castle` And `slot`

Build requests can carry `parent_castle` and `slot`. If `parent_castle` is
provided, the built root castle is attached into that parent slot.

The current slot model is a named entry in `parent_castle["children"]`.

### Build Is Mostly Synchronous

Although there are build queues, `process_incoming_builds()` currently processes
each build request to completion immediately inside one runtime tick.

There is no incremental multi-tick build progression yet.

### Failure Cleanup Is Basic

If a build phase fails after some records or widgets have already been created,
the runtime revokes build-created global exports, destroys build-created
associate widgets, removes build-created routes, and unregisters build-created
associates and castles.

### Route Semantics Are Minimal

All associates receive default routes to the host castle inbox, including label
associates that do not emit messages in the current demo.

This is simple and harmless for now, but the future design may distinguish
emitting associates from non-emitting associates.

### Validation Is Absent

The build process does not validate:

- template `kind` values
- required keys
- duplicate associate names
- associate type shape
- layout option shape
- route shape
- missing parent widgets

Errors currently surface as ordinary Python exceptions.

### Activation Does Not Project

`activate_build(build)` marks records active but does not project dirty
associates. Projection happens later in `project_dirty_associates()`, usually in
the same `runtime_tick()` after `process_incoming_builds()`.

This ordering is currently intentional, but it should remain explicit.

### Tk Master Is Global Runtime State

Top-level associate construction depends on global `RT.tk_master`. This matches
the current runtime-module idea, but it means build cannot construct top-level
Tk widgets before `setup_tk_bootstrap()` has run.

### Destroy Ceremony Is Separate

`destroy_all()` now has a clearer ceremony, but it is not build-specific. It
does not destroy only the records created by a specific build. It tears down the
runtime globally.

That is acceptable for the demo, but not enough for dynamic build/unbuild
behavior.
