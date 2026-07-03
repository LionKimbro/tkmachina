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

