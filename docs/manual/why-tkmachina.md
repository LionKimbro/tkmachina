# Why Use TkMachina?

TkMachina is not a replacement for Tkinter.

It is a way to build Tkinter applications as small live worlds made of castles,
associates, spots, routes, messages, and projected state.

Raw Tk is good. It is direct, mature, powerful, and honest. Use raw Tk when you
want to directly operate widgets and the direct code is still clear.

TkMachina is for the point where you want more of the running application to be
modeled.

## Raw Tk Is Good

Use raw Tk when direct widget programming is enough:

- small scripts
- one-window tools
- simple callback apps
- quick utility GUIs
- direct widget manipulation

TkMachina is not trying to be the shortest path to a button. A raw Tk button is
already short.

## The Problem TkMachina Solves

As Tkinter applications grow, meaning can become spread across:

- widget variables
- callbacks
- closures
- bindings
- manual `config(...)` calls
- implicit layout relationships
- explicit `destroy(...)` calls
- side effects

That can be fine for a while. Eventually, though, the running application can
become hard to inspect, replace, route, or reason about.

TkMachina tries to centralize application meaning into:

- castle state
- associate desired state
- associate observed state
- semantic events
- spots and placements
- routes
- reconciliation
- projection
- structural requests

Raw Tk asks:

```text
What widget do I mutate?
```

TkMachina asks:

```text
What state changed, what semantic event happened,
and what should be projected?
```

## What TkMachina Adds

TkMachina adds a visible runtime model.

Castles are stateful UI regions.

Associates are modeled companions to widgets.

`desired` is widget-facing state to project.

`observed` is the associate's modeled observation surface.

`private` is associate implementation detail.

Events are semantic messages.

Spots are named places where associates or child castles can be placed.

Routes move messages between outboxes and inboxes.

Structural requests let the runtime clear, build, or replace spot occupancy.

## The Cost

TkMachina adds machinery.

It is not a thinner Tkinter. It is a modeled Tkinter.

If you want the smallest possible Tk script, or a tiny throwaway dialog, raw Tk
is probably clearer.

## The Payoff

The payoff is not fewer lines.

The payoff is that the running UI becomes more inspectable, replaceable,
routable, and understandable as a system.

Use TkMachina when:

- your UI has regions that should be built, cleared, or replaced as units
- you want events to be semantic messages instead of scattered callbacks
- you want desired widget state to be inspectable data
- you want observed widget facts to have a public modeled surface
- you want child UI regions to be castles, not arbitrary frames
- you want destruction and cleanup to be part of the runtime model
- you want to reduce routine reasons to touch raw Tk widgets

Do not use TkMachina if:

- you want the smallest possible Tk script
- you are building a simple throwaway dialog
- you already enjoy direct widget-callback code
- you need every obscure Tk feature immediately modeled
- you do not want a runtime layer

## Raw Tk Remains Available

TkMachina does not prevent raw Tk access.

`associate["tk"]` remains available as an escape hatch for advanced, unusual,
or unmodeled behavior.

The goal is different:

```text
ordinary behavior should rarely require raw Tk
```

If authors routinely need raw Tk for ordinary behavior, that is evidence the
associate type is under-modeled.

If authors need raw Tk for rare, advanced, or widget-specific behavior, that is
acceptable.
