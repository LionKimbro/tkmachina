# ADR-0009: Runtime Scheduling

## Discussion Item

The runtime tick is still a fixed polling loop.

Current tick:

```python
process_incoming_builds()
deliver_messages()
process_castle_messages()
project_dirty_associates()
tk_master.after(50, runtime_tick)
```

The fixed `after(50, ...)` loop is legible, but probably temporary.

Eventually the runtime may want:

```python
schedule_runtime_tick()
```

Only schedule a tick when there is work:

- incoming builds
- messages
- dirty castles
- dirty associates
- timer events
- external responses

For now, the polling loop makes the machine easy to see.

