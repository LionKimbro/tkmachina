# Build Request

This note documents the build request data structure submitted to the runtime
build process in `examples/rt.py`.

`docs/code/build-process.md` describes how the runtime processes a build. This
document describes what a caller submits and what data that request carries.

## Purpose

A build request is one request to apply a reusable template.

The template is the pattern. The build request is a specific invocation of that
pattern. Calling `make_build_request(...)` twice with the same `template_fn`
creates two separate requests and can mint two separate live instances.

## Creating A Request

Build requests are created with:

```python
rt.make_build_request(
    template_fn=demo_template,
    build_context={
        "trace_wraplength": 400,
    },
)
```

Full call shape:

```python
rt.make_build_request(
    template_fn,
    build_context=None,
    parent_castle=None,
    slot=None,
    activate_when_complete=True,
)
```

## Submitted Request Record

`make_build_request(...)` returns this dictionary:

```python
{
    "kind": "build_request",
    "id": "build:1",
    "template_fn": template_fn,
    "build_context": build_context or {},
    "parent_castle": parent_castle,
    "slot": slot,
    "activate_when_complete": activate_when_complete,
}
```

This is the object passed to:

```python
rt.submit_build_request(build_request)
```

Submission appends the request to `incoming_builds`. The build request itself
does not create castles, associates, widgets, or routes.

## Request Fields

### `kind`

Always `"build_request"`.

This marks the dictionary as a build request. The current runtime does not
perform strict schema validation on it.

### `id`

Runtime-generated request id.

The id is assigned by `make_id("build")`. It identifies the request invocation
for tracing and diagnostics.

The id is not a template name, castle name, or global address.

### `template_fn`

Callable template function.

The template function receives `build_context` and returns a castle spec:

```python
def demo_template(build_context):
    return {
        "kind": "castle_spec",
        "name": "demo_castle",
        ...
    }
```

The template function is part of the request because the request says what
pattern should be applied.

### `build_context`

Invocation-specific template input.

If omitted, this becomes `{}`.

Use `build_context` for values that vary per build request while keeping the
same template reusable. For example:

```python
{
    "trace_wraplength": 400,
}
```

### `parent_castle`

Optional parent castle reference.

When provided, the built castle is attached into the parent castle's
`children` mapping. `slot` must also be provided.

### `slot`

Optional parent slot name.

When `parent_castle` is provided, `slot` names where the new castle is attached:

```python
parent_castle["children"][slot] = child_castle_id
child_castle["parent"] = parent_castle_id
child_castle["slot"] = slot
```

### `activate_when_complete`

Boolean activation flag.

Default: `True`.

When true, records minted by the build become active after the build completes.
When false, the request can still describe what to build, but the minted records
remain inactive.

## Template Return Value

The submitted request does not directly contain the castle, associate, export,
or route specs. It contains a `template_fn` that returns them.

That returned dictionary is the request's payload shape.

Current top-level template result:

```python
{
    "kind": "castle_spec",
    "name": "demo_castle",
    "state": {},
    "handle_fn": handle_demo_castle_message,
    "reconcile_fn": reconcile_demo_castle,
    "child_castles": [],
    "exports": [],
    "routes": [],
    "associates": [],
}
```

## Castle Spec Sections

### `kind`

Usually `"castle_spec"`.

This is self-description for the returned template record. The current runtime
does not deeply validate it.

### `name`

Local castle role name.

This is not globally unique. If the same template is built twice, both minted
castles may have the same `name`; each receives a different runtime id.

### `state`

Initial state dictionary for the minted castle.

The runtime copies this into the castle shell.

### `handle_fn`

Message handler for the minted castle.

The handler receives `(castle, message)`.

The handler should return one of:

- `rt.IGNORED`
- `rt.HANDLED`
- `rt.HANDLED_DIRTY`

Only `rt.HANDLED_DIRTY` marks the castle dirty for reconciliation. `None` is
treated as `rt.HANDLED_DIRTY` for backward compatibility.

### `reconcile_fn`

Optional post-message reconciliation function for the minted castle.

The reconciler receives `(castle)`. It runs after castle message handling and
before associate projection, but only for dirty castles that provide a
`reconcile_fn`.

Headless and service castles may omit it.

### `child_castles`

Optional list of child castle specs to build inside this castle.

Current Python-only child declaration shape:

```python
{
    "kind": "child_castle_spec",
    "slot": "trace_log",
    "template_fn": trace_log_castle_template,
    "build_context": {},
    "mount": {
        "parent_associate": "main_window",
        "grid": {
            "row": 3,
            "column": 0,
            "sticky": "ew",
        },
    },
}
```

Fields:

- `kind`: usually `"child_castle_spec"`
- `slot`: local slot name in the parent castle's `children` mapping
- `template_fn`: child template function to instantiate
- `build_context`: optional context passed to the child template
- `mount`: optional visual mount for the child's root associate

The `mount` section is only needed for visible child castles. Headless child
castles can omit it.

### `exports`

Optional list of global export specs.

Exports publish a minted castle under a global address.

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

Export fields:

- `kind`: usually `"export_spec"`
- `name`: global address to publish
- `target`: local target to publish

Current target shape:

```python
{
    "kind": "castle",
    "name": "demo_castle",
}
```

Current rule: a global export name must be unique. A build fails if the name is
already registered or duplicated inside the same template result.

### `routes`

Optional list of requested route specs.

Routes describe extra message paths requested by the template.

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

Route fields:

- `kind`: usually `"route_spec"`
- `from`: source endpoint
- `to`: destination endpoint

Endpoint fields:

- `kind`: endpoint namespace/kind
- `name`: endpoint name in that namespace
- `box`: source or destination queue name

Current endpoint kinds:

- `global_castle`: resolves through the global castle address book
- `castle`: resolves against castles minted by this build
- `associate`: resolves against associates minted by this build

### `associates`

List of associate specs owned by the castle.

Associate specs may be nested through `children`.

```python
{
    "kind": "associate_spec",
    "name": "priority_button",
    "associate_type": BUTTON_ASSOCIATE_TYPE,
    "data": {
        "text": "Required (5 left)",
        "enabled": True,
    },
    "layout": {},
    "grid": {
        "row": 0,
        "column": 0,
        "sticky": "ew",
    },
    "children": [],
}
```

Associate fields:

- `kind`: usually `"associate_spec"`
- `name`: local associate role name
- `associate_type`: setup/project/destroy behavior record
- `data`: desired widget-facing data
- `layout`: layout configuration for a child container this associate provides
- `grid`: Tk grid options for this associate's own widget
- `children`: nested associate specs

## Associate Type Shape

`associate_type` is a dictionary of behavior functions:

```python
{
    "name": "button",
    "setup_fn": setup_button_associate,
    "project_fn": project_button_associate,
    "destroy_fn": destroy_widget_associate,
}
```

Fields:

- `name`: associate type name
- `setup_fn`: creates or attaches the concrete Tk object
- `project_fn`: projects desired `data` onto the concrete Tk object
- `destroy_fn`: destroys or detaches the concrete Tk object

## Current Defaults

A build request does not need to declare default associate-to-castle routes.

The runtime currently creates routes from every associate `outbox` to the host
castle `inbox`. Template `routes` are for additional requested topology.

## Current Limits

The current request/template shape does not yet support:

- multiple castle specs in one request
- non-castle global exports
- conflict policies other than failing duplicate global exports
- schema validation for every `kind` field
- route endpoints by runtime id
