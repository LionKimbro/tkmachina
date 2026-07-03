# ADR-0011: Event Interest And Filtering

## Discussion Item

As TkMachina grows broader coverage over the Tkinter widget set, the runtime
will likely see a deluge of raw widget activity and semantic events.

The system needs a way to express:

```text
We are interested in these events.
We are not interested in those events.
```

Without this, associates may emit too many messages, routes may deliver too
much traffic, and castles may be forced to ignore large amounts of irrelevant
activity.

## Pressure

Richer widgets can produce many kinds of activity:

- focus changes
- key presses
- pointer motion
- selection changes
- scroll activity
- validation events
- edit events
- resize/configure events
- command invocations
- variable changes

Some castles care about only a small subset of those events.

## Open Questions

- Is event interest declared by the associate spec, the castle spec, the route
  spec, or all three?
- Should filtering happen before an associate emits a message?
- Should filtering happen during route delivery?
- Should castles receive everything and explicitly return `rt.IGNORED`?
- What defaults keep simple demos simple?
- Is event interest expressed in terms of raw Tk events, semantic message
  types, or both?

## Possible Shapes

Associate-level interest:

```python
{
    "kind": "associate_spec",
    "name": "search_box",
    "events": ["text_changed", "submitted"],
}
```

Route-level filtering:

```python
{
    "kind": "route_spec",
    "from": {...},
    "to": {...},
    "types": ["text_changed"],
}
```

Castle-level interest:

```python
{
    "kind": "castle_spec",
    "name": "search_castle",
    "interests": ["submitted", "selection_changed"],
}
```

## Current Posture

Do not implement this yet.

Keep the current message flow simple while the core runtime cycle, hierarchy,
replacement, state boundaries, and tests settle. Revisit before the associate
library covers enough Tk widgets to create noisy event streams.

