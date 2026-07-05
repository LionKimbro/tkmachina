# Glossary

## Active

Runtime state indicating that a castle, associate, spot, or route participates
in ordinary runtime work.

## Associate

A Little-Castles-side companion to a Tk widget or widget-like resource. An
associate owns desired state, modeled observed state, private implementation
state, a concrete widget reference, and an outbox for emitted messages.

## Associate Type

The semantic contract and lifecycle functions for a kind of associate. An
associate type is defined by the Little Castles promise it makes, not only by
the Tk widget it uses internally.

## Build

The runtime-owned process of turning a template and build request into live
castle, associate, spot, route, and widget records.

## Build Request

A request submitted to RT asking it to build a castle from a template,
optionally as a child of an existing castle and optionally into a parent spot.

## Castle

A runtime participant that owns state, an inbox, an outbox, local associates,
child castles, spots, placements, and optional handlers/reconcilers.

## Child Castle

A castle contained by another castle in the logical parent/child hierarchy.
A parent may place a child castle into one of its spots, but may not lay out
through it.

## Desired

`associate["desired"]`. The projection target: values that the castle or RT
wants projected onto the concrete widget.

## Dirty Associate

An associate whose desired state needs projection.

## Dirty Castle

A castle whose state should be reconciled into desired associate state.

## Effective Events

The semantic events an associate instance will emit:

```text
associate_type.default_events
union associate_spec.events
minus associate_spec.do_not_listen
```

## Event

A semantic message describing something that happened, such as
`button_pressed`, `submitted`, or `text_changed`.

## Global Castle

A named castle exposed through RT's global registry. Current examples include
the global trace castle.

## Observed

`associate["observed"]`. The associate's public modeled-observation surface.
It is intentionally maintained by the associate, but it is not a complete
mirror of Tk.

## Outbox

A queue of messages emitted by a castle or associate.

## Placement

Initial or scheduled occupancy of a spot by a local associate or child castle.

## Private

`associate["private"]`. Associate implementation detail such as trace IDs,
private Tk variables, projected-value caches, or suppression flags.

## Projection

The act of applying an associate's desired state to its concrete widget.

## Reconcile

Castle-owned interpretation of castle state into desired associate state.

## Route

A runtime record that moves messages from one outbox to another inbox.

## Spot

A named place in a castle's layout tree.

## Structural Request

A scheduled runtime request to clear, build, or replace spot occupancy.

## Template

A Python callable that returns a castle specification. Templates are class-like:
they describe what should be built, but they are not live castles.
