# TkMachina Discussion Docket

This is the working docket for TkMachina architecture discussions.

Each item has a detailed discussion record in `docs/architecture/decisions`.
This file is the index and status whiteboard: what needs review, what order to
review it in, and what current posture seems reasonable.

## Status Key

- `Open`: needs discussion
- `Accepted`: decision recorded, no immediate implementation required
- `Approved in principle`: direction accepted, implementation work remains
- `Deferred`: real issue, but not next
- `Implemented`: decision has been reflected in the current runtime/docs
- `Rejected`: proposal considered and not adopted

## Whiteboard

| ID | Topic | Status | Priority | Current posture | Discussion record |
| --- | --- | --- | --- | --- | --- |
| ADR-0001 | Runtime Cycle | Implemented | P1 | Castles may provide `reconcile_fn`; dirty castles reconcile before associate projection. | [Runtime Cycle](decisions/ADR-0001-runtime-cycle.md) |
| ADR-0002 | Castle Hierarchy | Implemented, partially superseded by ADR-0012 | P1 | Parent/child castle hierarchy remains; ADR-0012 replaces the older visual `mount`/slot layout framing with spots and placements. | [Castle Hierarchy](decisions/ADR-0002-castle-hierarchy.md) |
| ADR-0003 | Replacement And Dynamic Rebuild | Implemented, clarified by ADR-0012/0013 | P1 | Structural replacement is now expressed as scheduled spot clearing/building/replacement, executed by RT as ordered lifecycle work. | [Replacement And Dynamic Rebuild](decisions/ADR-0003-replacement-dynamic-rebuild.md) |
| ADR-0004 | Associate State Boundaries | Implemented | P2 | Associate state is split into `desired`, `observed`, and `private`; `data` remains only as a transition fallback for `desired`. | [Associate State Boundaries](decisions/ADR-0004-associate-state-boundaries.md) |
| ADR-0005 | Addressing And Scoping | Implemented | P2 | Runtime IDs are live identity; names are local authoring labels; castle `name` is now descriptive `template_name`. | [Addressing And Scoping](decisions/ADR-0005-addressing-scoping.md) |
| ADR-0006 | Message Semantics | Accepted | P3 | Current messages may remain `kind="event"`; richer message kinds wait for a concrete need. | [Message Semantics](decisions/ADR-0006-message-semantics.md) |
| ADR-0007 | Serializable Build Specs | Deferred | P3 | Function refs are fine during thought-object phase; revisit when specs need persistence, diffing, or generation. | [Serializable Build Specs](decisions/ADR-0007-serializable-build-specs.md) |
| ADR-0008 | Lifecycle Hooks | Deferred | P4 | Setup/project/destroy is enough for now; revisit when associates own timers, watchers, processes, or global bindings. | [Lifecycle Hooks](decisions/ADR-0008-lifecycle-hooks.md) |
| ADR-0009 | Runtime Scheduling | Rejected | P4 | Do not replace the fixed runtime heartbeat with conditional tick scheduling without a demonstrated problem. | [Runtime Scheduling](decisions/ADR-0009-runtime-scheduling.md) |
| ADR-0010 | Test Harness | Approved in principle | P2 | Add fake-associate invariant tests and hosted Tk lifecycle tests; implementation to-dos are recorded in `db/tasks.md`. | [Test Harness](decisions/ADR-0010-test-harness.md) |
| ADR-0011 | Event Interest And Filtering | Implemented, minimal | P2 | Associate types declare `default_events`; associate specs may add `events` or suppress with `do_not_listen`; RT computes `effective_events`. | [Event Interest And Filtering](decisions/ADR-0011-event-interest-filtering.md) |
| ADR-0012 | Spots And Placements For Castle Layout | Implemented | P1 | Castles declare beings separately from places: `associates`, `child_castles`, `spots`, and `placements`. | [Spots And Placements For Castle Layout](decisions/ADR-0012-spots-and-placements-for-castle-layout.md) |
| ADR-0013 | Scheduled Mutations Execute As Ordered Lifecycle Operations | Implemented | P1 | Scheduled clearing, building, and replacement execute in queue order as local lifecycle operations. | [Scheduled Mutations Execute As Ordered Lifecycle Operations](decisions/ADR-0013-scheduled-mutations-execute-as-ordered.md) |
| ADR-0014 | Associate Observed State Contract | Implemented | P2 | `observed` is a public modeled-observation surface, not a complete Tk mirror; raw Tk remains an escape hatch. | [Associate Observed State Contract](decisions/ADR-0014-associate-observed-state-contract.md) |

## Next Review Questions

### Test Harness

- Can the runtime be exercised with fake associate types and no Tk root?
- Which invariants should become tests before hierarchy/replacement work?
- Should tests live beside `examples` or under a new test directory?
