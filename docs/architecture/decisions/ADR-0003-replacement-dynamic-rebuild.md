# ADR-0003: Replacement And Dynamic Rebuild

## Discussion Item

There is no replacement or dynamic rebuild protocol yet.

The runtime has build, cleanup on failed build, and `destroy_all()`. It does not
yet have a slot-level operation like:

```text
Remove the castle/associate subtree currently in this slot, then build a new
subtree there.
```

That operation is central to the idea that templates make dynamic structure
easy.

Possible runtime requests:

```python
submit_replace_slot_request(parent_castle, slot, template_fn, build_context)
submit_destroy_castle_request(castle_id)
```

The missing phases are:

1. deactivate old subtree
2. disconnect routes
3. destroy widgets child-first
4. unregister records
5. build new subtree
6. attach into same parent slot
7. activate
8. project

`cleanup_failed_build()` and `destroy_all()` contain many of the pieces, but
they are not yet generalized into subtree lifecycle operations.


## Addendum: ADR-0012 Alignment — Scheduled Spot-Occupancy Operations

ADR-0003 remains correct in its central concern: structural replacement must be a runtime-managed ceremony, not an immediate mutation performed directly by castle handler code.

However, after ADR-0012, ADR-0003 should be read in terms of **spots** and **spot occupancy**, not ADR-0002-era slots or child-castle mount records.

### Updated framing

ADR-0003 is about scheduled structural operations over named spots owned by the target castle.

The intended programming shape is:

```python
rt.target_castle(castle)
rt.schedule_replacement("trace_log_spot", child_castle)    [PS:]

  [PS:] actually:
        rt.schedule_replacement("trace_log_spot", child_castle_template)
```

or:

```python
rt.target_castle(castle)
rt.schedule_clearing("trace_log_spot")
rt.schedule_placement("trace_log_spot", child_castle)    [PS:]

  [PS:] actually:
        rt_schedule_build("trace_log_spot", child_Castle_template)
```

The important architectural rule is that these operations are **scheduled**, not immediate.

Castle code does not directly tear down widgets, unregister associates, destroy child castles, or mutate the live placement tree. It records a structural intention. The runtime later performs that intention during a safe structural phase.

### Replacement means delete plus build

For ADR-0003 purposes:

```text
replacement = delete + build
```

A replacement request means:

```text
delete the current occupant of the spot
build/place the requested new occupant into the spot
```

Replacement is not an atomic swap where the old occupant remains unless the new occupant succeeds.

If a future system wants “build the replacement off to the side and swap only on success,” that should be treated as a separate operation with separate semantics. It is not the meaning of replacement in ADR-0003.

### Deletes precede builds

During the structural phase, the runtime must process destruction before construction.

The phase law is:

```text
all scheduled deletes happen before all scheduled builds
```

This preserves process integrity.

A handler may schedule multiple clearings, builds, and replacements. The runtime gathers those requests and executes them in an orderly structural phase. Destruction happens first. Building happens second. Activation happens only after the runtime has restored structural integrity.

### Visibility is not structural replacement

ADR-0003 should not include hide/show behavior.

Visibility is ordinary associate data. For example, an associate type may support:

```python
"visible": True
```

or:

```python
"visible": False
```

A castle may set that data during reconciliation, and the associate may project it during the normal dirty-associate projection phase.

That is not structural clearing, placement, deletion, or replacement.

Changing visibility does not alter spot occupancy. It does not destroy or build runtime beings. Therefore, it belongs to associate data projection, not ADR-0003.

### Relationship to associates and child castles

ADR-0012 establishes that spots may initially contain associates or child castles.

ADR-0003 concerns scheduled structural operations over spot occupancy.

The first implementation may choose to support replacement of child-castle occupants only. That is acceptable and likely simpler.

Associates are part of the declaring castle’s own body plan. Replacing an associate dynamically can invalidate assumptions in that castle’s reconcile function and should not be treated casually.

Therefore:

```text
Initial ADR-0003 implementation may limit scheduled replacement to child castles.
```

This is an implementation boundary, not a contradiction of the spot-occupancy model.

The architectural distinction is:

```text
Changing associate data -> reconciliation and projection
Changing spot occupancy -> scheduled structural operation
```

### Authority boundary

ADR-0012’s authority rule still applies.

A parent castle may schedule clearing, placement, or replacement in one of its own named spots.

A parent castle may place a child castle into a spot.

A parent castle may not lay out through that child castle or schedule structural operations inside the child castle’s internal spot tree unless it is acting through an explicit child-castle API or message protocol.

The target castle determines the authority boundary:

```python
rt.target_castle(castle)
```

After targeting a castle, scheduled spot operations refer to that castle’s local spot names.

### Summary

ADR-0003 should now be understood as the ADR for scheduled structural spot-occupancy operations.

Its core rule is:

```text
Do not mutate live structure immediately.
Schedule structural intentions.
At the structural phase, delete first, build second.
```

Visibility is not part of this ADR. It is associate data projection.

Replacement is not an atomic swap. Replacement means scheduled delete plus scheduled build.

The initial implementation may restrict replacement to child castles, while preserving the broader conceptual model of scheduled spot-occupancy operations.


## Codex Implementation Amendment

Older references in this document to `slot`, `submit_replace_slot_request(...)`, or slot-level replacement are historical language from the pre-ADR-0012 model.

The operative model is ADR-0012:

```text
spots + placements + scheduled structural operations
```

Implementation should therefore interpret ADR-0003 as follows:

* A castle owns a local spot map.
* A spot may have an occupant.
* A spot occupant may be a local associate or a child castle.
* Runtime code may schedule clearing, building, or replacement of a named spot.
* Scheduled spot operations refer to the currently targeted castle.
* Runtime handlers and reconcile functions must not mutate live spot occupancy directly.
* The runtime processes scheduled structural operations during a safe structural phase.

For the first implementation, scheduled replacement may be limited to child-castle occupants. This keeps dynamic replacement out of the declaring castle's own associate body plan.

Replacement means:

```text
delete current occupant
then build requested new child castle from a template
```

It is not an atomic swap and does not preserve the old occupant on replacement failure.

Clearing means:

```text
delete current occupant
leave the spot empty
```

Building means:

```text
build requested child castle from a template into an empty spot
```

The structural phase must process all deletions before processing all builds. After the structural phase completes, normal castle reconciliation and associate projection may continue.
