# Build Request

This note documents the current build request record submitted to the runtime
in `src/tkmachina/rt.py`.

Build requests are invocations of templates. A template describes a castle
structure. A build request says: build that template now, with this context, and
possibly attach the resulting root castle to an existing parent castle and
spot.

## Purpose

A build request is one construction request.

Calling `make_build_request(...)` twice with the same template function creates
two independent requests. Each successful request mints new runtime ids for
castles, associates, spots, and routes.

## Creating A Request

Build requests are created with:

```python
rt.make_build_request(
    template_fn,
    build_context=None,
    parent_castle=None,
    child_name=None,
    parent_spot=None,
    activate_when_complete=True,
)
```

The current function still accepts `slot` as a compatibility alias for
`child_name`. New code should not use it.

Normal top-level builds are submitted like this:

```python
request = rt.make_build_request(
    template_fn=demo_template,
    build_context={"trace_wraplength": 400},
)
rt.submit_build_request(request)
```

The runtime queues submitted requests in `incoming_builds`. They are processed
by `process_incoming_builds()` during the runtime tick.

## Request Shape

`make_build_request(...)` returns:

```python
{
    "kind": "build_request",
    "id": "build:1",
    "template_fn": template_fn,
    "build_context": build_context or {},
    "parent_castle": parent_castle,
    "slot": slot,
    "child_name": resolved_child_name,
    "parent_spot": parent_spot,
    "activate_when_complete": activate_when_complete,
}
```

`resolved_child_name` is `child_name` when provided, otherwise `slot`.

## Fields

### `template_fn`

Callable that receives `build_context` and returns a castle spec:

```python
spec = template_fn(build_context)
```

The runtime currently uses direct Python function references. That is not yet a
serializable template-reference system.

### `build_context`

Caller-supplied values for this build invocation.

The runtime passes this dictionary to the template function. Templates should
copy values they need into returned specs or state. The runtime does not keep
interpreting `build_context` after template expansion.

### `parent_castle`

Optional live parent castle record or castle id.

When present, the new root castle is attached to the parent castle's
`children` mapping under `child_name`.

### `child_name`

Parent-local name for the child castle:

```python
parent_castle["children"][child_name] = child_castle_id
```

`child_name` names the child being attached. It is not the visual spot.

For example:

```text
child_name:  "trace_log"
parent_spot: "trace_log_spot"
```

### `parent_spot`

Optional parent-local spot name.

When present, the build result is also placed into an existing live parent
spot. This is used by scheduled structural building and replacement.

The parent spot must exist and be empty when the build reaches
`apply_parent_spot_placement(build)`.

### `activate_when_complete`

If true, the build's castles, associates, spots, and routes are activated after
construction.

The default is true.

## Top-Level Builds

A top-level build usually has no parent:

```python
rt.submit_build_request(
    rt.make_build_request(
        template_fn=demo_template,
        build_context={"trace_wraplength": 400},
    )
)
```

Its root visual associate will be constructed under `tk_master`.

## Structural Builds

Scheduled structural building uses build requests internally.

When code calls:

```python
rt.target_castle(parent_castle)
rt.schedule_building(
    "trace_log_spot",
    trace_log_castle_template,
    {"trace_wraplength": 400},
    child_name="trace_log",
)
```

the runtime later creates a build request shaped roughly like:

```python
rt.make_build_request(
    template_fn=trace_log_castle_template,
    build_context={"trace_wraplength": 400},
    parent_castle=parent_castle["id"],
    child_name="trace_log",
    parent_spot="trace_log_spot",
)
```

This builds a new child castle from the template and places its root associate
into the named parent spot.

## Relationship To Templates

The request is not the template.

```text
template = reusable castle pattern
request = one invocation of that pattern
build = live runtime construction attempt
```

A template function returns a castle spec. The build request carries the
template function and context needed to produce that spec.

## Relationship To Spots And Placements

ADR-0012 is the current layout model.

New request language should be:

```text
child_name  -> name of child castle in parent["children"]
parent_spot -> name of visual/layout spot in parent["spots"]
```

Old `slot` language should be read as historical or compatibility-only.

Build requests do not carry `mount` records. Visual placement is expressed
through parent spots and spot occupancy.

## Failure Behavior

If a build fails, `execute_build_request(request)` catches the exception,
cleans up records created by that build attempt, and moves the build record to
`faulty_builds`.

For failed structural builds, cleanup also detaches any parent spot occupancy
that pointed at the partially built child castle.

## Current Limits

- Requests use direct Python function references.
- `slot` still exists as a compatibility alias for `child_name`.
- Request records are plain dictionaries, not typed objects.
- Error policy is currently simple: log, clean up, and record faulty builds.
