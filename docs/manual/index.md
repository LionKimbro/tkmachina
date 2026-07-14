# TkMachina Manual

TkMachina is a Tkinter-backed GUI runtime. Interface regions are modeled as
**castles** (bounded state machines), each widget is tended by an **associate**
(a modeled companion that projects desired state and translates raw Tk activity
into semantic events), and everything communicates through **queues** and
**routes** driven by a periodic **runtime tick**.

This manual is regenerated from the code (`src/tkmachina/rt.py`,
`src/tkmachina/associates.py`). Where a statement here disagrees with the code,
the code is right and this manual is stale.

## Start here

- [Why TkMachina?](why-tkmachina.md) — when to use it and what it buys you.
- [Concepts](concepts.md) — the whole model in one pass.

## Conceptual chapters

- [Castles](castles.md) — bounded state machines: state, handlers, reconcile.
- [Associates](associates.md) — widget companions: `desired`, `observed`, `private`, events.
- [Spots and placements](spots.md) — where associates and child castles are placed.
- [Routes and messages](routes-and-messages.md) — how event records move.
- [Builds and structural changes](builds.md) — templates, build phases, dynamic replacement.
- [The runtime cycle](runtime-cycle.md) — bootstrap, the tick, teardown.

## Reference

- [Associate reference](associate-reference.md) — the built-in associate types.
- [API reference](api-reference.md) — the public `rt` and `associates` functions.
- [Glossary](glossary.md) — terms in one place.

## The shape of an interaction

Every user interaction follows the same path, and the manual is organized around
it:

```text
raw Tk happening
  -> the widget's associate translates it
  -> associate emits a semantic event into its outbox
  -> routes deliver the event to a castle inbox
  -> the castle's handler updates owned state
  -> the castle sets desired state on its associates
  -> dirty associates project desired state onto widgets
  -> the trace records the path
```

## Status

The runtime, the six core associate types (`window`, `frame`, `label_frame`,
`button`, `label`, `entry`), spots, routes, builds, structural replacement, the
global trace castle, and the tick loop are implemented. Text-, Treeview-, and
Canvas-backed associate families are not yet implemented.
