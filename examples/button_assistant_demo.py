"""
TkMachina runtime-owned construction demo.

This is a runnable thought-object, not a framework. It proves a small loop:

template describes -> RT builds -> RT wires -> RT activates -> associates emit
-> RT delivers -> castle interprets -> RT projects
"""

from __future__ import annotations

from associates import BUTTON_ASSOCIATE_TYPE, LABEL_ASSOCIATE_TYPE, WINDOW_ASSOCIATE_TYPE
import rt


def demo_template(build_context):
    return {
        "kind": "castle_spec",
        "name": "demo_castle",
        "state": {
            "press_count": 0,
            "button_enabled": True,
            "window_width": None,
            "window_height": None,
        },
        "handle_fn": handle_demo_castle_message,
        "associates": [
            {
                "kind": "associate_spec",
                "name": "main_window",
                "associate_type": WINDOW_ASSOCIATE_TYPE,
                "data": {
                    "title": "TkMachina RT Demo",
                    "desired_width": 460,
                    "desired_height": 480,
                    "min_width": 420,
                    "min_height": 480,
                    "actual_width": None,
                    "actual_height": None,
                    "content_padding": 16,
                },
                "layout": {
                    "columnconfigure": {0: {"weight": 1}},
                },
                "children": [
                    {
                        "kind": "associate_spec",
                        "name": "priority_button",
                        "associate_type": BUTTON_ASSOCIATE_TYPE,
                        "data": {
                            "text": "Required (5 left)",
                            "enabled": True,
                        },
                        "grid": {"row": 0, "column": 0, "sticky": "ew"},
                    },
                    {
                        "kind": "associate_spec",
                        "name": "count_label",
                        "associate_type": LABEL_ASSOCIATE_TYPE,
                        "data": {
                            "text": "Castle state: press_count = 0",
                        },
                        "grid": {
                            "row": 1,
                            "column": 0,
                            "sticky": "w",
                            "pady": (14, 4),
                        },
                    },
                    {
                        "kind": "associate_spec",
                        "name": "size_label",
                        "associate_type": LABEL_ASSOCIATE_TYPE,
                        "data": {
                            "text": "Window frame: waiting for resize event",
                        },
                        "grid": {"row": 2, "column": 0, "sticky": "w"},
                    },
                    {
                        "kind": "associate_spec",
                        "name": "trace_label",
                        "associate_type": LABEL_ASSOCIATE_TYPE,
                        "data": {
                            "text": "Recent RT trace: waiting",
                            "wraplength": build_context.get("trace_wraplength", 380),
                        },
                        "grid": {
                            "row": 3,
                            "column": 0,
                            "sticky": "ew",
                            "pady": (14, 0),
                        },
                    },
                    {
                        "kind": "associate_spec",
                        "name": "reset_button",
                        "associate_type": BUTTON_ASSOCIATE_TYPE,
                        "data": {
                            "text": "Reset",
                            "enabled": True,
                        },
                        "grid": {
                            "row": 4,
                            "column": 0,
                            "sticky": "e",
                            "pady": (14, 0),
                        },
                    },
                ],
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
        sync_demo_castle_view_state(castle)
    elif message["type"] == "button_pressed" and message["origin"] == "reset_button":
        castle["state"]["press_count"] = 0
        castle["state"]["button_enabled"] = True
        rt.add_trace(f"{castle_label} handled reset_button")
        sync_demo_castle_view_state(castle)
    elif message["type"] == "window_resized":
        castle["state"]["window_width"] = message["payload"]["width"]
        castle["state"]["window_height"] = message["payload"]["height"]
        rt.add_trace(
            f"{castle_label} handled window_resized; "
            f"size is {message['payload']['width']}x{message['payload']['height']}"
        )
        sync_demo_castle_view_state(castle)
    elif message["type"] == "trace_changed":
        sync_demo_castle_view_state(castle)


def sync_demo_castle_view_state(castle):
    state = castle["state"]
    priority_button = rt.get_associate(castle, "priority_button")
    count_label = rt.get_associate(castle, "count_label")
    size_label = rt.get_associate(castle, "size_label")
    trace_label = rt.get_associate(castle, "trace_label")

    rt.target_associate(priority_button)
    rt.set_data("enabled", state["button_enabled"])
    if state["button_enabled"]:
        remaining = 5 - state["press_count"]
        rt.set_data("text", f"Required ({remaining} left)")
    else:
        rt.set_data("text", "Required complete")

    rt.target_associate(count_label)
    rt.set_data("text", f"Castle state: press_count = {state['press_count']}")

    rt.target_associate(size_label)
    if state["window_width"] is None or state["window_height"] is None:
        rt.set_data("text", "Window frame: waiting for resize event")
    else:
        rt.set_data(
            "text",
            f"Window frame: {state['window_width']} x {state['window_height']}",
        )

    rt.target_associate(trace_label)
    recent_trace = rt.get_trace_entries()[-20:]
    if recent_trace:
        rt.set_data(
            "text",
            "Recent RT trace:\n" + "\n".join(f"- {line}" for line in recent_trace),
        )
    else:
        rt.set_data("text", "Recent RT trace: waiting")


def main():
    rt.reset()
    rt.setup_tk_bootstrap()
    build_request = rt.make_build_request(
        name="demo",
        template_fn=demo_template,
        build_context={
            "trace_wraplength": 400,
        },
        activate_when_complete=True,
    )
    rt.submit_build_request(build_request)
    rt.submit_build_request(build_request)
    rt.run()


if __name__ == "__main__":
    main()
