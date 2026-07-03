# ADR-0007: Serializable Build Specs

## Discussion Item

The build spec is not serializable yet.

Templates are Python functions that return dictionaries containing function
references and associate type objects:

```python
"handle_fn": handle_demo_castle_message
"associate_type": BUTTON_ASSOCIATE_TYPE
```

That is appropriate for the thought-object phase, but it is not yet a
serializable template language.

If templates should eventually be saved, reloaded, diffed, or generated, they
will need names instead of function objects:

```python
"handle": "demo.handle_message"
"associate_type": "button"
```

Then the runtime needs registries:

```python
registered_castle_handlers["demo.handle_message"]
registered_associate_types["button"]
```

The current system has runtime-owned construction. A future version may need
runtime-owned construction from declarative specs.

