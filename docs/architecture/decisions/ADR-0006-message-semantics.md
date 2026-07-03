# ADR-0006: Message Semantics

## Discussion Item

Message semantics are still too flat.

Current messages look like:

```python
{
    "kind": "event",
    "type": "button_pressed",
    "origin": associate["name"],
    "emitter": associate["name"],
    "payload": {},
}
```

Associates emit semantic-ish events, which is promising. As the system grows,
it may need clearer distinctions between message kinds:

| Message kind | Meaning |
| --- | --- |
| `event` | something happened |
| `command` | please do something |
| `state_changed` | a model/system value changed |
| `request` | asking another castle/service for work |
| `response` | reply to request |
| `fault` | failure/report |

Right now `trace_changed`, `button_pressed`, and `window_resized` are all
events. That is fine for the demo, but message vocabulary will become important
with:

- child castles
- global service castles
- build requests
- validation errors
- async external process results
- menu actions
- keyboard focus events
- save/load operations

