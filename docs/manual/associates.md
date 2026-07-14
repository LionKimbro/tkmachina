# Associates

An associate is the modeled companion to one Tk widget. It gives a castle a
data-focused way to work with a concrete widget: it projects `desired` state onto
the widget, maintains `observed` facts about it, keeps `private` implementation
detail, and emits semantic events.

## The associate record

Allocated by `allocate_associate_shell`:

```python
{
    "kind": "associate",
    "id": "associate:5",
    "name": "priority_button",
    "associate_type": BUTTON_ASSOCIATE_TYPE,
    "host_castle": "castle:3",
    "parent_associate": <id or None>,   # widget-tree parent
    "children": [associate_id, ...],
    "desired": {...},
    "observed": {...},
    "private": {...},
    "events": [...],                    # opt-in events from the spec
    "do_not_listen": [...],             # suppressed events
    "effective_events": {...},          # default | events - do_not_listen
    "tk": <widget or None>,
    "child_tk_parent": <widget or None>,# where child widgets attach
    "layout": {...},
    "grid": {...},
    "outbox": [],
    "active": False,
}
```

## The three surfaces

### `desired` — the projection target

Values the castle wants projected onto the widget: `button["desired"]["text"]`,
`window["desired"]["title"]`, etc. Castle code should update desired state through
the runtime helpers so change-tracking and dirtying happen:

```python
rt.target_associate(button)
rt.set_desired("text", "Save")      # marks dirty only if the value changed
```

`set_desired` compares old and new and returns `True`/`False` for whether it
changed anything. `set_data` is an alias.

### `observed` — the modeled fact surface

The associate's public present-tense facts about the widget — e.g.
`entry["observed"]["text"]`, `entry["observed"]["focused"]`,
`window["observed"]["actual_width"]`. Each associate type defines which observed
fields it maintains, and it maintains them **regardless of whether the
corresponding event is emitted** (event interest controls notification, not
whether observed state is kept current). Castle authors may read `observed`; they
should not generally write it — store interpretations in castle state instead.
Read observed via `rt.get_observed(associate, key)`.

### `private` — implementation detail

Tk resources, trace ids, projection bookkeeping, caches used by the type's
`setup_fn` / `project_fn` / `destroy_fn`. Castle authors should not depend on
private fields. For example, the entry associate keeps its `StringVar`, its write
trace id, and a `suppress_text_changed` flag in `private`, and removes the trace
in its `destroy_fn`.

## Lifecycle functions

An associate type provides three functions:

- **`setup_fn(associate, tk_parent)`** — creates the concrete widget, stores it
  as `associate["tk"]` (and a `child_tk_parent` for containers), installs event
  bindings, and seeds observed facts. For the root associate, `tk_parent` is the
  hidden `tk_master`.
- **`project_fn(associate)`** — projects `desired` onto the widget, diffing
  against current widget state so it only reconfigures on change.
- **`destroy_fn(associate)`** — tears down private resources (traces, vars) and
  destroys the widget.

Construction marks each new associate dirty, so it projects once on activation.

## Events

Associates emit semantic events into their `outbox` with `emit_event`:

```python
{"kind": "event", "type": "button_pressed", "origin": name, "emitter": name, "payload": {...}}
```

Which events an associate emits is its **effective event set**:

```text
associate_type.default_events  |  spec.events  -  spec.do_not_listen
```

`emit_event` only fires for events in that set (`wants_event` gates it). This is
opt-in: a type declares defaults, and a spec adds or suppresses.

### Common widget events

Reusable binders (`bind_common_widget_events`) provide these opt-in events for
any widget associate, with raw Tk detail carried in the payload:

| Event | Payload |
|---|---|
| `focused` / `unfocused` | (also maintains `observed["focused"]`) |
| `pointer_entered` / `pointer_left` | `x, y, x_root, y_root` |
| `clicked` / `double_clicked` / `middle_clicked` / `right_clicked` | `x, y, x_root, y_root` |
| `key_pressed` / `key_released` | `keysym, char, keycode, state` |
| `configured` | `width, height, x, y` |

Type-specific events (`button_pressed`, `submitted`, `text_changed`,
`window_resized`) live on the associate type. See the
[associate reference](associate-reference.md) for each type's defaults and
observed fields.

## Placement fields

`parent_associate`, `children`, `grid`, and `layout` describe the associate's
place in the widget tree; they are set by the spot/placement system (see
[spots](spots.md)), not by the associate itself. An associate does not choose its
own row/column — placement belongs to the containing surface.
