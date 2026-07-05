# ADR-0014: Associate Observed State Contract

## Status

Implemented

## Context

ADR-0004 split associate state into three dictionaries:

```python
associate["desired"]
associate["observed"]
associate["private"]
```

That split raises an important boundary question:

```text
Is observed public Little Castles runtime state, private widget bookkeeping,
or a complete mirror of Tk?
```

TkMachina's larger design aim is that castle authors should almost never need
to inspect raw Tk widgets for ordinary behavior. Associates exist as the
Little-Castles-side companions to Tk widgets. They project desired state, model
ordinary observed facts, translate selected widget activity into semantic
messages, and keep most Tk machinery behind the associate boundary.

If `observed` exists, it should not be a half-promise. It should be meaningful
for castle authors to read. But it should also not imply that the associate
mirrors every raw Tk property, quirk, and widget-specific behavior.

## Decision

`associate["observed"]` is a public modeled-observation surface, not a complete
mirror of Tk.

Each associate type defines which observed fields it intentionally maintains.

Those fields should be reliable regardless of whether corresponding events are
emitted.

Event interest controls notification, not whether modeled observed state is
maintained.

Associates should model ordinary semantic facts so authors rarely need raw Tk
access.

Raw Tk access remains an escape hatch for advanced, unusual, or unmodeled
behavior.

If authors repeatedly need raw Tk for a common use case, that is a signal to
add a modeled desired field, observed field, or event to the associate type.

The fields have the following intended ownership:

```text
desired:
  public-ish, castle/RT-authored target state

observed:
  public, associate-authored modeled observation

private:
  not public, associate implementation detail
```

Castle authors may read modeled observed facts such as:

```python
entry["observed"]["text"]
entry["observed"]["focused"]
```

That does not mean every possible Tk fact is represented in `observed`.

Castle authors should not generally write `observed`. If a castle needs to
remember or interpret observed reality, it should store that interpretation in
castle state.

## Event Interest Is Not Observation

ADR-0011 controls message emission. It does not decide whether observed state
is maintained.

For example, an Entry associate should keep:

```python
associate["observed"]["text"]
```

current even when the associate has not opted into emitting `text_changed`
messages.

The distinction is:

```text
observed state:
  modeled widget facts the associate intentionally maintains

event interest:
  which semantic messages the associate should emit
```

Therefore private Tk machinery may be installed to maintain `observed` state
even when the corresponding semantic event is not in `effective_events`.

## Consequences

Associates may use private resources, such as `StringVar` traces or Tk event
bindings, to keep observed state current.

Those resources must be managed as private associate resources. They should be
stored in `associate["private"]`, cleaned up by the associate `destroy_fn`, and
not left to widget destruction by accident when explicit cleanup is available.

Event-interest filtering still matters. It controls whether the associate emits
messages, not whether the associate maintains the observed fields it claims to
model.

This keeps the Little Castles surface data-focused for ordinary behavior:
castle code should usually read modeled associate state, not raw Tk widget
methods.

Raw Tk access is still allowed through `associate["tk"]`.

If users routinely need raw Tk for ordinary behavior, that is evidence the
associate type is under-modeled.

If users need raw Tk for rare, advanced, or widget-specific behavior, that is
acceptable.
