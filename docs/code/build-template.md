# Build Template

This note documents the current build template shape used by
`src/tkmachina/rt.py`.

A template is a Python callable that returns a castle spec. The returned spec
declares the castle's local beings, places, initial placements, state, handlers,
and routes.

## Purpose

Templates are reusable construction patterns.

They do not create live castles directly. They describe what the runtime should
build. A live castle instance appears only after the runtime processes a build
request or scheduled structural building operation.

```text
template function + build context
  -> castle spec
  -> runtime build process
  -> live castle instance
```

## Template Function

A template function receives one dictionary:

```python
def demo_template(build_context):
    return {
        "kind": "castle_spec",
        "template_name": "demo_castle",
        ...
    }
```

`build_context` is per-invocation input. Templates should copy the values they
need into the returned spec.

## Castle Spec Shape

A current castle spec may contain:

```python
{
    "kind": "castle_spec",
    "template_name": "demo_castle",
    "state": {...},
    "handle_fn": handle_demo_castle_message,
    "reconcile_fn": reconcile_demo_castle,
    "child_castles": [...],
    "associates": [...],
    "spots": {...},
    "placements": {...},
    "routes": [...],
    "exports": [...],
}
```

`template_name` is the descriptive name for the kind of castle being built. It
is not a live-object address and does not need to be globally unique.

For transition, the runtime still accepts `name` as a fallback for
`template_name`. New templates should use `template_name`.

Useful visual castles usually provide associates, spots, and placements.

## Castle State

`state` is copied into the live castle record:

```python
"state": {
    "press_count": 0,
    "button_enabled": True,
}
```

Castle state is semantic memory owned by the castle. It is distinct from
associate `desired`, `observed`, and `private` state.

## Handlers And Reconciliation

`handle_fn` processes messages from the castle inbox:

```python
def handle_demo_castle_message(castle, message):
    ...
```

It returns one of:

```python
rt.IGNORED
rt.HANDLED
rt.HANDLED_DIRTY
```

`None` is currently treated like `HANDLED_DIRTY`.

`reconcile_fn` interprets castle state into desired associate state:

```python
def reconcile_demo_castle(castle):
    button = rt.get_associate(castle, "priority_button")
    rt.target_associate(button)
    rt.set_desired("enabled", castle["state"]["button_enabled"])
```

Reconciliation should update `associate["desired"]`, not Tk widgets directly.

## Associates

Associates are declared in `associates`:

```python
{
    "kind": "associate_spec",
    "name": "priority_button",
    "associate_type": BUTTON_ASSOCIATE_TYPE,
    "desired": {
        "text": "Required (5 left)",
        "enabled": True,
    },
}
```

The current runtime copies these spec sections into associate records:

```python
"desired": dict(associate_spec.get("desired", ...))
"observed": dict(associate_spec.get("observed", {}))
"private": dict(associate_spec.get("private", {}))
"events": list(associate_spec.get("events", []))
"do_not_listen": list(associate_spec.get("do_not_listen", []))
"effective_events": (
    associate_type.default_events
    union associate_spec.events
    minus associate_spec.do_not_listen
)
```

During transition, `data` may be used as a fallback source for `desired`, but
new templates should use `desired`.

### Desired

`desired` is what the castle or runtime wants projected onto the concrete
widget.

Examples:

```python
{"text": "Reset", "enabled": True}
{"title": "TkMachina RT Demo", "desired_width": 460}
```

### Observed

`observed` is widget reality reported back by the associate.

Example:

```python
{
    "actual_width": None,
    "actual_height": None,
}
```

Castles should not write observed values directly. They should receive messages
and store interpreted semantic memory in castle state.

### Private

`private` is projector or widget bookkeeping.

Example:

```python
{"projected_size": (460, 480)}
```

Templates usually do not need to initialize `private`.

### Event Interest

Associate specs may opt into or suppress semantic events:

```python
{
    "kind": "associate_spec",
    "name": "search_box",
    "associate_type": ENTRY_ASSOCIATE_TYPE,
    "events": ["text_changed", "submitted"],
    "do_not_listen": ["focus_changed"],
}
```

The runtime computes `effective_events` from the associate type's
`default_events`, the spec's `events`, and the spec's `do_not_listen` list.

Associate setup functions should bind or emit only semantic events included in
`effective_events`.

## Associate Types

Associate types live in `src/tkmachina/associates.py`.

The current type dictionaries look like:

```python
{
    "name": "button",
    "can_host_children": False,
    "embeddable": True,
    "default_events": ["button_pressed"],
    "setup_fn": setup_button_associate,
    "project_fn": project_button_associate,
    "destroy_fn": destroy_widget_associate,
}
```

Important flags:

- `can_host_children`: the associate can provide a layout parent for child spots
- `embeddable`: the associate can be embedded into another widget hierarchy
- `default_events`: semantic events enabled unless the associate spec suppresses
  them

`WINDOW_ASSOCIATE_TYPE` can host children but is not embeddable.

Current built-in event defaults:

- `WINDOW_ASSOCIATE_TYPE`: `window_resized`
- `BUTTON_ASSOCIATE_TYPE`: `button_pressed`
- `LABEL_ASSOCIATE_TYPE`: no default events

## Child Castles

Child castles are declared separately from layout:

```python
"child_castles": [
    {
        "kind": "child_castle_spec",
        "name": "trace_log",
        "template_fn": trace_log_castle_template,
        "build_context": {"trace_wraplength": 400},
    },
]
```

The `name` is the parent-local child name. The runtime stores:

```python
parent_castle["children"]["trace_log"] = child_castle_id
```

This does not visually place the child castle. Visual placement happens through
`spots` and `placements`.

## Spots

Spots declare the castle's local layout places:

```python
"spots": {
    "name": "main_window_spot",
    "layout": {
        "columnconfigure": {0: {"weight": 1}},
    },
    "children": [
        {
            "name": "priority_button_spot",
            "grid": {"row": 0, "column": 0, "sticky": "ew"},
        },
        {
            "name": "trace_log_spot",
            "grid": {"row": 1, "column": 0, "sticky": "ew"},
        },
    ],
}
```

A spot belongs to one castle. A parent castle may place a child castle into one
of its own spots, but it may not lay out through that child castle into the
child castle's internal spots.

## Placements

`placements` declare initial spot occupants:

```python
"placements": {
    "main_window_spot": {
        "kind": "associate",
        "name": "main_window",
    },
    "trace_log_spot": {
        "kind": "child_castle",
        "name": "trace_log",
    },
}
```

`kind` may currently be:

- `"associate"` for a local associate
- `"child_castle"` for a local child castle

Placements are initial occupancy, not permanent structure. Later runtime
operations may schedule clearing, building, or replacement of spot occupancy.

## Branching Spot Rule

ADR-0012 requires:

```text
if a spot has occupied child spots,
then the parent spot must have an occupant,
and that occupant must be a local associate that can host children
```

For example, if `main_window_spot` has child spots that are occupied, then
`main_window_spot` must contain something like a window, frame, or label frame
associate type with `can_host_children`.

## Placed Child Castle Rule

A child castle placed into a parent spot must expose exactly one root associate.

If the child castle is embedded below another associate, that root associate
must be embeddable. A `Toplevel`-style window root is not embeddable into
another widget hierarchy.

## Routes

Every associate automatically gets a default route:

```text
associate.outbox -> host_castle.inbox
```

Templates may also declare explicit routes:

```python
"routes": [
    {
        "kind": "route_spec",
        "from": {
            "kind": "global_castle",
            "name": rt.TRACE_CASTLE,
            "box": "outbox",
        },
        "to": {
            "kind": "castle",
            "template_name": "trace_log_castle",
            "box": "inbox",
        },
    },
]
```

Endpoint kinds currently include:

- `"global_castle"`
- `"castle"` within the current build
- `"associate"` within the current build

## Exports

Templates may export castles into `rt.global_castles`:

```python
"exports": [
    {
        "name": "some_global_name",
        "target": {
            "kind": "castle",
            "template_name": "local_castle_template_name",
        },
    },
]
```

The current runtime supports castle exports only.

## Structural Scheduling

Templates describe initial structure. Runtime mutation uses scheduled
operations:

```python
rt.target_castle(castle)
rt.schedule_clearing("trace_log_spot")
rt.schedule_building("trace_log_spot", trace_log_template)
rt.schedule_replacement("trace_log_spot", trace_log_template)
```

The new occupant is specified by a template. The live child castle does not
exist until the runtime executes the scheduled building lifecycle operation.

ADR-0013 applies: scheduled mutations execute in order as lifecycle operations.
The runtime does not compute a final desired tree.

## Naming And Addressing

Names in templates are local:

- associate names are local to the owning castle
- child names are local to the parent castle
- spot names are local to the owning castle
- template names are descriptive metadata for what was built
- route endpoint names are resolved within the build or global registry

Runtime ids distinguish multiple live instances built from the same template.

## Current Limits

- Templates are Python callables, not serializable specs.
- Handler, reconciliation, template, and associate type references are direct
  Python objects.
- `data` is accepted only as a transition fallback for associate `desired`.
- The builder validates current spot and placement rules, but the lifecycle
  model is still evolving.
