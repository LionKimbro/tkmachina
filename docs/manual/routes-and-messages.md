# Routes and Messages

Behavior in TkMachina moves as **messages** (event records) along declared
**routes** from one endpoint's box to another's, and is processed on the tick.
Nothing calls arbitrary application code directly.

## Messages (event records)

A message is a plain dict:

```python
{
    "kind": "event",
    "type": "button_pressed",
    "origin": "priority_button",   # where it originated
    "emitter": "priority_button",  # the declared emitter identity
    "payload": {...},              # event-specific data (may be empty)
}
```

Associates emit via `associates.emit_event(associate, type, payload)`, which
appends to the associate's `outbox`. Castles emit by appending an event record to
their own `outbox` (as the global trace castle does with `trace_changed`).

## Boxes

Every castle and associate has an `outbox`; every castle has an `inbox`. Routes
move messages from a source's box to a destination's box. Endpoints are addressed
by `(kind, id, box)` where `kind` is `"associate"` or `"castle"`.

## Default routes

`wire_default_routes` creates, for each build:

- one route per associate: that associate's `outbox` -> its **host castle's**
  `inbox`;
- one route per child castle: that castle's `outbox` -> its **parent castle's**
  `inbox`.

So by default, a widget's events land in its own castle, and a child castle's
emissions bubble up to its parent.

## Template routes

A castle spec may declare extra `routes`:

```python
"routes": [
    {"from": {"kind": "associate", "name": "file_list", "box": "outbox"},
     "to":   {"kind": "castle",    "name": "inspector",  "box": "inbox"}},
]
```

Endpoint `kind` may be:

- `"associate"` — resolved by name within the build;
- `"castle"` — resolved by `template_name` within the build;
- `"global_castle"` — resolved by exported global name (see below).

## Global castles and exports

A castle spec may export itself under a global name:

```python
"exports": [{"name": "app_trace", "target": {"kind": "castle", "template_name": "context_panel"}}]
```

Exported names live in `rt.global_castles` and can be used as
`{"kind": "global_castle", "name": "app_trace", "box": "inbox"}` route endpoints,
letting unrelated builds route to a well-known castle (the built-in
`global_trace` castle is always available). Exports are revoked when the castle is
destroyed.

## Delivery on the tick

`deliver_messages` (early in each tick) groups active routes by source box,
drains each source box once, and appends a copy of each message to every matching
destination box (payload is shallow-copied). Fan-out is natural: two routes from
the same box each receive a copy. Delivered messages then wait in castle inboxes
until `process_castle_messages` runs later in the same tick.

Routes are inactive until their build is activated, and are removed when their
build fails or their castles are destroyed.
