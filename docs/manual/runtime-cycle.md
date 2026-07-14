# The Runtime Cycle

TkMachina runs a hidden Tk root and a periodic tick that turns queued input into
state transitions and projected output.

## Bootstrap

```python
from tkmachina import rt

rt.setup_tk_bootstrap()   # create the hidden, withdrawn Tk root; set up the trace castle
# ... submit an initial build ...
rt.run()                  # schedule the first tick and enter the Tk mainloop
```

`setup_tk_bootstrap()` creates `tk_master = tk.Tk()`, withdraws it, and sets up
the global trace castle. It must be called before any build or `run()`. `run()`
schedules `runtime_tick` via `tk_master.after(0, ...)` and enters `mainloop()`.

## The tick

`runtime_tick()` runs the following phases in order, then re-schedules itself with
`tk_master.after(50, runtime_tick)` (~20 Hz):

```text
1. process_incoming_builds     # execute submitted build requests
2. deliver_messages            # move outbox messages to inbox boxes via routes
3. process_castle_messages     # drain each active castle's inbox -> handle_fn
4. reconcile_dirty_castles     # reconcile_fn(castle) for dirty castles
5. process_structural_requests # clear / build / replace spot occupants
6. project_dirty_associates    # project_fn(associate) for dirty associates
```

Ordering matters:

- Handlers run after delivery, so a message emitted this tick is handled next
  tick (one-tick pipeline).
- Reconcile runs after handlers, so it sees the post-message state.
- Structural changes apply after reconcile and before projection, so newly built
  associates project in the same tick they are constructed (construction marks
  them dirty).
- Projection runs last, so widgets reflect the settled state of the tick.

## Dirty tracking

Work is driven by two dirty sets:

- `dirty_castles` — reconciled and cleared in phase 4. A castle becomes dirty
  when its `handle_fn` returns `HANDLED_DIRTY` (or `None`), or via
  `rt.mark_castle_dirty`.
- `dirty_associates` — projected and cleared in phase 6. An associate becomes
  dirty on construction, on `rt.set_desired` (when the value changes), or via
  `rt.mark_dirty`.

Only `active` castles/associates are processed; inactive ones are skipped.

## Ending the app

There is no separate shutdown policy object. A `window` associate binds
`WM_DELETE_WINDOW` to call `rt.destroy_all()` and then destroy the Tk root, which
ends `mainloop()`. So closing a window-owned application tears the runtime down
and exits.

`rt.destroy_all()` deactivates all routes/castles/associates, clears the queues,
revokes global exports, runs every associate's `destroy_fn` (child-first), and
unregisters all records. `rt.reset()` clears the module registries back to empty
(useful for tests and REPL sessions).
