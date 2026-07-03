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
dirty_associates = set()
current_target_associate = None
tk_master = None
global_castles = {}

TRACE_CASTLE = "global_trace"

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
    name,
    template_fn,
    build_context=None,
    parent_castle=None,
    slot=None,
    activate_when_complete=True,
):
    return {
        "kind": "build_request",
        "id": make_id("build"),
        "name": name,
        "template_fn": template_fn,
        "build_context": build_context or {},
        "parent_castle": parent_castle,
        "slot": slot,
        "activate_when_complete": activate_when_complete,
    }


def submit_build_request(build_request):
    incoming_builds.append(build_request)
    trace.append(f"submitted build {build_request['name']}")


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
            "castle_ids": [],
            "associate_ids": [],
            "route_ids": [],
            "status": "active",
        }
        active_builds.append(build)
        trace.append(f"started build {request['name']}")

        try:
            process_build(build)
        except Exception as exc:
            build["status"] = "faulty"
            build["error"] = repr(exc)
            active_builds.remove(build)
            faulty_builds.append(build)
            trace.append(f"build {request['name']} failed: {exc}")
        else:
            build["status"] = "completed"
            active_builds.remove(build)
            completed_builds.append(build)
            trace.append(f"completed build {request['name']}")


def process_build(build):
    expand_template(build)
    allocate_castle_shells(build)
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
    spec = build["spec"]
    castle_id = make_id("castle")
    castle = {
        "kind": "castle",
        "id": castle_id,
        "name": spec["name"],
        "state": dict(spec.get("state", {})),
        "associates": {},
        "children": {},
        "inbox": [],
        "outbox": [],
        "active": False,
        "handle_fn": spec.get("handle_fn"),
    }
    castles[castle_id] = castle
    build["castle_ids"].append(castle_id)
    trace.append(f"phase: allocated castle shell {castle['name']}")


def allocate_associate_shells(build):
    spec = build["spec"]
    castle_id = build["castle_ids"][0]
    castle = castles[castle_id]

    for associate_spec in spec.get("associates", []):
        allocate_associate_shell(build, castle, castle_id, associate_spec, None)


def allocate_associate_shell(build, castle, castle_id, associate_spec, parent_id):
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
        "grid": dict(associate_spec.get("grid", {})),
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
    castle_id = build["castle_ids"][0]
    for associate_id in build["associate_ids"]:
        route_id = make_id("route")
        route = {
            "kind": "route",
            "id": route_id,
            "from_kind": "associate",
            "from_id": associate_id,
            "from_box": "outbox",
            "to_kind": "castle",
            "to_id": castle_id,
            "to_box": "inbox",
            "active": False,
        }
        routes.append(route)
        build["route_ids"].append(route_id)

    wire_global_trace_route(build, castle_id)
    trace.append("phase: wired default associate-to-castle routes")


def wire_global_trace_route(build, castle_id):
    if TRACE_CASTLE not in global_castles:
        return

    trace_castle_id = global_castles[TRACE_CASTLE]
    if trace_castle_id == castle_id:
        return

    route_id = make_id("route")
    route = {
        "kind": "route",
        "id": route_id,
        "from_kind": "castle",
        "from_id": trace_castle_id,
        "from_box": "outbox",
        "to_kind": "castle",
        "to_id": castle_id,
        "to_box": "inbox",
        "active": False,
    }
    routes.append(route)
    build["route_ids"].append(route_id)


def append_extra_routes(build):
    if build["spec"].get("routes"):
        trace.append("TODO: extra template routes are not implemented in this demo")


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
            handle_fn(castle, message)


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
    project_dirty_associates()
    tk_master.after(50, runtime_tick)


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
    dirty_associates.clear()

    for castle in castles.values():
        castle["inbox"].clear()
        castle["outbox"].clear()

    for associate in associates.values():
        associate["outbox"].clear()

    trace.append("destroy: cleared build, message, and dirty queues")


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
