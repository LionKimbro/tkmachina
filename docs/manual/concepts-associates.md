# How Associates Work

An associate is the Little-Castles-side companion to a Tk widget or widget-like
resource.

The associate is not just a thin widget variable. It is the boundary object
that gives a castle a modeled, data-focused way to work with a concrete Tk
object.

An associate type defines a public semantic promise. It may use a Tk widget
internally, but the associate type is not defined only by that Tk widget. For
simple widgets, the relationship is often one-to-one. For richer surfaces such
as Text, Treeview, and Canvas, several associate types may eventually share the
same underlying Tk widget while making different Little Castles promises.

## Associate Record

A live associate record currently includes:

```python
{
    "kind": "associate",
    "id": associate_id,
    "name": "priority_button",
    "associate_type": BUTTON_ASSOCIATE_TYPE,
    "host_castle": castle_id,
    "desired": {...},
    "observed": {...},
    "private": {...},
    "tk": widget,
    "child_tk_parent": None,
    "outbox": [],
    "active": True,
}
```

## Desired

`associate["desired"]` is the projection target.

It contains values the castle or runtime wants the associate to project onto
the concrete widget.

Examples:

```python
button["desired"]["text"] = "Save"
button["desired"]["enabled"] = True
window["desired"]["title"] = "TkMachina"
entry["desired"]["text"] = "initial value"
```

Castle code should normally update desired state through RT helpers:

```python
rt.target_associate(button)
rt.set_desired("text", "Save")
```

`set_desired(...)` compares old and new values and marks the associate dirty
only when the value changes.

## Observed

`associate["observed"]` is the associate's public modeled-observation surface.

It is not a complete mirror of Tk. Each associate type defines which observed
fields it intentionally maintains.

Those fields should be reliable regardless of whether corresponding events are
emitted. Event interest controls notification, not whether modeled observed
state is maintained.

Examples:

```python
entry["observed"]["text"]
entry["observed"]["focused"]
window["observed"]["actual_width"]
window["observed"]["actual_height"]
```

Castle authors may read modeled observed facts. Castle authors should not
generally write `observed`; if a castle needs to interpret observed reality, it
should store that interpretation in castle state.

Raw Tk access through `associate["tk"]` remains available as an escape hatch
for rare, advanced, or unmodeled behavior. If authors routinely need raw Tk for
ordinary behavior, that is evidence the associate is under-modeled.

## Private

`associate["private"]` is associate implementation detail.

It may hold Tk resources, trace IDs, projected-value bookkeeping, caches, or
other state needed by `setup_fn`, `project_fn`, and `destroy_fn`.

Examples:

```python
entry["private"]["text_var"]
entry["private"]["text_trace"]
entry["private"]["suppress_text_changed"]
window["private"]["projected_size"]
```

Castle authors should not depend on private fields.

Private resources should be explicitly cleaned up by the associate's
`destroy_fn` when practical. For example, the Entry associate stores its
`StringVar` and trace ID in `private`, suppresses text-change emission during
projection, and removes the trace during destruction.

## Setup, Projection, And Destruction

Associate types currently use three lifecycle functions:

```python
setup_fn
project_fn
destroy_fn
```

`setup_fn` creates the concrete widget and installs the event machinery needed
by the associate.

`project_fn` projects `desired` state onto the widget.

`destroy_fn` tears down private resources and destroys the widget.

Activation is currently RT-level bookkeeping, not an associate hook.

## Events

Associates emit semantic messages through their `outbox`.

For example:

```python
{
    "kind": "event",
    "type": "button_pressed",
    "origin": "save_button",
    "emitter": "save_button",
    "payload": {},
}
```

Each associate type may define `default_events`. An associate spec may add
`events` or suppress defaults with `do_not_listen`.

The effective event set is:

```text
associate_type.default_events
union associate_spec.events
minus associate_spec.do_not_listen
```

Event interest controls which messages are emitted. It does not control which
modeled observed fields are maintained.

## Common Widget Events

TkMachina provides reusable helper binders for boring common widget events.
These events remain opt-in unless an associate type deliberately makes one a
default:

- `focused`
- `unfocused`
- `pointer_entered`
- `pointer_left`
- `clicked`
- `double_clicked`
- `middle_clicked`
- `right_clicked`
- `key_pressed`
- `key_released`
- `configured`

Associate-specific events remain on the associate type. Examples:

- `button_pressed`
- `submitted`
- `text_changed`
- `window_resized`
