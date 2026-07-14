# Glossary

Terms as used in the code. Cross-references point to the chapter that defines
each in depth.

**Active** — a castle, associate, spot, or route becomes active at build
activation. Only active castles/associates are processed by the tick.

**Associate** — the modeled companion to one Tk widget. Holds `desired`,
`observed`, and `private` surfaces, emits semantic events, and projects desired
state. See [associates](associates.md). (Historically called a "Lady".)

**Associate type** — a dict of flags and lifecycle functions
(`setup_fn`, `project_fn`, `destroy_fn`, `default_events`, `can_host_children`,
`embeddable`) shared by all associates of that kind. See
[associate reference](associate-reference.md).

**Build** — the process that expands a template into castle/associate/spot/route
records and activates them. See [builds](builds.md).

**Build request** — a queued instruction to run a build, optionally mounting the
result into a parent castle's spot.

**Castle** — a bounded state machine that owns application meaning: state, a
handler, an optional reconcile function, associates, child castles, and spots.
See [castles](castles.md).

**Child castle** — a castle mounted as an occupant of another castle's spot.

**Desired** — an associate's widget-facing projection target (e.g. `text`,
`enabled`). Set via `rt.set_desired`.

**Dirty** — marked for work this tick: dirty castles are reconciled, dirty
associates are projected.

**Effective events** — the events an associate actually emits:
`default_events | spec.events - spec.do_not_listen`.

**Emitter / origin** — identity fields on an event record naming who produced it.

**Event (message / event record)** — a semantic data record
(`{kind, type, origin, emitter, payload}`) that moves along routes into castle
inboxes. See [routes and messages](routes-and-messages.md).

**Global castle** — a castle registered under a global name via `exports`,
addressable as a route endpoint. The built-in `global_trace` castle is one.

**Headless castle** — a castle with no associates/surface (e.g. the trace
castle).

**Inbox / outbox** — a castle has both; an associate has an outbox. Routes move
messages from outboxes to inboxes.

**Observed** — an associate's public, present-tense fact surface, maintained
regardless of whether an event is emitted. Read via `rt.get_observed`.

**Placement** — a castle's mapping of spot name to occupant
(`{kind: "associate" | "child_castle", name}`). See [spots](spots.md).

**Private** — an associate's implementation detail (Tk vars, trace ids,
projection bookkeeping); not part of the public contract.

**Projection** — applying `desired` onto the concrete widget via the type's
`project_fn`, diffing so it only reconfigures on change.

**Reconcile (`reconcile_fn`)** — an optional per-castle derived pass run after
message handling for dirty castles.

**Route** — a declared delivery path from one endpoint box to another. Default
routes wire associate outboxes to their host castle and child castles to their
parents. See [routes and messages](routes-and-messages.md).

**Runtime (`rt`)** — the module holding all registries and the tick loop. The
system is deliberately a module of plain dicts so the live world is inspectable.

**Spot** — a named place inside a castle occupied by an associate or a child
castle; spots nest. Replaces the older "slot". See [spots](spots.md).

**Structural request** — a queued `clearing`, `building`, or `replacement` of a
spot's occupant, executed on the tick.

**Tick (`runtime_tick`)** — the ~50ms cycle: process builds, deliver messages,
process castle messages, reconcile dirty castles, process structural requests,
project dirty associates. See [the runtime cycle](runtime-cycle.md).

**Trace** — the inspectable history: the low-level `rt.trace` list of phase
strings, and the application-level global trace castle
(`rt.add_trace` / `rt.get_trace_entries`).

**tk_master** — the single hidden, withdrawn Tk root created by
`setup_tk_bootstrap`.
