# ADR-0012: Spots and Placements for Castle Layout

## Status

Proposed

## Context

ADR-0002 established that castles may have child castles. A parent castle can create, own, and route messages to child castles, and those child castles may themselves have associates and child castles.

However, the earlier layout model blurred several separate concerns:

* Which associates exist?
* Which child castles exist?
* Which layout positions exist?
* Which things are initially placed into those positions?
* Which child castles are visual, and which are purely logical?

The current demo has already reached the point where this distinction matters. For example, a parent castle may have a visual child castle such as a trace log, but it may also have a purely logical child castle that participates in message routing and state management without being mounted into the UI at all.

We therefore need a clearer model:

> A castle declares its beings separately from its places.

The castle should declare local associates, child castles, a tree of named spots, and initial placements into those spots. The runtime is responsible for sequencing construction, destruction, mounting, unmounting, routing, activation, reconciliation, and projection.

## Decision

A castle spec may use the following shape:

```python
{
    "kind": "castle_spec",
    "name": "demo_castle",

    "state": {...},
    "handle_fn": handle_demo_castle_message,
    "reconcile_fn": reconcile_demo_castle,

    "associates": [
        {
            "name": "main_window",
            "associate_type": WINDOW_ASSOCIATE_TYPE,
            "data": {...},
        },
        {
            "name": "priority_button",
            "associate_type": BUTTON_ASSOCIATE_TYPE,
            "data": {...},
        },
        {
            "name": "count_label",
            "associate_type": LABEL_ASSOCIATE_TYPE,
            "data": {...},
        },
    ],

    "child_castles": [
        {
            "name": "trace_log",
            "template_fn": trace_log_castle_template,
            "build_context": {...},
        },
        {
            "name": "logic_only_child",
            "template_fn": logic_only_template,
            "build_context": {...},
        },
    ],

    "spots": {
        "name": "main_window_spot",
        "layout": {
            "columnconfigure": {0: {"weight": 1}},
        },
        "children": [
            {
                "name": "priority_button_spot",
                "grid": {"row": 0, "column": 0, "sticky": "ew"},
            },
            {
                "name": "count_label_spot",
                "grid": {"row": 1, "column": 0, "sticky": "w"},
            },
            {
                "name": "trace_log_spot",
                "grid": {"row": 2, "column": 0, "sticky": "ew"},
            },
        ],
    },

    "placements": {
        "main_window_spot": {
            "kind": "associate",
            "name": "main_window",
        },
        "priority_button_spot": {
            "kind": "associate",
            "name": "priority_button",
        },
        "count_label_spot": {
            "kind": "associate",
            "name": "count_label",
        },
        "trace_log_spot": {
            "kind": "child_castle",
            "name": "trace_log",
        },
    },
}
```

This separates four concerns:

1. `associates` declares this castle’s local associate companions.
2. `child_castles` declares this castle’s child castles, whether visual or logical.
3. `spots` declares this castle’s named layout structure.
4. `placements` declares the initial occupants of spots.

The runtime must preserve the spot map after construction so that spots can later be referred to programmatically.

## Rules

### 1. Associates and child castles are declared separately from layout

An associate should not need to carry its own grid information.

A child castle should not need to carry its own mount information.

Instead, layout positions are declared in `spots`, and initial occupancy is declared in `placements`.

This avoids using the associate tree as a layout tree.

### 2. Spots belong to the authority of the declaring castle

A castle’s `spots` tree describes only the spatial structure that this castle has authority over.

A parent castle may place a child castle into one of its spots, but the parent castle may not describe the child castle’s internal spots.

### 3. Child castles are placeable leaves

Within a castle’s own `spots` tree:

* An associate may be a branching node if its associate type exposes a child layout parent.
* A child castle may be placed into a spot, but it is a leaf from the parent castle’s point of view.
* A logical child castle may exist without being placed into any spot.
* An empty spot may exist without any initial placement.

This is the central sovereignty rule:

> A castle may place another castle, but may not lay out through it.

Or, equivalently:

> Castles are placeable leaves in another castle’s layout. Only local associates can be layout branches.

### 4. Branching requires a local associate container

If a spot has child spots, then the thing placed in that spot must be a local associate that can contain children.

For example, if `main_window_spot` has children, then `main_window_spot` must initially contain an associate such as `main_window`, whose associate type exposes a child layout parent.

This is valid:

```python
"spots": {
    "name": "main_window_spot",
    "children": [
        {"name": "priority_button_spot", "grid": {"row": 0, "column": 0}},
        {"name": "trace_log_spot", "grid": {"row": 1, "column": 0}},
    ],
},

"placements": {
    "main_window_spot": {"kind": "associate", "name": "main_window"},
    "priority_button_spot": {"kind": "associate", "name": "priority_button"},
    "trace_log_spot": {"kind": "child_castle", "name": "trace_log"},
}
```

This is invalid if `trace_log_spot` contains a child castle:

```python
"spots": {
    "name": "trace_log_spot",
    "children": [
        {"name": "trace_label_inside_child"}
    ],
}
```

The parent castle does not own the trace log castle’s internal layout.

### 5. Local names are used in specs and APIs

Spot names, associate names, and child castle names are local to the declaring castle.

The authored spec should use simple local names such as:

```python
"main_window_spot"
"priority_button"
"trace_log"
```

The runtime may internally create globally unique identities, but those identities are runtime-private. They should not leak into the authored castle spec.

### 6. Initial placements are not the same as permanent structure

`placements` declares the initial occupancy of spots.

A spot may be empty at build time. A spot may later be cleared, filled, or replaced by scheduled structural operations.

The spot map remains part of the live castle runtime record after build.

### 7. Structural changes are scheduled, not immediate

Runtime code should not immediately rip associates or child castles out of the live system.

Instead, handlers and reconcile functions may schedule structural intentions, such as:

```python
rt.target_castle(castle)
rt.schedule_replacement("trace_log_spot", child_castle)
```

or:

```python
rt.target_castle(castle)
rt.schedule_clearing("trace_log_spot")
rt.schedule_placement("trace_log_spot", child_castle)
```

The exact API may change, but the architectural rule is firm:

> Structural changes are requested, staged, and applied by the runtime at safe phase boundaries.

Destruction, if any, happens before construction. Construction happens before activation. Activation happens only after the runtime has restored structural integrity.

### 8. Runtime owns sequencing

The spec describes the desired beings, places, and initial placements. It does not describe construction order.

The runtime is responsible for sequencing, including:

1. Expanding the castle template.
2. Allocating the castle shell.
3. Allocating associate shells.
4. Allocating child castle build requests.
5. Allocating spot records.
6. Constructing associate widgets.
7. Building child castles.
8. Resolving spot parents.
9. Applying layout configuration.
10. Applying initial placements.
11. Wiring routes.
12. Activating castles, associates, routes, and placements.
13. Reconciling dirty castles.
14. Projecting dirty associates.

The exact implementation order may evolve, but the template should remain declarative.

## Consequences

### Benefits

This model keeps layout simple and explicit.

It allows visual child castles and logical child castles to coexist.

It avoids forcing all child castles to be mounted.

It allows the runtime to preserve a named spot map for later dynamic changes.

It supports staged structural changes instead of immediate mutation.

It preserves castle authority boundaries: a parent castle can place a child castle, but cannot lay out the child castle’s internals.

### Costs

The runtime must now understand spots and placements as first-class runtime concepts.

The builder must validate that branching spots are occupied by local associates capable of containing children.

The runtime must resolve local names to runtime records during build.

The runtime must preserve enough spot information after build to support later scheduled clearing, placement, and replacement operations.

## Summary

A castle spec should not make layout an incidental property of associates or child castles.

Instead:

> Declare the beings. Declare the places. Declare the initial placements.

Associates and child castles are things. Spots are places. Placements say which things initially occupy which places.

A child castle may be placed in a spot, but it is a leaf in the parent castle’s layout. The child castle owns its own internal layout.

Structural changes to spots are staged through runtime requests and applied only during safe runtime phases.
