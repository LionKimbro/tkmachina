# ADR-0008: Lifecycle Hooks

## Discussion Item

There are no lifecycle hooks besides setup, project, and destroy.

Associate types currently have:

```python
setup_fn
project_fn
destroy_fn
```

That is a strong minimal set. The system may eventually need:

```python
setup_fn
activate_fn
deactivate_fn
project_fn
destroy_fn
```

Some bindings, timers, and listeners may need to exist only while active. Right
now setup creates bindings immediately, activation only flips
`associate["active"] = True`, and routes decide whether messages flow.

That is probably fine for the current demo. If associates later own file
watchers, animation timers, socket listeners, process monitors, or global
keybindings, activation and deactivation become real phases.

