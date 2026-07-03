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

