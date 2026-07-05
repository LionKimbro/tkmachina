# Associate Reference

This reference records the public promise of each associate type.

## Reference Page Format

Each associate reference should use this shape:

```text
Name
Purpose
Underlying Tk widget
Can host children?
Embeddable?
Desired fields
Observed fields
Private resources
Default events
Optional events
Projection behavior
Destroy behavior
Examples
Notes and open questions
```

The reference page is a design test. If one page has to describe several
different human-facing promises, the associate may need to be split.

## `window`

### Purpose

Owns a `tkinter.Toplevel` window and provides a content frame that can host
child spots.

### Underlying Tk Widget

- `tkinter.Toplevel`
- internal `ttk.Frame` as `child_tk_parent`

### Can Host Children?

Yes.

### Embeddable?

No. A window associate is a Toplevel-style root, not an embeddable child widget.

### Desired Fields

- `title`: window title
- `desired_width`: projected width
- `desired_height`: projected height
- `min_width`: minimum width
- `min_height`: minimum height
- `content_padding`: padding for the internal content frame

### Observed Fields

- `actual_width`: latest observed Toplevel width when `window_resized` handling
  is active
- `actual_height`: latest observed Toplevel height when `window_resized`
  handling is active

### Private Resources

- `projected_size`: last projected `(desired_width, desired_height)` pair

### Default Events

- `window_resized`

### Optional Events

Common widget events may be opted into, though not all are equally meaningful
on a Toplevel.

### Projection Behavior

Projection updates the title, minimum size, and requested geometry when the
desired size changes.

### Destroy Behavior

Destroys the Toplevel and clears `tk` and `child_tk_parent`.

### Example

```python
{
    "kind": "associate_spec",
    "name": "window",
    "associate_type": WINDOW_ASSOCIATE_TYPE,
    "desired": {
        "title": "TkMachina",
        "desired_width": 460,
        "desired_height": 320,
        "content_padding": 16,
    },
}
```

## `button`

### Purpose

Provides a command-style button.

### Underlying Tk Widget

- `ttk.Button`

### Can Host Children?

No.

### Embeddable?

Yes.

### Desired Fields

- `text`: button label
- `enabled`: boolean, defaults to `True`

### Observed Fields

None currently modeled.

### Private Resources

None currently modeled.

### Default Events

- `button_pressed`

`button_pressed` represents command invocation, not just a mouse click. A Tk
button can be activated by more than pointer input.

### Optional Events

Common widget events may be opted into, such as:

- `focused`
- `unfocused`
- `pointer_entered`
- `pointer_left`
- `clicked`

### Projection Behavior

Projection updates the button text and enabled/disabled state.

### Destroy Behavior

Destroys the underlying widget and clears `tk`.

### Example

```python
{
    "kind": "associate_spec",
    "name": "submit_button",
    "associate_type": BUTTON_ASSOCIATE_TYPE,
    "desired": {
        "text": "Submit",
        "enabled": True,
    },
}
```

## `label`

### Purpose

Displays text.

### Underlying Tk Widget

- `ttk.Label`

### Can Host Children?

No.

### Embeddable?

Yes.

### Desired Fields

- `text`: displayed text
- `wraplength`: optional wrap length

### Observed Fields

None currently modeled.

### Private Resources

None currently modeled.

### Default Events

None.

### Optional Events

Common widget events may be opted into, though most labels do not need events.

### Projection Behavior

Projection updates the displayed text and optional wrap length.

### Destroy Behavior

Destroys the underlying widget and clears `tk`.

### Example

```python
{
    "kind": "associate_spec",
    "name": "status_label",
    "associate_type": LABEL_ASSOCIATE_TYPE,
    "desired": {
        "text": "Ready",
        "wraplength": 360,
    },
}
```

## `entry`

### Purpose

Provides a single-line text input with semantic submission and optional change
or focus events.

### Underlying Tk Widget

- `ttk.Entry`
- `tk.StringVar` for modeled text observation

### Can Host Children?

No.

### Embeddable?

Yes.

### Desired Fields

- `text`: projected entry text
- `enabled`: boolean, defaults to `True`
- `width`: optional Entry width

### Observed Fields

- `text`: current modeled text
- `focused`: current modeled focus state

These fields are maintained even when corresponding notification events are not
enabled.

### Private Resources

- `text_var`: private `StringVar`
- `text_trace`: trace ID used to keep `observed["text"]` current
- `projected_text`: last projected desired text
- `suppress_text_changed`: suppresses event emission during projection

### Default Events

- `submitted`

`submitted` is currently emitted when Return is pressed while the Entry handles
the key event.

### Optional Events

- `text_changed`
- `focused`
- `unfocused`
- common pointer, click, key, and configure events

### Projection Behavior

Projection updates Entry text, enabled/disabled state, and optional width.

Projection does not emit `text_changed`.

### Destroy Behavior

Removes the private `StringVar` trace when present, destroys the widget, clears
`tk`, and removes private resource keys.

### Example

```python
{
    "kind": "associate_spec",
    "name": "search_entry",
    "associate_type": ENTRY_ASSOCIATE_TYPE,
    "events": ["text_changed", "focused", "unfocused"],
    "desired": {
        "text": "",
        "width": 32,
    },
}
```
