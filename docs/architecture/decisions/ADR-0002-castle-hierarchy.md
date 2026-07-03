# ADR-0002: Castle Hierarchy

## Discussion Item

There is no real castle hierarchy yet.

`make_build_request()` already has `parent_castle` and `slot`, but the current
build path does not actually attach a newly built castle into a parent castle's
child structure. The castle record has `"children": {}`, but builds remain
basically top-level islands.

Right now the runtime can build two demo castles, but cannot yet say:

```text
Build this child castle into this named slot of that parent castle.
```

The hierarchy probably needs records like:

```python
parent_castle["children"][slot] = child_castle_id
child_castle["parent"] = parent_castle_id
child_castle["slot"] = slot
```

Routes, layout, and ownership may need to respect that hierarchy.

Without this, TkMachina has runtime-owned construction, but not yet composable
castle structure.

