# ADR-0005: Addressing And Scoping

## Discussion Item

Names are local-ish, but not really scoped yet.

The demo builds the same `demo_template()` twice. Each castle is named
`"demo_castle"`, and each has associates named `"priority_button"`,
`"count_label"`, and so on.

This works because `find_built_castle_id()` only searches inside the current
build, and each castle's associate names are stored inside that castle.

The broader system needs a more explicit answer to:

```text
What is the address of this thing?
```

Possible address shapes:

```text
castle:7
castle:7/associate:priority_button
root/sidebar/search_box
parent.children["inspector"].associates["title_label"]
```

Routes currently store runtime ids internally, which is good. Specs still refer
to names, and names will eventually need scope rules.

Possible philosophy:

```text
IDs internally, names locally, paths at boundaries.
```


## Decision

TkMachina does not use castle names as global object addresses.

Runtime communication is governed by routes, and routes store resolved runtime
IDs.

Runtime IDs are the true live-object identity.

Names are local authoring labels:

- associate names are local to a castle
- child names are local to a parent castle
- template names describe what was built
- global names exist only through explicit global export

The live castle field formerly called `name` is now `template_name`.

`template_name` is descriptive metadata. It is useful for diagnostics,
build-local route/export lookup, and human-readable traces, but it is not a
runtime address and is not required to be globally unique.

No general path language is introduced by this ADR.

Earlier references in this ADR to `find_built_castle_id(...)` and castle
`name` refer to the pre-decision implementation. The current implementation
uses `template_name` for descriptive castle metadata and resolves build-local
castle references through `find_built_castle_id_by_template_name(...)`.

