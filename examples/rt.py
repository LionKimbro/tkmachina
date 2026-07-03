"""
Tiny module-shaped runtime for the TkMachina demo.

RT is intentionally a module with global registries. The demo uses plain
dictionaries and functions so the live object system stays visible.
"""

import tkinter as tk

incoming_builds = []
active_builds = []
completed_builds = []
faulty_builds = []

castles = {}
associates = {}
routes = []
trace = []
dirty_castles = set()
dirty_associates = set()
current_target_associate = None
tk_master = None
global_castles = {}

TRACE_CASTLE = "global_trace"

IGNORED = "ignored"
HANDLED = "handled"
HANDLED_DIRTY = "handled_dirty"

_next_ids = {
    "build": 0,
    "castle": 0,
    "associate": 0,
    "route": 0,
}


def reset():
    incoming_builds.clear()
    active_builds.clear()
    completed_builds.clear()
    faulty_builds.clear()
    castles.clear()
    associates.clear()
    routes.clear()
    trace.clear()
    dirty_castles.clear()
    dirty_associates.clear()
    global_castles.clear()
    global current_target_associate, tk_master
    current_target_associate = None
    tk_master = None
    for key in _next_ids:
        _next_ids[key] = 0


def make_id(kind):
    _next_ids[kind] += 1
    return f"{kind}:{_next_ids[kind]}"


def make_build_request(
    template_fn,
    build_context=None,
    parent_castle=None,
    slot=None,
    activate_when_complete=True,
):
    return {
        "kind": "build_request",
        "id": make_id("build"),
        "template_fn": template_fn,
        "build_context": build_context or {},
        "parent_castle": parent_castle,
        "slot": slot,
        "activate_when_complete": activate_when_complete,
    }


def submit_build_request(build_request):
    incoming_builds.append(build_request)
    trace.append(f"submitted build {build_request['id']}")


def setup_global_castles():
    if TRACE_CASTLE in global_castles:
        return

    castle_id = make_id("castle")
    castle = {
        "kind": "castle",
        "id": castle_id,
        "name": TRACE_CASTLE,
        "state": {
            "entries": [],
            "version": 0,
        },
        "associates": {},
        "children": {},
        "inbox": [],
        "outbox": [],
        "active": True,
        "handle_fn": None,
        "reconcile_fn": None,
        "global": True,
        "headless": True,
    }
    castles[castle_id] = castle
    global_castles[TRACE_CASTLE] = castle_id
    trace.append(f"setup global castle {TRACE_CASTLE}")


def get_global_castle(name):
    castle_id = global_castles[name]
    return castles[castle_id]


def add_trace(text):
    if TRACE_CASTLE not in global_castles:
        setup_global_castles()

    trace_castle = get_global_castle(TRACE_CASTLE)
    trace_castle["state"]["entries"].append(text)
    trace_castle["state"]["version"] += 1
    version = trace_castle["state"]["version"]
    trace_castle["outbox"].append(
        {
            "kind": "event",
            "type": "trace_changed",
            "origin": trace_castle["name"],
            "emitter": trace_castle["name"],
            "payload": {
                "version": version,
                "text": text,
            },
        }
    )
    trace.append(f"global trace appended version {version}")


def get_trace_entries():
    if TRACE_CASTLE not in global_castles:
        return []

    return list(get_global_castle(TRACE_CASTLE)["state"]["entries"])


def process_incoming_builds():
    while incoming_builds:
        request = incoming_builds.pop(0)
        build = {
            "kind": "active_build",
            "request": request,
            "spec": None,
            "castle_specs": {},
            "castle_mounts": {},
            "castle_ids": [],
            "associate_ids": [],
            "route_ids": [],
            "global_export_names": [],
            "status": "active",
        }
        active_builds.append(build)
        trace.append(f"started build {request['id']}")

        try:
            process_build(build)
        except Exception as exc:
            build["status"] = "faulty"
            build["error"] = repr(exc)
            cleanup_failed_build(build)
            active_builds.remove(build)
            faulty_builds.append(build)
            trace.append(f"build {request['id']} failed: {exc}")
        else:
            build["status"] = "completed"
            active_builds.remove(build)
            completed_builds.append(build)
            trace.append(f"completed build {request['id']}")


def process_build(build):
    expand_template(build)
    allocate_castle_shells(build)
    register_global_exports(build)
    allocate_associate_shells(build)
    construct_widgets(build)
    apply_layout(build)
    wire_default_routes(build)
    append_extra_routes(build)
    if build["request"]["activate_when_complete"]:
        activate_build(build)


def expand_template(build):
    request = build["request"]
    build["spec"] = request["template_fn"](request["build_context"])
    trace.append("phase: expanded template")


def allocate_castle_shells(build):
    request = build["request"]
    parent_castle = request.get("parent_castle")
    parent_castle_id = None
    if parent_castle is not None:
        parent_castle_id = get_castle_id(parent_castle)
        if request.get("slot") is None:
            raise ValueError("slot is required when parent_castle is provided")

    allocate_castle_shell(
        build,
        build["spec"],
        parent_castle_id=parent_castle_id,
        slot=request.get("slot"),
    )


def get_castle_id(castle_or_id):
    if isinstance(castle_or_id, str):
        return castle_or_id

    return castle_or_id["id"]


def allocate_castle_shell(build, spec, parent_castle_id=None, slot=None, mount=None):
    castle_id = make_id("castle")
    castle = {
        "kind": "castle",
        "id": castle_id,
        "name": spec["name"],
        "parent": parent_castle_id,
        "slot": slot,
        "state": dict(spec.get("state", {})),
        "associates": {},
        "children": {},
        "inbox": [],
        "outbox": [],
        "active": False,
        "handle_fn": spec.get("handle_fn"),
        "reconcile_fn": spec.get("reconcile_fn"),
    }
    castles[castle_id] = castle
    build["castle_specs"][castle_id] = spec
    if mount is not None:
        build["castle_mounts"][castle_id] = mount
    build["castle_ids"].append(castle_id)
    trace.append(f"phase: allocated castle shell {castle['name']}")

    if parent_castle_id is not None:
        parent_castle = castles[parent_castle_id]
        if slot in parent_castle["children"]:
            raise ValueError(f"parent slot already has a child castle: {slot}")
        parent_castle["children"][slot] = castle_id
        trace.append(
            f"phase: mounted child castle {castle['name']} in slot {slot}"
        )

    for child_spec in spec.get("child_castles", []):
        child_template_fn = child_spec["template_fn"]
        child_context = child_spec.get("build_context", {})
        child_castle_spec = child_template_fn(child_context)
        allocate_castle_shell(
            build,
            child_castle_spec,
            parent_castle_id=castle_id,
            slot=child_spec["slot"],
            mount=child_spec.get("mount"),
        )


def register_global_exports(build):
    export_specs = []
    for castle_id in build["castle_ids"]:
        for export_spec in build["castle_specs"][castle_id].get("exports", []):
            export_specs.append(export_spec)

    export_names = set()

    for export_spec in export_specs:
        export_name = export_spec["name"]
        if export_name in export_names:
            raise ValueError(f"duplicate export in build spec: {export_name}")
        if export_name in global_castles:
            raise ValueError(f"global castle export already exists: {export_name}")

        export_names.add(export_name)

    for export_spec in export_specs:
        export_name = export_spec["name"]
        target_kind, target_id = resolve_export_target(build, export_spec["target"])
        if target_kind != "castle":
            raise ValueError(f"unsupported global export target kind: {target_kind}")

        global_castles[export_name] = target_id
        build["global_export_names"].append(export_name)
        castles[target_id].setdefault("global_names", []).append(export_name)
        trace.append(f"phase: exported castle {target_id} as {export_name}")


def resolve_export_target(build, target_spec):
    target_kind = target_spec["kind"]

    if target_kind == "castle":
        castle_id = find_built_castle_id(build, target_spec["name"])
        return "castle", castle_id

    raise ValueError(f"unknown export target spec kind: {target_kind}")


def allocate_associate_shells(build):
    for castle_id in build["castle_ids"]:
        allocate_castle_associate_shells(build, castle_id)


def allocate_castle_associate_shells(build, castle_id):
    spec = build["castle_specs"][castle_id]
    castle = castles[castle_id]
    associate_specs = spec.get("associates", [])
    mount = build["castle_mounts"].get(castle_id)

    parent_id = None
    grid_override = None
    if mount is not None:
        if len(associate_specs) != 1:
            raise ValueError(
                f"mounted castle must have exactly one root associate: {castle['name']}"
            )
        parent_id = resolve_mount_parent_associate(castle, mount)
        grid_override = mount.get("grid", {})

    for associate_spec in associate_specs:
        allocate_associate_shell(
            build,
            castle,
            castle_id,
            associate_spec,
            parent_id,
            grid_override=grid_override,
        )


def resolve_mount_parent_associate(castle, mount):
    parent_castle_id = castle["parent"]
    if parent_castle_id is None:
        raise ValueError(f"mounted castle has no parent castle: {castle['name']}")

    parent_castle = castles[parent_castle_id]
    parent_associate_name = mount["parent_associate"]
    return parent_castle["associates"][parent_associate_name]


def allocate_associate_shell(
    build,
    castle,
    castle_id,
    associate_spec,
    parent_id,
    grid_override=None,
):
    associate_id = make_id("associate")
    associate = {
        "kind": "associate",
        "id": associate_id,
        "name": associate_spec["name"],
        "associate_type": associate_spec["associate_type"],
        "host_castle": castle_id,
        "parent_associate": parent_id,
        "children": [],
        "data": dict(associate_spec.get("data", {})),
        "tk": None,
        "child_tk_parent": None,
        "layout": dict(associate_spec.get("layout", {})),
        "grid": dict(
            grid_override if grid_override is not None else associate_spec.get("grid", {})
        ),
        "outbox": [],
        "active": False,
    }
    associates[associate_id] = associate
    castle["associates"][associate["name"]] = associate_id
    build["associate_ids"].append(associate_id)

    if parent_id is not None:
        associates[parent_id]["children"].append(associate_id)

    trace.append(f"phase: allocated associate shell {associate['name']}")

    for child_spec in associate_spec.get("children", []):
        allocate_associate_shell(build, castle, castle_id, child_spec, associate_id)


def construct_widgets(build):
    for associate_id in build["associate_ids"]:
        associate = associates[associate_id]
        associate_type = associate["associate_type"]
        parent = get_widget_parent(build, associate)
        associate_type["setup_fn"](associate, parent)
        mark_dirty(associate_id)
        trace.append(f"phase: constructed widget for {associate['name']}")


def get_widget_parent(build, associate):
    parent_id = associate["parent_associate"]
    if parent_id is None:
        if tk_master is None:
            raise RuntimeError("setup_tk_bootstrap must be called before building")
        return tk_master

    parent_associate = associates[parent_id]
    if parent_associate.get("child_tk_parent") is not None:
        return parent_associate["child_tk_parent"]

    return parent_associate["tk"]


def apply_layout(build):
    for associate_id in build["associate_ids"]:
        associate = associates[associate_id]
        layout_parent = associate.get("child_tk_parent")
        layout = associate.get("layout", {})

        if layout_parent is not None:
            for column, options in layout.get("columnconfigure", {}).items():
                layout_parent.columnconfigure(column, **options)

            for row, options in layout.get("rowconfigure", {}).items():
                layout_parent.rowconfigure(row, **options)

        if associate["grid"]:
            associate["tk"].grid(**associate["grid"])

    trace.append("phase: applied layout")


def wire_default_routes(build):
    for associate_id in build["associate_ids"]:
        associate = associates[associate_id]
        route_id = make_id("route")
        route = {
            "kind": "route",
            "id": route_id,
            "from_kind": "associate",
            "from_id": associate_id,
            "from_box": "outbox",
            "to_kind": "castle",
            "to_id": associate["host_castle"],
            "to_box": "inbox",
            "active": False,
        }
        routes.append(route)
        build["route_ids"].append(route_id)

    trace.append("phase: wired default associate-to-castle routes")


def append_extra_routes(build):
    for castle_id in build["castle_ids"]:
        route_specs = build["castle_specs"][castle_id].get("routes", [])
        for route_spec in route_specs:
            from_kind, from_id, from_box = resolve_route_endpoint(
                build,
                route_spec["from"],
            )
            to_kind, to_id, to_box = resolve_route_endpoint(
                build,
                route_spec["to"],
            )

            route_id = make_id("route")
            route = {
                "kind": "route",
                "id": route_id,
                "from_kind": from_kind,
                "from_id": from_id,
                "from_box": from_box,
                "to_kind": to_kind,
                "to_id": to_id,
                "to_box": to_box,
                "active": False,
            }
            routes.append(route)
            build["route_ids"].append(route_id)
            trace.append(f"phase: appended template route {route_id}")


def resolve_route_endpoint(build, endpoint_spec):
    endpoint_kind = endpoint_spec["kind"]
    endpoint_box = endpoint_spec["box"]

    if endpoint_kind == "global_castle":
        castle_id = global_castles[endpoint_spec["name"]]
        return "castle", castle_id, endpoint_box

    if endpoint_kind == "castle":
        castle_id = find_built_castle_id(build, endpoint_spec["name"])
        return "castle", castle_id, endpoint_box

    if endpoint_kind == "associate":
        associate_id = find_built_associate_id(build, endpoint_spec["name"])
        return "associate", associate_id, endpoint_box

    raise ValueError(f"unknown route endpoint spec kind: {endpoint_kind}")


def find_built_castle_id(build, castle_name):
    for castle_id in build["castle_ids"]:
        if castles[castle_id]["name"] == castle_name:
            return castle_id

    raise KeyError(f"built castle not found for route endpoint: {castle_name}")


def find_built_associate_id(build, associate_name):
    for associate_id in build["associate_ids"]:
        if associates[associate_id]["name"] == associate_name:
            return associate_id

    raise KeyError(f"built associate not found for route endpoint: {associate_name}")


def activate_build(build):
    for castle_id in build["castle_ids"]:
        castles[castle_id]["active"] = True

    for associate_id in build["associate_ids"]:
        associates[associate_id]["active"] = True

    for route in routes:
        if route["id"] in build["route_ids"]:
            route["active"] = True

    trace.append("phase: activated build")


def get_associate(castle, associate_name):
    associate_id = castle["associates"][associate_name]
    return associates[associate_id]


def target_associate(associate_or_id):
    global current_target_associate
    if isinstance(associate_or_id, str):
        current_target_associate = associates[associate_or_id]
    else:
        current_target_associate = associate_or_id


def set_data(key, value):
    if current_target_associate is None:
        raise RuntimeError("set_data called without target_associate")

    old_value = current_target_associate["data"].get(key)
    if old_value == value:
        return False

    current_target_associate["data"][key] = value
    mark_dirty(current_target_associate)
    return True


def mark_castle_dirty(castle_or_id):
    if isinstance(castle_or_id, str):
        dirty_castles.add(castle_or_id)
    else:
        dirty_castles.add(castle_or_id["id"])


def mark_dirty(associate_or_id):
    if isinstance(associate_or_id, str):
        dirty_associates.add(associate_or_id)
    else:
        dirty_associates.add(associate_or_id["id"])


def mark_castle_associate_dirty(castle, associate_name):
    mark_dirty(castle["associates"][associate_name])


def deliver_messages():
    routes_by_source = {}
    for route in routes:
        if route["active"]:
            source_key = (route["from_kind"], route["from_id"], route["from_box"])
            routes_by_source.setdefault(source_key, []).append(route)

    for source_key, source_routes in routes_by_source.items():
        from_kind, from_id, from_box = source_key
        source = get_route_endpoint(from_kind, from_id)
        source_box = source[from_box]
        messages = list(source_box)
        source_box.clear()

        for message in messages:
            for route in source_routes:
                destination = get_route_endpoint(route["to_kind"], route["to_id"])
                destination_box = destination[route["to_box"]]
                delivered_message = dict(message)
                if isinstance(message.get("payload"), dict):
                    delivered_message["payload"] = dict(message["payload"])
                destination_box.append(delivered_message)
                trace.append(
                    f"delivered {message['type']} from "
                    f"{source['name']} to {destination['name']}"
                )


def get_route_endpoint(kind, endpoint_id):
    if kind == "associate":
        return associates[endpoint_id]
    if kind == "castle":
        return castles[endpoint_id]
    raise ValueError(f"unknown route endpoint kind: {kind}")


def process_castle_messages():
    for castle in castles.values():
        if not castle["active"]:
            continue

        handle_fn = castle.get("handle_fn")
        if handle_fn is None:
            continue

        while castle["inbox"]:
            message = castle["inbox"].pop(0)
            result = handle_fn(castle, message)
            if result is None:
                result = HANDLED_DIRTY
            if result == HANDLED_DIRTY:
                mark_castle_dirty(castle)
            elif result not in (IGNORED, HANDLED):
                raise ValueError(f"unknown castle handler result: {result}")


def reconcile_dirty_castles():
    while dirty_castles:
        castle_id = dirty_castles.pop()
        castle = castles.get(castle_id)
        if castle is None or not castle["active"]:
            continue

        reconcile_fn = castle.get("reconcile_fn")
        if reconcile_fn is None:
            continue

        reconcile_fn(castle)
        trace.append(f"reconciled {castle['name']}")


def project_dirty_associates():
    while dirty_associates:
        associate_id = dirty_associates.pop()
        associate = associates.get(associate_id)
        if associate is None or not associate["active"]:
            continue

        associate_type = associate["associate_type"]
        associate_type["project_fn"](associate)
        trace.append(f"projected {associate['name']}")


def runtime_tick():
    process_incoming_builds()
    deliver_messages()
    process_castle_messages()
    reconcile_dirty_castles()
    project_dirty_associates()
    tk_master.after(50, runtime_tick)


def cleanup_failed_build(build):
    revoke_global_exports(build)
    destroy_build_associate_widgets(build)
    unregister_build_records(build)
    trace.append(f"cleanup: removed failed build {build['request']['id']} records")


def revoke_global_exports(build):
    for export_name in build.get("global_export_names", []):
        castle_id = global_castles.get(export_name)
        if castle_id is not None:
            castle = castles.get(castle_id)
            if castle is not None and export_name in castle.get("global_names", []):
                castle["global_names"].remove(export_name)

        global_castles.pop(export_name, None)
        trace.append(f"cleanup: revoked global export {export_name}")

    build["global_export_names"].clear()


def destroy_build_associate_widgets(build):
    for associate_id in reversed(build.get("associate_ids", [])):
        associate = associates.get(associate_id)
        if associate is None:
            continue

        destroy_fn = associate["associate_type"].get("destroy_fn")
        if destroy_fn is not None:
            destroy_fn(associate)


def unregister_build_records(build):
    route_ids = set(build.get("route_ids", []))
    if route_ids:
        routes[:] = [route for route in routes if route["id"] not in route_ids]

    for associate_id in build.get("associate_ids", []):
        dirty_associates.discard(associate_id)
        associates.pop(associate_id, None)

    for castle_id in build.get("castle_ids", []):
        dirty_castles.discard(castle_id)
        castles.pop(castle_id, None)

    build["route_ids"].clear()
    build["associate_ids"].clear()
    build["castle_specs"].clear()
    build["castle_mounts"].clear()
    build["castle_ids"].clear()


def setup_tk_bootstrap():
    global tk_master
    tk_master = tk.Tk()
    tk_master.withdraw()
    setup_global_castles()
    return tk_master


def run():
    if tk_master is None:
        raise RuntimeError("setup_tk_bootstrap must be called before run")

    tk_master.after(0, runtime_tick)
    tk_master.mainloop()


def destroy_all():
    trace.append("destroy: begin")
    deactivate_all()
    clear_runtime_queues()
    revoke_completed_global_exports()
    destroy_associate_widgets()
    unregister_runtime_records()
    trace.append("destroy: complete")


def deactivate_all():
    for route in routes:
        route["active"] = False

    for castle in castles.values():
        castle["active"] = False

    for associate in associates.values():
        associate["active"] = False

    trace.append("destroy: deactivated routes, castles, and associates")


def clear_runtime_queues():
    incoming_builds.clear()
    active_builds.clear()
    dirty_castles.clear()
    dirty_associates.clear()

    for castle in castles.values():
        castle["inbox"].clear()
        castle["outbox"].clear()

    for associate in associates.values():
        associate["outbox"].clear()

    trace.append("destroy: cleared build, message, and dirty queues")


def revoke_completed_global_exports():
    for build in completed_builds:
        revoke_global_exports(build)

    trace.append("destroy: revoked completed build global exports")


def destroy_associate_widgets():
    for associate in reversed(list(associates.values())):
        destroy_fn = associate["associate_type"].get("destroy_fn")
        if destroy_fn is not None:
            destroy_fn(associate)

    trace.append("destroy: destroyed associate widgets child-first")


def unregister_runtime_records():
    global current_target_associate
    current_target_associate = None
    routes.clear()
    associates.clear()
    castles.clear()
    global_castles.clear()
    completed_builds.clear()
    faulty_builds.clear()

    trace.append("destroy: unregistered runtime records")
