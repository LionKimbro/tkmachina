# ADR-0001: Runtime Cycle And Optional Castle Reconciliation

## Status

Accepted with changes.

## Context

The current demo castle manually calls `sync_demo_castle_view_state(castle)`
inside message handlers after state changes.

This is simple and explicit, but it requires handlers to remember to call the
sync function after every relevant mutation.

However, not all castles are view/projecting castles. For example, the global
trace castle is headless, has no associates, and still participates
meaningfully in the runtime.

## Decision

A castle is not inherently a view projector.

TkMachina will allow, but not require, a castle to provide an optional
post-message reconciliation function.

This function is not specifically a view sync function. It may reconcile derived
associate state, emit derived messages, update child structures, validate state,
or do nothing.

The tentative name is:

```python
reconcile_fn
```

The intended runtime order is:

1. process incoming builds
2. deliver messages
3. process castle messages
4. reconcile dirty castles that provide `reconcile_fn`
5. project dirty associates

Castle handlers return one of:

- `rt.IGNORED`
- `rt.HANDLED`
- `rt.HANDLED_DIRTY`

Runtime behavior:

- `IGNORED`: do not mark the castle dirty
- `HANDLED`: do not mark the castle dirty
- `HANDLED_DIRTY`: mark the castle dirty
- `None`: treat as `HANDLED_DIRTY` for backward compatibility

## Important Constraint

Headless castles and service castles are valid castles. They do not need
associates and do not need a reconciliation function.

## Implementation Status

Implemented in the demo runtime.
