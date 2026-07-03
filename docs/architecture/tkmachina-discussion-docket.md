# TkMachina Discussion Docket

This is the working docket for TkMachina architecture discussions.

Each item has a detailed discussion record in `docs/architecture/decisions`.
This file is the index and status whiteboard: what needs review, what order to
review it in, and what current posture seems reasonable.

## Status Key

- `Open`: needs discussion
- `Leaning`: likely direction exists, but not decided
- `Decided`: decision recorded
- `Deferred`: real issue, but not next

## Review Order

1. Runtime cycle
2. Castle hierarchy
3. Replacement and dynamic rebuild
4. Associate state boundaries
5. Addressing and scoping
6. Test harness
7. Event interest and filtering
8. Message semantics
9. Serializable build specs
10. Lifecycle hooks
11. Runtime scheduling

## Whiteboard

| ID | Topic | Status | Priority | Current posture | Discussion record |
| --- | --- | --- | --- | --- | --- |
| ADR-0001 | Runtime Cycle | Decided | P1 | Accepted with changes: castles may optionally provide `reconcile_fn`; dirty castles reconcile before associate projection. | [Runtime Cycle](decisions/ADR-0001-runtime-cycle.md) |
| ADR-0002 | Castle Hierarchy | Decided | P1 | Accepted: parent/child castles attach through named slots, and visible children may mount a root associate into parent UI. | [Castle Hierarchy](decisions/ADR-0002-castle-hierarchy.md) |
| ADR-0003 | Replacement And Dynamic Rebuild | Open | P1 | Generalize teardown/build pieces into slot replacement and subtree lifecycle operations. | [Replacement And Dynamic Rebuild](decisions/ADR-0003-replacement-dynamic-rebuild.md) |
| ADR-0004 | Associate State Boundaries | Open | P2 | Split associate data into desired, observed, and private state before the single `data` bag gets muddy. | [Associate State Boundaries](decisions/ADR-0004-associate-state-boundaries.md) |
| ADR-0005 | Addressing And Scoping | Open | P2 | Prefer ids internally, names locally, and paths/global addresses at boundaries. | [Addressing And Scoping](decisions/ADR-0005-addressing-scoping.md) |
| ADR-0006 | Message Semantics | Open | P3 | Keep current event shape for now, but define vocabulary before services, async work, and child castles proliferate. | [Message Semantics](decisions/ADR-0006-message-semantics.md) |
| ADR-0007 | Serializable Build Specs | Deferred | P3 | Function refs are fine during thought-object phase; revisit when specs need persistence, diffing, or generation. | [Serializable Build Specs](decisions/ADR-0007-serializable-build-specs.md) |
| ADR-0008 | Lifecycle Hooks | Deferred | P4 | Setup/project/destroy is enough for now; revisit when associates own timers, watchers, processes, or global bindings. | [Lifecycle Hooks](decisions/ADR-0008-lifecycle-hooks.md) |
| ADR-0009 | Runtime Scheduling | Deferred | P4 | Keep fixed polling while the machine is still being made visible. | [Runtime Scheduling](decisions/ADR-0009-runtime-scheduling.md) |
| ADR-0010 | Test Harness | Open | P2 | Add fake-associate runtime tests soon so invariants guide the next architecture changes. | [Test Harness](decisions/ADR-0010-test-harness.md) |
| ADR-0011 | Event Interest And Filtering | Open | P2 | As widget coverage grows, associates/castles need a way to declare which raw or semantic events they care about. | [Event Interest And Filtering](decisions/ADR-0011-event-interest-filtering.md) |

## Next Review Questions

### Replacement And Dynamic Rebuild

- Is replacement a specialized build request or a separate request type?
- What is the exact failure behavior if destroy succeeds but rebuild fails?
- Should replacement preserve slot address, layout position, or both?

### Associate State Boundaries

- Are `desired`, `observed`, and `private` the right names?
- Do associate event handlers write `observed` directly, or only emit messages?
- Which state belongs in the castle versus the associate?

### Addressing And Scoping

- What are the minimum address forms needed beyond parent/child slots?
- Are global exports enough for out-of-build addressing right now?
- When should path syntax become explicit?

### Test Harness

- Can the runtime be exercised with fake associate types and no Tk root?
- Which invariants should become tests before hierarchy/replacement work?
- Should tests live beside `examples` or under a new test directory?

### Event Interest And Filtering

- Should event interest be declared on associate specs, castle specs, route
  specs, or some combination?
- Should filtering happen before message creation, before route delivery, or at
  castle handling time?
- How should default event interest work for simple demos?
