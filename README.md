# TkMachina

TkMachina is an experiment in building Tkinter applications as small live
worlds instead of scattered widget callbacks.

It is not a thinner Tkinter. It is a modeled Tkinter.

Raw Tk is good: direct, mature, powerful, and honest. TkMachina is for the
moment when an application wants more visible structure: stateful UI regions,
modeled companions to widgets, semantic events, named layout spots, routes,
projection, and runtime-owned build/teardown.

In raw Tk you often ask:

```text
What widget do I mutate?
```

In TkMachina you ask:

```text
What state changed, what semantic event happened,
and what should be projected?
```

The payoff is not fewer lines. The payoff is a running UI that is more
inspectable, replaceable, routable, and understandable as it grows.

## Core Ideas

- **Castles** are stateful UI regions.
- **Associates** are modeled companions to Tk widgets.
- **Desired** state is what should be projected onto widgets.
- **Observed** state is the associate's public modeled observation surface.
- **Private** state is associate implementation detail.
- **Spots** are named places for associates or child castles.
- **Routes** move semantic messages between outboxes and inboxes.
- **Structural requests** let the runtime clear, build, or replace pieces.

TkMachina does not ban raw Tk. `associate["tk"]` remains available as an
escape hatch for advanced or unmodeled behavior. The aim is that ordinary
behavior should rarely require raw Tk.

## Current Shape

The project currently includes:

- a module-shaped runtime in `src/tkmachina/rt.py`
- associate types for `window`, `frame`, `label_frame`, `button`, `label`,
  and `entry`
- spots and placements for castle-owned layout
- child-castle bubble-up routes
- scheduled clearing/building/replacement
- fake-associate runtime tests
- hosted Tk tests through `tkintertester`
- a living manual in `docs/manual/`

## Manual

The living manual source is in:

```text
docs/manual/
```

There is also an occasional friendly HTML snapshot in:

```text
docs/manual-html/index.html
```

Ordinary documentation updates should go to `docs/manual/`. The HTML snapshot
is refreshed deliberately from time to time.

## Tests

TkMachina currently has two small test tracks.

Runtime invariant tests use fake associate types and do not require real Tk
widgets:

```powershell
$env:PYTHONPATH='src'; python tests/run_runtime_invariants.py
```

Hosted Tk tests use `tkintertester` and run inside the real Tk event loop:

```powershell
$env:PYTHONPATH='src'; python guitests/test_runtime_hosted.py
$env:PYTHONPATH='src'; python guitests/test_entry_associate_hosted.py
```

From `cmd.exe`, run the whole suite:

```bat
run-tests.bat
```

## Examples

Entry associate demo with an inner castle and automatic child-to-parent
bubble-up routing:

```powershell
$env:PYTHONPATH='src'; python examples/entry_inner_castle_demo.py
```
