# Build Template

This note documents build templates in the current demo runtime.

`docs/code/build-request.md` documents the submitted request envelope.
`docs/code/build-process.md` documents the runtime phases that process a build.
This document focuses on the reusable template function and the spec data it
returns.

## Purpose

A build template is a reusable pattern for minting runtime objects.

The same template can be applied many times. Each application can create fresh
castle records, associate records, routes, widgets, and runtime ids.

Templates describe what should exist. They should not directly create Tk
widgets or mutate runtime registries.

## Template Function

A template is a callable that receives `build_context`:

```python
def demo_template(build_context):
    return {
        "kind": "castle_spec",
        "name": "demo_castle",
        ...
    }
```

The build context is supplied by the build request:

```python
rt.make_build_request(
    template_fn=demo_template,
    build_context={
        "trace_wraplength": 400,
    },
)
```

Use `build_context` for invocation-specific values while keeping the template
itself reusable.

## Top-Level Shape

The current runtime expects the template to return one castle spec:

```python
{
    "kind": "castle_spec",
    "name": "demo_castle",
    "state": {
        "press_count": 0,
    },
    "handle_fn": handle_demo_castle_message,
    "reconcile_fn": reconcile_demo_castle,
    "child_castles": [],
    "exports": [],
    "routes": [],
    "associates": [],
}
```

## Castle Spec

The castle spec describes the castle minted by this template application.

### `kind`

Usually `"castle_spec"`.

This field makes the record self-describing. The current runtime does not
strictly validate it.

### `name`

Local role name for the castle.

This name is not globally unique. If a template is built twice, both minted
castles can be named `"demo_castle"`. Their runtime ids distinguish them.

Route endpoints with kind `"castle"` use this name as a local lookup inside the
current build.

### `state`

Initial state for the castle.

The runtime copies this dictionary when it allocates the castle shell, so each
minted castle receives its own state dictionary.

Example:

```python
"state": {
    "press_count": 0,
    "button_enabled": True,
    "window_width": None,
    "window_height": None,
}
```

### `handle_fn`

Message handler for the castle.

The function receives:

```python
handle_fn(castle, message)
```

It may inspect and mutate `castle["state"]`, read messages, call runtime helper
functions, and emit additional messages.

The handler should return one of:

- `rt.IGNORED`
- `rt.HANDLED`
- `rt.HANDLED_DIRTY`

Only `rt.HANDLED_DIRTY` marks the castle dirty for reconciliation. `None` is
treated as `rt.HANDLED_DIRTY` for backward compatibility.

### `reconcile_fn`

Optional post-message reconciliation function for the castle.

The function receives:

```python
reconcile_fn(castle)
```

When an active castle handles messages, the runtime marks it dirty. After castle
message handling, dirty castles that provide `reconcile_fn` are reconciled
before dirty associates are projected.

This function is not only for view synchronization. It may reconcile derived
associate state, emit derived messages, update child structures, validate
state, or do nothing.

Headless and service castles do not need associates and do not need a
`reconcile_fn`.

### `child_castles`

Optional list of child castle declarations.

Child castles are built as runtime participants in their own right, then
attached into the parent castle's `children` mapping by slot name.

Current Python-only shape:

```python
"child_castles": [
    {
        "kind": "child_castle_spec",
        "slot": "trace_log",
        "template_fn": trace_log_castle_template,
        "build_context": {
            "trace_wraplength": 400,
        },
        "mount": {
            "parent_associate": "main_window",
            "grid": {
                "row": 3,
                "column": 0,
                "sticky": "ew",
                "pady": (14, 0),
            },
        },
    },
]
```

Child declaration fields:

- `kind`: usually `"child_castle_spec"`
- `slot`: name used in the parent castle's `children` mapping
- `template_fn`: child template function to instantiate
- `build_context`: optional context passed to the child template
- `mount`: optional visual mount for the child's root associate

Visible child castles should provide one root associate. The mount places that
root associate into a parent associate's layout region. Headless child castles
can omit `mount`.

### `exports`

Optional list of global exports.

Exports publish a minted local castle under a global address. They are useful
when future builds need to route to an out-of-build castle.

Example:

```python
"exports": [
    {
        "kind": "export_spec",
        "name": "demo_primary",
        "target": {
            "kind": "castle",
            "name": "demo_castle",
        },
    },
]
```

Export names must be unique in the global castle address book. A build fails if
an export name is already registered or duplicated in the same template result.

### `routes`

Optional list of explicit route specs.

Routes describe message paths requested by the template beyond the runtime's
default associate-to-host-castle routes.

Example:

```python
"routes": [
    {
        "kind": "route_spec",
        "from": {
            "kind": "global_castle",
            "name": rt.TRACE_CASTLE,
            "box": "outbox",
        },
        "to": {
            "kind": "castle",
            "name": "demo_castle",
            "box": "inbox",
        },
    },
]
```

This route subscribes the built castle to the globally addressable trace castle.

### `associates`

List of associate specs owned by the castle.

Associates are the widget-facing companions to the castle. They hold desired
widget data, emit semantic messages, and project state onto concrete Tk
widgets.

## Export Spec

Export specs appear inside `exports`.

```python
{
    "kind": "export_spec",
    "name": "demo_primary",
    "target": {
        "kind": "castle",
        "name": "demo_castle",
    },
}
```

### `kind`

Usually `"export_spec"`.

The current runtime does not inspect this value.

### `name`

Global address to publish.

This name must be unique. The current conflict policy is fail.

### `target`

Local target to publish.

Current supported target:

```python
{
    "kind": "castle",
    "name": "demo_castle",
}
```

The target name resolves against castles minted by the current build.

## Route Spec

Route specs appear inside `routes`.

```python
{
    "kind": "route_spec",
    "from": {
        "kind": "global_castle",
        "name": rt.TRACE_CASTLE,
        "box": "outbox",
    },
    "to": {
        "kind": "castle",
        "name": "demo_castle",
        "box": "inbox",
    },
}
```

### `kind`

Usually `"route_spec"`.

Inside a `routes` list this is somewhat redundant, but it keeps the route
record self-describing.

### `from`

Source endpoint.

### `to`

Destination endpoint.

## Route Endpoint

Route endpoints describe where a route starts or ends.

```python
{
    "kind": "castle",
    "name": "demo_castle",
    "box": "inbox",
}
```

### `kind`

Endpoint namespace.

Current endpoint kinds:

- `global_castle`
- `castle`
- `associate`

### `name`

Endpoint name within the selected namespace.

For `global_castle`, this is a global address. For `castle` and `associate`,
this is a local role name inside the current build.

### `box`

Queue name on the endpoint record.

Common boxes:

- `inbox`
- `outbox`

## Associate Spec

Associate specs appear inside `associates` or inside another associate's
`children`.

```python
{
    "kind": "associate_spec",
    "name": "priority_button",
    "associate_type": BUTTON_ASSOCIATE_TYPE,
    "desired": {
        "text": "Required (5 left)",
        "enabled": True,
    },
    "grid": {
        "row": 0,
        "column": 0,
        "sticky": "ew",
    },
}
```

### `kind`

Usually `"associate_spec"`.

The current runtime does not strictly validate it.

### `name`

Local role name for the associate within its host castle.

Handlers can use this name to find the minted associate:

```python
priority_button = rt.get_associate(castle, "priority_button")
```

Messages emitted by associates also use the associate name as their `origin`.

### `associate_type`

Behavior record for the associate.

Current demo types:

- `WINDOW_ASSOCIATE_TYPE`
- `BUTTON_ASSOCIATE_TYPE`
- `LABEL_ASSOCIATE_TYPE`

Associate types provide setup, projection, and teardown behavior.

### `data`

Desired widget-facing data.

The shape depends on the associate type.

Button data currently uses:

```python
{
    "text": "Required (5 left)",
    "enabled": True,
}
```

Label data currently uses:

```python
{
    "text": "Recent RT trace: waiting",
    "wraplength": 400,
}
```

Window desired data currently uses:

```python
{
    "title": "TkMachina RT Demo",
    "desired_width": 460,
    "desired_height": 480,
    "min_width": 420,
    "min_height": 480,
    "content_padding": 16,
}
```

Window observed data may start with:

```python
{
    "actual_width": None,
    "actual_height": None,
}
```

### `layout`

Layout configuration applied to a child container provided by this associate.

The window associate provides `child_tk_parent`, so its `layout` can configure
the content frame used by its children.

Current supported keys:

- `columnconfigure`
- `rowconfigure`

Example:

```python
"layout": {
    "columnconfigure": {
        0: {"weight": 1},
    },
}
```

### `grid`

Tk grid options for this associate's own widget.

Example:

```python
"grid": {
    "row": 1,
    "column": 0,
    "sticky": "w",
    "pady": (14, 4),
}
```

### `children`

Nested associate specs.

Children use their parent's `child_tk_parent` if one exists. Otherwise they use
the parent's own Tk widget as their Tk parent.

## Associate Type

Associate types are not template sections, but templates refer to them through
`associate_type`.

```python
{
    "name": "button",
    "setup_fn": setup_button_associate,
    "project_fn": project_button_associate,
    "destroy_fn": destroy_widget_associate,
}
```

### `name`

Associate type name.

### `setup_fn`

Creates or attaches the concrete Tk object and stores it on the associate.

### `project_fn`

Projects desired associate `data` onto the concrete Tk object.

### `destroy_fn`

Destroys or detaches the concrete Tk object during teardown.

## Naming And Addressing

Template names are local role names, not global identities.

Local names:

- castle spec `name`
- associate spec `name`

Global names:

- export spec `name`
- endpoint `name` when endpoint kind is `global_castle`

Runtime ids are minted by the runtime. Templates should describe roles and
addresses, not precomputed runtime ids.

## Reuse

A template should be safe to apply more than once.

Avoid sharing mutable objects between applications unless sharing is intended.
The current runtime copies castle `state` and associate `data` dictionaries, but
nested mutable values inside those dictionaries are still shared if the template
reuses them.

## Current Limits

Current templates describe one top-level castle with optional child castles.
They do not yet support:

- multiple castle specs in one template result
- non-castle global exports
- route endpoints by runtime id
- schema validation for every `kind` field
