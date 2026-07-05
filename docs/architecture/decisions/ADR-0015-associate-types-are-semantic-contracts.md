# ADR-0015: Associate Types Are Semantic Contracts

## Status

Accepted

## Context

Simple TkMachina associates often have a direct relationship to a Tk widget:

```text
label associate  -> ttk.Label
button associate -> ttk.Button
entry associate  -> ttk.Entry
```

That mapping is useful for small widgets, but it should not become the rule for
all associate design.

Some Tk widgets are really interaction surfaces. `Text`, `Treeview`, and
`Canvas` can each support several different human-facing abstractions. A
`ttk.Treeview`, for example, may be used as a hierarchy, a single-selection
table, a multi-selection table, a sortable table, or a data grid. Those are not
the same public promise even if they share the same Tk substrate.

## Decision

An associate type is not defined by the Tk widget it uses.

An associate type is defined by the Little Castles promise it makes.

Multiple associate types may use the same Tk widget internally when the
human-facing semantics are different enough.

Therefore TkMachina should prefer separate public associate types for distinct
semantic promises, even when those associates share implementation machinery.

For advanced widgets, this means families of associates may be more appropriate
than one monolithic associate:

```text
Text-backed examples:
  plain_text_editor
  log_view
  rich_text_view
  code_editor

Treeview-backed examples:
  tree_view
  single_select_table
  multi_select_table
  sortable_table

Canvas-backed examples:
  canvas_drawing_surface
  vector_canvas
  scene_canvas
  diagram_canvas
```

The names above are provisional. The principle is the important part:

```text
Public associate type = semantic contract
Tk widget = implementation detail
```

## Performance And Sync Strategy

Advanced associates may manage large internal worlds. TkMachina should not
accidentally promise that every runtime tick fully reconciles an entire text
buffer, tree, table, or canvas scene.

Some advanced associates may need an operation model rather than simple desired
state projection:

```python
{
    "operations": [
        {"kind": "insert_row", "id": "r17", "values": [...]},
        {"kind": "update_row", "id": "r22", "values": [...]},
        {"kind": "delete_row", "id": "r31"},
    ],
}
```

Different semantic promises may need different synchronization strategies.
This is another reason to avoid prematurely unifying advanced widgets behind a
single generic associate type.

## Consequences

TkMachina may have several associate types backed by the same Tk widget.

Shared implementation should be factored only after the public semantic shapes
are understood. The first goal is clear public promises, not premature
unification.

The manual becomes a design tool. If one associate reference page has to say
"when used as a table," "when used as a tree," and "when used as a sortable
grid," that is evidence the associate should be split.

Raw Tk access remains available as an escape hatch, but repeated raw Tk use for
ordinary behavior is evidence that an associate type is under-modeled.
