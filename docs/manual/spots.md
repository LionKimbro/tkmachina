# Spots and Placements

A **spot** is a named place inside a castle where something is placed. Its
occupant is either a local **associate** or a mounted **child castle**. Spots
replace the older "slot" idea and unify both kinds of placement under one
mechanism.

## The spot record

Allocated by `allocate_spot_record` from a castle spec's `spots` tree:

```python
{
    "kind": "spot",
    "id": "spot:2",
    "name": "inspector",
    "host_castle": "castle:3",
    "parent_spot": <name or None>,   # spots nest
    "children": [child_spot_name, ...],
    "layout": {...},                 # applied to the occupant
    "grid": {...},                   # applied to the occupant
    "occupant": None,                # {"kind": "associate"|"child_castle", "id": ...}
    "active": False,
}
```

Spots nest: a spot spec may carry `children: [ <spot spec>, ... ]`, forming a
tree of named places within one castle.

## Placements

A castle spec declares which occupant fills each spot via `placements`:

```python
"placements": {
    "title":   {"kind": "associate",    "name": "title_label"},
    "body":    {"kind": "associate",    "name": "content_frame"},
    "inspector": {"kind": "child_castle", "name": "inspector_castle"},
}
```

`resolve_placement_occupant` looks the name up in the castle's `associates` or
`children` and records `{"kind", "id"}` as the spot's occupant. Placing an
occupant sets its `grid`/`layout` from the spot and attaches it under the correct
widget parent (`apply_spot_placement_effects` -> `place_associate_in_spot`).

## Rules the runtime enforces

- **Branching spots must be hosted by a child-hosting associate.** If a spot has
  occupied child spots, the spot itself must be occupied by an *associate* whose
  type has `can_host_children: True` (e.g. `frame`, `label_frame`, `window`).
  Otherwise there is nowhere to attach the child widgets.
- **Embeddability.** An occupant placed inside a child spot must have
  `embeddable: True` (all types except `window` are embeddable). A child castle's
  root associate must be embeddable to be mounted under a parent associate.
- **One root per placed child castle.** A child castle mounted into a parent spot
  must have exactly one root associate (its `parent_associate is None`); that
  root is what gets placed into the spot.

## Mounting a child castle into a parent spot

When a build request carries `parent_castle` + `parent_spot`,
`apply_parent_spot_placement` sets the target spot's occupant to the new child
castle, records the placement, validates it, and places the child's root
associate under the spot's parent associate. This is how one castle becomes the
occupant of another castle's spot.

## Dynamic replacement

Because spots are named and their occupancy is data, a running castle can swap
what fills a spot. See [builds and structural changes](builds.md): a castle
targets itself and schedules `clearing`, `building`, or `replacement` on a spot
name. Note that **only child-castle occupants can be dynamically cleared today**
— clearing an associate-occupied spot raises `NotImplementedError`.
