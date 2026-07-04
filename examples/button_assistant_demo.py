"""
TkMachina runtime-owned construction demo.

This is a runnable thought-object, not a framework. It proves a small loop:

template describes -> RT builds -> RT wires -> RT activates -> associates emit
-> RT delivers -> castle interprets -> RT projects
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tkmachina import rt
from tkmachina.associates import (
    BUTTON_ASSOCIATE_TYPE,
    LABEL_ASSOCIATE_TYPE,
    WINDOW_ASSOCIATE_TYPE,
)


def demo_template(build_context):
    return {
        "kind": "castle_spec",
        "name": "demo_castle",
        "state": {
            "press_count": 0,
            "button_enabled": True,
            "window_width": None,
            "window_height": None,
            "trace_generation": 0,
            "trace_wraplength": build_context.get("trace_wraplength", 380),
        },
        "handle_fn": handle_demo_castle_message,
        "reconcile_fn": reconcile_demo_castle,
        "child_castles": [
            {
                "kind": "child_castle_spec",
                "name": "trace_log",
                "template_fn": trace_log_castle_template,
                "build_context": {
                    "trace_wraplength": build_context.get("trace_wraplength", 380),
                },
            },
        ],
        "associates": [
            {
                "kind": "associate_spec",
                "name": "main_window",
                "associate_type": WINDOW_ASSOCIATE_TYPE,
                "desired": {
                    "title": "TkMachina RT Demo",
                    "desired_width": 460,
                    "desired_height": 480,
                    "min_width": 420,
                    "min_height": 480,
                    "content_padding": 16,
                },
                "observed": {
                    "actual_width": None,
                    "actual_height": None,
                },
            },
            {
                "kind": "associate_spec",
                "name": "priority_button",
                "associate_type": BUTTON_ASSOCIATE_TYPE,
                "desired": {
                    "text": "Required (5 left)",
                    "enabled": True,
                },
            },
            {
                "kind": "associate_spec",
                "name": "count_label",
                "associate_type": LABEL_ASSOCIATE_TYPE,
                "desired": {
                    "text": "Castle state: press_count = 0",
                },
            },
            {
                "kind": "associate_spec",
                "name": "size_label",
                "associate_type": LABEL_ASSOCIATE_TYPE,
                "desired": {
                    "text": "Window frame: waiting for resize event",
                },
            },
            {
                "kind": "associate_spec",
                "name": "reset_button",
                "associate_type": BUTTON_ASSOCIATE_TYPE,
                "desired": {
                    "text": "Reset",
                    "enabled": True,
                },
            },
            {
                "kind": "associate_spec",
                "name": "replace_trace_button",
                "associate_type": BUTTON_ASSOCIATE_TYPE,
                "desired": {
                    "text": "Replace trace",
                    "enabled": True,
                },
            },
        ],
        "spots": {
            "name": "main_window_spot",
            "layout": {
                "columnconfigure": {0: {"weight": 1}},
            },
            "children": [
                {
                    "name": "priority_button_spot",
                    "grid": {"row": 0, "column": 0, "sticky": "ew"},
                },
                {
                    "name": "count_label_spot",
                    "grid": {
                        "row": 1,
                        "column": 0,
                        "sticky": "w",
                        "pady": (14, 4),
                    },
                },
                {
                    "name": "size_label_spot",
                    "grid": {"row": 2, "column": 0, "sticky": "w"},
                },
                {
                    "name": "trace_log_spot",
                    "grid": {
                        "row": 3,
                        "column": 0,
                        "sticky": "ew",
                        "pady": (14, 0),
                    },
                },
                {
                    "name": "reset_button_spot",
                    "grid": {
                        "row": 4,
                        "column": 0,
                        "sticky": "e",
                        "pady": (14, 0),
                    },
                },
                {
                    "name": "replace_trace_button_spot",
                    "grid": {
                        "row": 5,
                        "column": 0,
                        "sticky": "e",
                        "pady": (8, 0),
                    },
                },
            ],
        },
        "placements": {
            "main_window_spot": {
                "kind": "associate",
                "name": "main_window",
            },
            "priority_button_spot": {
                "kind": "associate",
                "name": "priority_button",
            },
            "count_label_spot": {
                "kind": "associate",
                "name": "count_label",
            },
            "size_label_spot": {
                "kind": "associate",
                "name": "size_label",
            },
            "trace_log_spot": {
                "kind": "child_castle",
                "name": "trace_log",
            },
            "reset_button_spot": {
                "kind": "associate",
                "name": "reset_button",
            },
            "replace_trace_button_spot": {
                "kind": "associate",
                "name": "replace_trace_button",
            },
        },
    }


def trace_log_castle_template(build_context):
    return {
        "kind": "castle_spec",
        "name": "trace_log_castle",
        "state": {
            "trace_version": 0,
        },
        "handle_fn": handle_trace_log_castle_message,
        "reconcile_fn": reconcile_trace_log_castle,
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
                    "name": "trace_log_castle",
                    "box": "inbox",
                },
            },
        ],
        "associates": [
            {
                "kind": "associate_spec",
                "name": "trace_label",
                "associate_type": LABEL_ASSOCIATE_TYPE,
                "desired": {
                    "text": build_context.get(
                        "label_prefix",
                        "Recent RT trace",
                    ) + ": waiting",
                    "wraplength": build_context.get("trace_wraplength", 380),
                    "label_prefix": build_context.get(
                        "label_prefix",
                        "Recent RT trace",
                    ),
                },
            },
        ],
    }


def handle_demo_castle_message(castle, message):
    castle_label = f"{castle['name']}[{castle['id']}]"

    if message["type"] == "button_pressed" and message["origin"] == "priority_button":
        castle["state"]["press_count"] += 1
        count = castle["state"]["press_count"]
        castle["state"]["button_enabled"] = count < 5
        rt.add_trace(f"{castle_label} handled priority_button; count is now {count}")
        return rt.HANDLED_DIRTY
    elif message["type"] == "button_pressed" and message["origin"] == "reset_button":
        castle["state"]["press_count"] = 0
        castle["state"]["button_enabled"] = True
        rt.add_trace(f"{castle_label} handled reset_button")
        return rt.HANDLED_DIRTY
    elif (
        message["type"] == "button_pressed"
        and message["origin"] == "replace_trace_button"
    ):
        castle["state"]["trace_generation"] += 1
        generation = castle["state"]["trace_generation"]
        rt.target_castle(castle)
        rt.schedule_replacement(
            "trace_log_spot",
            trace_log_castle_template,
            {
                "trace_wraplength": castle["state"]["trace_wraplength"],
                "label_prefix": f"Recent RT trace #{generation}",
            },
        )
        rt.add_trace(f"{castle_label} scheduled trace replacement #{generation}")
        return rt.HANDLED_DIRTY
    elif message["type"] == "window_resized":
        castle["state"]["window_width"] = message["payload"]["width"]
        castle["state"]["window_height"] = message["payload"]["height"]
        rt.add_trace(
            f"{castle_label} handled window_resized; "
            f"size is {message['payload']['width']}x{message['payload']['height']}"
        )
        return rt.HANDLED_DIRTY

    return rt.IGNORED


def reconcile_demo_castle(castle):
    state = castle["state"]
    priority_button = rt.get_associate(castle, "priority_button")
    count_label = rt.get_associate(castle, "count_label")
    size_label = rt.get_associate(castle, "size_label")

    rt.target_associate(priority_button)
    rt.set_desired("enabled", state["button_enabled"])
    if state["button_enabled"]:
        remaining = 5 - state["press_count"]
        rt.set_desired("text", f"Required ({remaining} left)")
    else:
        rt.set_desired("text", "Required complete")

    rt.target_associate(count_label)
    rt.set_desired("text", f"Castle state: press_count = {state['press_count']}")

    rt.target_associate(size_label)
    if state["window_width"] is None or state["window_height"] is None:
        rt.set_desired("text", "Window frame: waiting for resize event")
    else:
        rt.set_desired(
            "text",
            f"Window frame: {state['window_width']} x {state['window_height']}",
        )


def handle_trace_log_castle_message(castle, message):
    if message["type"] == "trace_changed":
        castle["state"]["trace_version"] = message["payload"]["version"]
        return rt.HANDLED_DIRTY

    return rt.IGNORED


def reconcile_trace_log_castle(castle):
    trace_label = rt.get_associate(castle, "trace_label")
    label_prefix = trace_label["desired"].get("label_prefix", "Recent RT trace")
    rt.target_associate(trace_label)
    recent_trace = rt.get_trace_entries()[-20:]
    if recent_trace:
        rt.set_desired(
            "text",
            f"{label_prefix}:\n" + "\n".join(f"- {line}" for line in recent_trace),
        )
    else:
        rt.set_desired("text", f"{label_prefix}: waiting")


def main():
    rt.reset()
    rt.setup_tk_bootstrap()
    rt.submit_build_request(
        rt.make_build_request(
            template_fn=demo_template,
            build_context={
                "trace_wraplength": 400,
            },
        )
    )
    rt.submit_build_request(
        rt.make_build_request(
            template_fn=demo_template,
            build_context={
                "trace_wraplength": 400,
            },
        )
    )
    rt.run()


if __name__ == "__main__":
    main()
