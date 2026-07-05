# ADR-0013: Scheduled Mutations Execute as Ordered Lifecycle Operations

Status: Implemented

Date: 2026-07-04

## Context

tkMachina supports runtime-owned construction and destruction of castles.

A castle may be built from a template. A castle may contain layout spots where child castles can be placed. A template may define child castles to be built automatically, or it may leave spots open for later placement.

The runtime also supports scheduled mutation. A caller may schedule a castle to be cleared, built, or replaced. These scheduled mutations do not necessarily happen immediately. They are collected and later committed by the runtime.

Earlier thinking leaned toward a two-phase mutation model:

```text
1. perform all clearing/destruction
2. perform all building/construction
```

This had an appealing simplicity. It created a distinct period in which destruction happened, followed by a distinct period in which construction happened. It also seemed to make existence easy to reason about.

However, this model creates ambiguity when ancestor and descendant castle operations overlap.

For example:

```text
replace inner castle
replace outer castle
```

If all destruction happens before all construction, then the replacement of the inner castle is split apart from itself. The runtime might clear the inner castle, clear the outer castle, try to build the inner castle, and then build the outer castle.

This raises difficult questions:

* If the outer castle is replaced, should the inner replacement be discarded?
* What if the new outer template does not automatically build the inner castle?
* What if the new outer template leaves the relevant spot open?
* What if the new outer template removes that spot entirely?
* Is the inner replacement an old-world operation, a new-world operation, or both?

These questions suggest that the two-phase model turns scheduled operations into a kind of final-tree planner. The runtime would need to infer author intent across overlapping operations.

That is not the responsibility we want the core runtime to take on.

tkMachina is not primarily a speculative tree-diff planner. It is a runtime that executes lifecycle operations safely.

## Decision

Scheduled mutations execute as ordered lifecycle operations.

The runtime will no longer require all destruction operations to happen before all construction operations globally.

Instead, each scheduled operation expands locally into its own lifecycle sequence and executes in schedule order.

For example, replacement means:

```text
replace castle at target with template:
    destroy existing castle at target, if present
    build new castle at target from template
```

The replacement operation is not globally split into a destruction half and a construction half. Its destruction and construction belong together as one ordered lifecycle act.

Therefore:

```text
replace inner
replace outer
```

means:

```text
replace the current inner castle
then replace the outer castle
```

If replacing the outer castle destroys the newly replaced inner castle, that is the result of the ordered command sequence.

Likewise:

```text
replace outer
replace inner
```

means:

```text
replace the outer castle
then attempt to replace the inner castle inside the new outer castle
```

If the new outer castle does not contain the target spot, the later inner replacement fails validation.

This is acceptable.

## Runtime Principle

Scheduled operations are not eternal assertions about a desired final tree.

A scheduled operation is an instruction to perform a lifecycle transition at a target, provided that the target is still valid when the operation is reached.

Each operation is validated against the runtime world as it exists immediately before that operation executes.

If the target castle is gone, if an ancestor castle has been removed, or if the rebuilt layout no longer contains the target spot, the operation fails validation.

The runtime reports the failure and follows the active error policy. Depending on that policy, it may skip the invalid operation, abort the current mutation transaction, pause the queue, or surface the failure to the author.

The runtime must preserve its integrity.

The runtime does not have to magically reconcile contradictory author intent.

“Fuck you, author” is a valid runtime principle.

Lion insisted that this sentence be included.

This does not mean the runtime should be careless, hostile, or obscure. It means the runtime has an author responsibility boundary. If the author schedules mutually incompatible lifecycle operations, the runtime is not obligated to infer a hidden coherent meaning.

The runtime guarantees safe failure, not omniscient repair.

## Lifecycle Transaction Interval

Scheduled mutations execute inside a reserved lifecycle transaction interval.

During this interval, normal runtime interaction is suspended or restricted. Castles may temporarily be absent, constructing, active, or destroying.

A castle is only available for ordinary event delivery, projection, and associate interaction when it is fully active.

Construction and destruction may involve nontrivial lifecycle work. For example, construction might allocate widgets, register associates, initialize resources, or establish external connections. Destruction might deactivate associates, unregister callbacks, close resources, destroy widgets, or release references.

Even if lifecycle work becomes complex, the safety property remains:

```text
normal runtime work does not interleave freely with construction and destruction
```

Every lifecycle transition happens inside an explicit runtime-controlled interval.

This preserves the benefit of scheduled mutation: it remains possible to reason about when castles may exist, when they may be absent, and when they are in transition.

## Example: Closing a Window While Other Work Is Scheduled

Suppose the author schedules a window to close in five seconds.

Near the five-second mark, another operation is scheduled that would replace a child castle inside that window.

The close operation executes first:

```text
close outer window
```

Then the child replacement operation is reached:

```text
replace child inside outer window
```

But the outer window is gone.

The runtime validates the target path, sees that it is no longer valid, and reports an error such as:

```text
Err: cannot replace child castle; ancestor castle no longer exists
```

The operation fails safely.

The runtime remains coherent.

Life goes on.

This is preferable to silently resurrecting the window, moving the child operation somewhere else, preserving the child operation as a speculative future intent, or attempting to infer what the author “really meant.”

## Consequences

### Positive Consequences

This decision preserves the local meaning of replacement.

A replacement operation means:

```text
destroy old thing here
build new thing here
```

It is not split apart by unrelated operations elsewhere in the schedule.

Operation order becomes semantically meaningful. Authors can express different meanings by scheduling operations in different orders.

The runtime becomes simpler. It executes an ordered lifecycle script instead of attempting to normalize an entire final desired castle tree.

Failure behavior becomes clearer. If a later operation targets something that no longer exists, that operation fails validation.

This also fits the living-runtime nature of tkMachina. Operations may be scheduled at different times by different causes. The runtime should execute them safely in order, not pretend that all scheduled work forms a perfectly coherent final design.

### Negative Consequences

Authors can schedule wasteful or self-defeating operations.

For example:

```text
replace inner
replace outer
```

may replace the inner castle and then immediately destroy it when the outer castle is replaced.

This is acceptable.

Authors can also schedule operations that fail because earlier operations removed their targets.

This is also acceptable.

The runtime must have good diagnostics. Safe failure is not enough if failures are invisible or confusing.

The runtime must define an error policy for failed scheduled operations.

Possible policies include:

```text
log and continue
abort current transaction
pause the mutation queue
raise to author
enter recovery mode
```

The exact policy may vary by runtime mode.

## Non-Goals

This ADR does not require the runtime to compute an optimal tree edit plan.

This ADR does not require the runtime to preserve descendant construction intent across ancestor replacement.

This ADR does not require the runtime to infer whether a child operation should apply to the old ancestor castle or the rebuilt ancestor castle.

This ADR does not forbid a future higher-level planner, linter, or schedule normalizer.

Such a tool may be useful later. It could detect suspicious overlapping operations, warn the author, or rewrite a batch of desired final assertions into an ordered lifecycle script.

But that belongs above the core runtime.

The core runtime executes ordered lifecycle operations safely.

## Summary

Scheduled castle mutations execute in order as lifecycle operations.

Replacement remains local:

```text
destroy target
build target
```

Operations are validated when reached.

If the world has changed and the target is no longer valid, the operation fails safely.

The runtime guarantees lifecycle safety, not magical reconciliation of contradictory author commands.

---

[^1]: Lion Kimbro apologizes to Codex for changing his mind so many times. This ADR reflects the latest correction in the design trail, not a failure of Codex. The castle laws were still being discovered.
