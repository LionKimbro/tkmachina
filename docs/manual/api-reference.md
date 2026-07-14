# API Reference

Public functions of the module runtime (`tkmachina.rt`) and the associate helpers
(`tkmachina.associates`). Signatures are from the code.

## Runtime lifecycle

| Function | Purpose |
|---|---|
| `setup_tk_bootstrap()` | Create the hidden withdrawn Tk root and the trace castle. Returns `tk_master`. Call before building or `run()`. |
| `run()` | Schedule the first tick and enter the Tk mainloop. |
| `runtime_tick()` | One cycle (see [runtime cycle](runtime-cycle.md)); re-schedules itself every 50ms. |
| `destroy_all()` | Deactivate everything, run destroys child-first, unregister all records. |
| `reset()` | Clear all module registries and id counters to empty (tests / REPL). |

## Builds

| Function | Purpose |
|---|---|
| `make_build_request(template_fn, build_context=None, parent_castle=None, child_name=None, parent_spot=None, activate_when_complete=True)` | Construct a build request. |
| `submit_build_request(request)` | Queue a build request; executed next tick. |

## Structural requests

Target a castle first with `target_castle`, then schedule against a spot name:

| Function | Purpose |
|---|---|
| `target_castle(castle_or_id)` | Set the current target castle for structural helpers. |
| `schedule_clearing(spot_name)` | Clear (destroy) the child castle in a spot. |
| `schedule_building(spot_name, template_fn, build_context=None, child_name=None)` | Build a child castle into an empty spot. |
| `schedule_replacement(spot_name, template_fn, build_context=None, child_name=None)` | Clear then build a spot's child castle. |

## Associates and desired/observed state

| Function | Purpose |
|---|---|
| `target_associate(associate_or_id)` | Set the current target associate. |
| `set_desired(key, value)` | Set a desired field on the target associate; marks dirty only on change; returns changed?. |
| `set_data(key, value)` | Alias for `set_desired`. |
| `get_desired(associate_or_id, key=None, default=None)` | Read desired state (whole dict if `key is None`). |
| `get_observed(associate_or_id, key=None, default=None)` | Read observed facts. |
| `get_associate(castle, associate_name)` | Look up one of a castle's associates by name. |

## Dirty marking

| Function | Purpose |
|---|---|
| `mark_dirty(associate_or_id)` | Queue an associate for projection. |
| `mark_castle_dirty(castle_or_id)` | Queue a castle for reconciliation. |
| `mark_castle_associate_dirty(castle, associate_name)` | Mark one of a castle's associates dirty by name. |

## Trace and global castles

| Function | Purpose |
|---|---|
| `add_trace(text)` | Append a line to the global trace castle (emits `trace_changed`). |
| `get_trace_entries()` | Read the global trace entries. |
| `get_global_castle(name)` | Look up a castle by exported global name. |

## Handler return values

`handle_fn(castle, message)` returns one of the module constants:

| Constant | Effect |
|---|---|
| `rt.IGNORED` | Not handled; castle not marked dirty. |
| `rt.HANDLED` | Handled; castle not marked dirty. |
| `rt.HANDLED_DIRTY` | Handled; castle marked dirty so `reconcile_fn` runs. |
| `None` | Treated as `HANDLED_DIRTY`. |

## Associate helpers (`tkmachina.associates`)

| Function | Purpose |
|---|---|
| `emit_event(associate, event_type, payload=None)` | Append a semantic event to the associate's outbox. |
| `wants_event(associate, event_type)` | Whether the event is in the associate's effective set. |
| `bind_common_widget_events(associate)` | Install the opt-in common widget bindings (focus, pointer, click, key, configure). |
| `WINDOW_ASSOCIATE_TYPE`, `FRAME_ASSOCIATE_TYPE`, `LABEL_FRAME_ASSOCIATE_TYPE`, `BUTTON_ASSOCIATE_TYPE`, `LABEL_ASSOCIATE_TYPE`, `ENTRY_ASSOCIATE_TYPE` | The built-in associate type constants. |

## Inspecting the live world

Because the runtime is a module of plain dicts, these registries are directly
readable (do not mutate them casually): `rt.castles`, `rt.associates`,
`rt.routes`, `rt.trace`, `rt.dirty_castles`, `rt.dirty_associates`,
`rt.global_castles`, and the build lists (`rt.incoming_builds`,
`rt.active_builds`, `rt.completed_builds`, `rt.faulty_builds`).
