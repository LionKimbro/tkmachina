# ADR-0011: Event Interest And Filtering

## Status

Approved for minimal implementation.

## Guidance

As TkMachina grows broader coverage over the Tkinter widget set, associates
must not emit every possible semantic event by default.

Richer widgets can produce many kinds of activity: focus changes, key presses,
pointer motion, selection changes, scroll activity, validation events, edit
events, resize/configure events, command invocations, variable changes, and
more.

Some castles care about only a small subset of those events.

TkMachina therefore needs a simple event-interest system.

## Decision

Event interest is declared primarily at the associate level.

Each associate type may define events that are enabled by default:

```python
{
    "name": "button",
    "default_events": ["button_pressed"],
    ...
}
```

Each associate instance may explicitly enable additional semantic events:

```python
{
    "kind": "associate_spec",
    "name": "search_box",
    "associate_type": ENTRY_ASSOCIATE_TYPE,
    "events": ["text_changed", "submitted"],
}
```

Each associate instance may also explicitly suppress events, including events
that would otherwise be enabled by default:

```python
{
    "kind": "associate_spec",
    "name": "main_window",
    "associate_type": WINDOW_ASSOCIATE_TYPE,
    "do_not_listen": ["window_resized"],
}
```

The effective event set for an associate is:

```text
effective_events =
    associate_type.default_events
    union associate_spec.events
    minus associate_spec.do_not_listen
```

In Python terms:

```python
effective_events = (
    set(associate_type.get("default_events", []))
    | set(associate_spec.get("events", []))
) - set(associate_spec.get("do_not_listen", []))
```

Associate setup functions should bind/listen only for events in the
associate's effective event set.

## Semantics

`default_events` belongs to the associate type.

It expresses the ordinary, expected semantic events for that kind of associate.

For example, a button normally emits `button_pressed`. A basic window associate
may normally emit `window_resized`. A text entry might default only to
`submitted`, while requiring explicit opt-in for noisy events such as
`text_changed`.

`events` belongs to the associate instance.

It expresses additional semantic events this particular associate wants
enabled.

`do_not_listen` also belongs to the associate instance.

It forcibly disables semantic events for this particular associate, even if
those events were enabled by the associate type's defaults.

## Defaults

Simple demos should remain simple.

A normal button should not require event configuration just to emit
`button_pressed`.

Noisy events should generally not be default-enabled unless they are essential
to the identity of the associate type.

Examples of noisy or optional events include:

```text
pointer_moved
key_pressed
focus_changed
text_changed
scroll_changed
selection_changed
```

These should usually require explicit opt-in from the associate spec.

## Filtering Location

Filtering should happen as early as practical.

Associates should avoid binding to raw Tk events and avoid emitting semantic
messages unless those semantic events are in their effective event set.

This avoids unnecessary message traffic and prevents castles from being forced
to ignore floods of irrelevant activity.

Route-level filtering may still be added separately:

```python
{
    "kind": "route_spec",
    "from": {...},
    "to": {...},
    "types": ["text_changed"],
}
```

If route-level filtering exists, it controls delivery, not emission.

The distinction is:

```text
associate event interest controls what gets emitted
route type filtering controls what gets delivered
castle handlers control what gets interpreted
```

## Deferred

Castle-level interest declarations are deferred.

For now, if a castle receives a message, it may handle it or return
`rt.IGNORED`.

The system should not introduce a third filtering layer until there is a
concrete need.

## Raw Tk Events vs. Semantic Events

Event interest should be expressed in semantic TkMachina message types, not raw
Tk event names.

For example:

```text
text_changed
submitted
button_pressed
window_resized
selection_changed
```

not:

```text
<KeyRelease>
<Return>
<Button-1>
<Configure>
<<TreeviewSelect>>
```

Associate types remain responsible for translating raw Tk activity into
semantic TkMachina messages.

## Consequences

Associates avoid producing unwanted event traffic.

Simple widgets remain simple.

Noisy widgets become controllable.

Castles are not forced to ignore large volumes of irrelevant messages.

Route filtering can still be used later to direct different subsets of one
source's messages to different destinations.

The implementation remains small and practical while preserving room for richer
event routing later.
