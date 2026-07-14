# Concepts

This chapter is the whole model in one pass. Later chapters go deeper.

## The runtime is a module

TkMachina's runtime is a module (`tkmachina.rt`) holding global registries in
plain dictionaries and lists: `castles`, `associates`, `routes`, `trace`,
`dirty_castles`, `dirty_associates`, the build queues, and a few `current_*`
targets. The live object system stays visible and inspectable by design. There
is one hidden Tk root (`rt.tk_master`), created withdrawn by
`setup_tk_bootstrap()`.

## Castle

A **castle** is the logical unit of an application: a bounded machine with a
name, owned `state`, an `inbox` and `outbox`, a `handle_fn` (its message
handler / reducer), an optional `reconcile_fn`, its `associates`, its child
castles, and its `spots`. A castle owns application meaning — what a pressed
button means, what state transition should occur, what to project. Outside code
does not reach in and mutate a castle; input arrives through routes into its
inbox, and output leaves as projected widget changes or emitted messages.

Castles may be **headless** (no associates, no surface) — the built-in global
**trace castle** is one such.

## Associate

An **associate** is the companion to one Tk widget (or widget-like resource). It
holds three surfaces:

- **`desired`** — widget-facing state the castle wants projected (e.g.
  `text`, `enabled`).
- **`observed`** — a modeled fact surface about the widget (e.g. `text`,
  `focused`, `actual_width`). Observed fields are maintained *regardless of
  whether a corresponding event is emitted.*
- **`private`** — implementation detail (Tk vars, trace ids, projection
  bookkeeping).

An associate translates raw Tk happenings into **semantic events** placed in its
`outbox`, and projects `desired` onto the widget. It does not decide what an
event *means* — that is the castle's job. `associate["tk"]` is the raw-Tk escape
hatch.

## Event vs. observed fact

TkMachina deliberately separates two kinds of input:

- **Events** are discrete semantic notifications (`button_pressed`, `submitted`).
  They flow outbox -> route -> inbox and are handled on the tick.
- **Observed facts** are present-tense state kept current on the associate.
  Event *interest* controls whether a notification is emitted; it does not
  control whether the observed fact is maintained.

This split is why a castle can read `entry["observed"]["text"]` at any time even
if it never subscribed to `text_changed`.

## Spot and placement

A **spot** is a named place inside a castle where an occupant is placed. A spot's
occupant is either a local **associate** or a mounted **child castle**. Spots
nest (a spot may have child spots), and a branching spot must be occupied by an
associate that can host children. A castle's **placements** map spot names to
occupants. Spots are how embedding and dynamic replacement are modeled.

## Route and message

A **message** (event record) is data: `{kind, type, origin, emitter, payload}`.
A **route** declares that messages from one endpoint's box are delivered to
another endpoint's box — by default, each associate's `outbox` routes to its host
castle's `inbox`, and each child castle's `outbox` routes to its parent castle's
`inbox`. Templates may declare extra routes between associates and castles
(including global castles).

## Build

A castle world is created by a **build**: a `template_fn(build_context)` returns
a spec dict, and the runtime expands it into castle/associate/spot/route records
through an ordered set of phases, then activates it. Builds can also mount a
child castle into a parent's spot, and **structural requests** (clear / build /
replace) let a running castle swap the child castle occupying one of its spots.

## The tick

`runtime_tick()` runs every ~50ms and performs, in order: process incoming
builds, deliver messages, process castle messages (handlers), reconcile dirty
castles, process structural requests, project dirty associates. This is the
heartbeat that turns queued input into state transitions and projected output.

## Trace

The runtime keeps a `trace` list of phase/step strings, and a **global trace
castle** whose `state["entries"]` accumulates application-level trace text (with
a `trace_changed` event on each append). Trace exists because TkMachina's value
depends on the running system being inspectable.
