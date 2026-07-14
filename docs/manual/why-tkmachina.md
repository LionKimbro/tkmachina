# Why TkMachina?

TkMachina is not a replacement for Tkinter. It is a way to build Tkinter
applications as small live worlds of castles, associates, spots, routes,
messages, and projected state.

Raw Tk is good — direct, mature, honest. Use it for small scripts, one-window
tools, and quick utilities where direct widget code stays clear. TkMachina is
for the point where you want more of the *running* application to be modeled and
inspectable.

## The problem it solves

As a Tkinter app grows, meaning scatters across widget variables, callbacks,
closures, bindings, `config(...)` calls, implicit layout, and `destroy(...)`
calls. That is fine for a while, then the running application becomes hard to
inspect, route, replace, or reason about.

Raw Tk asks: *what widget do I mutate?*

TkMachina asks: *what state changed, what semantic event happened, and what
should be projected?*

## What it adds

- **Castles** — bounded, stateful UI regions that own application meaning.
- **Associates** — modeled companions to widgets, with `desired` (what to
  project), `observed` (modeled facts), and `private` (implementation) surfaces.
- **Semantic events** — user and UI happenings become data records before they
  become behavior.
- **Spots and placements** — named places where associates or child castles are
  placed, so embedding and replacement are first-class, not frame tricks.
- **Routes and queues** — messages move along declared paths into inboxes, and
  are processed on the tick.
- **A global trace** — an inspectable history of what happened.

## The structural laws

TkMachina keeps a few distinctions sacred:

```text
Layout is not logic.
A widget is not an application object; its associate mediates.
A button is not behavior; it is an input port.
Projection (desired state -> widget) is separate from application state.
A castle does not expose its interior to arbitrary external mutation.
```

## The cost and the payoff

The cost is machinery: TkMachina is a modeled Tkinter, not a thinner one. The
payoff is not fewer lines — it is that the running UI becomes inspectable,
replaceable, routable, and understandable as a system.

Raw Tk remains available as an escape hatch through `associate["tk"]`. The goal:
*ordinary behavior should rarely require raw Tk.* If authors routinely need raw
Tk for ordinary behavior, that is evidence the associate type is under-modeled.

Do not use TkMachina for the smallest possible Tk script, a throwaway dialog, or
if you simply enjoy direct widget-callback code. Use it when your UI has regions
to build/clear/replace as units, when you want events to be semantic messages
instead of scattered callbacks, and when you want the running application to be
data you can inspect.
