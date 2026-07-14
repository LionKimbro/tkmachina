# Associate Reference

The built-in associate types, from `src/tkmachina/associates.py`. Each type is a
dict exported as a constant (e.g. `BUTTON_ASSOCIATE_TYPE`) that a castle spec
references as `associate_type`.

Every type also supports the opt-in [common widget events](associates.md#common-widget-events)
(`focused`, `clicked`, `key_pressed`, `configured`, …). Only type-specific
defaults and maintained observed fields are listed below.

## `window` — `WINDOW_ASSOCIATE_TYPE`

A `Toplevel` with an inner content frame. Non-embeddable; hosts children.

- **flags:** `can_host_children: True`, `embeddable: False`
- **default events:** `window_resized`
- **desired:** `title`, `min_width` + `min_height`, `desired_width` +
  `desired_height`, `content_padding`
- **observed:** `actual_width`, `actual_height`
- **notes:** child widgets attach to an inner content frame
  (`child_tk_parent`). Closing the window (`WM_DELETE_WINDOW`) calls
  `rt.destroy_all()` and destroys the Tk root — this is how a window-owned app
  ends. `window_resized` fires (and updates observed size) on real size changes.

## `frame` — `FRAME_ASSOCIATE_TYPE`

A `ttk.Frame` container. Hosts children.

- **flags:** `can_host_children: True`, `embeddable: True`
- **default events:** none
- **desired:** `padding`, `width`, `height`
- **notes:** the frame is its own `child_tk_parent`.

## `label_frame` — `LABEL_FRAME_ASSOCIATE_TYPE`

A `ttk.LabelFrame` container with a caption.

- **flags:** `can_host_children: True`, `embeddable: True`
- **default events:** none
- **desired:** `text` (caption), `padding`, `width`, `height`
- **observed:** `text`

## `button` — `BUTTON_ASSOCIATE_TYPE`

A `ttk.Button`. Emits intent; the castle decides meaning.

- **flags:** `can_host_children: False`, `embeddable: True`
- **default events:** `button_pressed`
- **desired:** `text` (required), `enabled` (default `True`)
- **notes:** the Tk `command` emits `button_pressed` (only wired when that event
  is in the effective set).

## `label` — `LABEL_ASSOCIATE_TYPE`

A left-justified `ttk.Label`.

- **flags:** `can_host_children: False`, `embeddable: True`
- **default events:** none
- **desired:** `text` (required), `wraplength` (optional)

## `entry` — `ENTRY_ASSOCIATE_TYPE`

A `ttk.Entry` backed by a `StringVar`.

- **flags:** `can_host_children: False`, `embeddable: True`
- **default events:** `submitted` (on `<Return>`)
- **optional events:** `text_changed`
- **desired:** `text`, `enabled` (default `True`), `width`
- **observed:** `text`, `focused`
- **notes:** `observed["text"]` is kept current on every keystroke regardless of
  whether `text_changed` is subscribed. Projection suppresses `text_changed`
  while it writes `desired["text"]` back into the entry, so programmatic updates
  do not echo as user edits.

## Not yet implemented

The manual and model anticipate further associate families that are **not** in
the code yet:

- **Text-backed** associates
- **Treeview-backed** associates
- **Canvas-backed** associates

Richer surfaces like Text, Treeview, and Canvas are expected to have several
associate types over the same underlying widget, each making a different public
promise. A canvas associate in particular will need a fact surface for pointer
and modifier state and a scene-oriented projection rather than field-diffing.
