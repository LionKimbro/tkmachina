"""
TkMachina runtime-owned construction demo.

This is a runnable thought-object, not a framework. It proves a small loop:

template describes -> RT builds -> RT wires -> RT activates -> associates emit
-> RT delivers -> castle interprets -> RT projects
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import rt


def make_button_associate_type():
    return {
        "name": "button",
        "setup_fn": setup_button_associate,
        "project_fn": project_button_associate,
        "destroy_fn": destroy_widget_associate,
    }


def make_window_associate_type():
    return {
        "name": "window",
        "setup_fn": setup_window_associate,
        "project_fn": project_window_associate,
        "destroy_fn": destroy_window_associate,
    }


def make_label_associate_type():
    return {
        "name": "label",
        "setup_fn": setup_label_associate,
        "project_fn": project_label_associate,
        "destroy_fn": destroy_widget_associate,
    }


def setup_window_associate(associate, tk_master):
    data = associate["data"]
    window = tk.Toplevel(tk_master)
    content_frame = ttk.Frame(window, padding=data.get("content_padding", 0))
    content_frame.grid(row=0, column=0, sticky="nsew")
    window.columnconfigure(0, weight=1)
    window.rowconfigure(0, weight=1)

    def on_configure(event):
        if event.widget is not window:
            return

        old_size = (data.get("actual_width"), data.get("actual_height"))
        new_size = (event.width, event.height)
        if old_size == new_size:
            return

        data["actual_width"] = event.width
        data["actual_height"] = event.height
        associate["outbox"].append(
            {
                "kind": "event",
                "type": "window_resized",
                "origin": associate["name"],
                "emitter": associate["name"],
                "payload": {
                    "width": event.width,
                    "height": event.height,
                },
            }
        )

    def on_close():
        rt.destroy_all()
        tk_master.destroy()

    window.bind("<Configure>", on_configure)
    window.protocol("WM_DELETE_WINDOW", on_close)
    associate["tk"] = window
    associate["child_tk_parent"] = content_frame


def project_window_associate(associate):
    data = associate["data"]
    window = associate["tk"]

    if data.get("title") and window.title() != data["title"]:
        window.title(data["title"])

    min_width = data.get("min_width")
    min_height = data.get("min_height")
    if min_width is not None and min_height is not None:
        window.minsize(min_width, min_height)

    desired_width = data.get("desired_width")
    desired_height = data.get("desired_height")
    desired_size = (desired_width, desired_height)
    if (
        desired_width is not None
        and desired_height is not None
        and data.get("_projected_size") != desired_size
    ):
        window.geometry(f"{desired_width}x{desired_height}")
        data["_projected_size"] = desired_size


def setup_button_associate(associate, tk_parent):
    def on_click():
        associate["outbox"].append(
            {
                "kind": "event",
                "type": "button_pressed",
                "origin": associate["name"],
                "emitter": associate["name"],
                "payload": {},
            }
        )

    associate["tk"] = ttk.Button(tk_parent, command=on_click)


def project_button_associate(associate):
    data = associate["data"]
    widget = associate["tk"]

    if widget.cget("text") != data["text"]:
        widget.config(text=data["text"])

    desired_state = "normal" if data.get("enabled", True) else "disabled"
    if widget.cget("state") != desired_state:
        widget.config(state=desired_state)


def setup_label_associate(associate, tk_parent):
    associate["tk"] = ttk.Label(tk_parent, justify="left")


def project_label_associate(associate):
    data = associate["data"]
    widget = associate["tk"]

    if widget.cget("text") != data["text"]:
        widget.config(text=data["text"])

    desired_wraplength = data.get("wraplength")
    if (
        desired_wraplength is not None
        and widget.cget("wraplength") != desired_wraplength
    ):
        widget.config(wraplength=desired_wraplength)


def destroy_widget_associate(associate):
    widget = associate.get("tk")
    if widget is not None:
        widget.destroy()
        associate["tk"] = None


def destroy_window_associate(associate):
    widget = associate.get("tk")
    if widget is not None:
        widget.destroy()
        associate["tk"] = None
        associate["child_tk_parent"] = None


WINDOW_ASSOCIATE_TYPE = make_window_associate_type()
BUTTON_ASSOCIATE_TYPE = make_button_associate_type()
LABEL_ASSOCIATE_TYPE = make_label_associate_type()


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
        "project_fn": project_demo_castle,
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
                            "text": "Required",
                            "enabled": True,
                        },
                        "grid": {"row": 0, "column": 0, "sticky": "ew"},
                    },
                    {
                        "kind": "associate_spec",
                        "name": "count_label",
                        "associate_type": LABEL_ASSOCIATE_TYPE,
                        "data": {
                            "text": "",
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
                            "text": "",
                        },
                        "grid": {"row": 2, "column": 0, "sticky": "w"},
                    },
                    {
                        "kind": "associate_spec",
                        "name": "trace_label",
                        "associate_type": LABEL_ASSOCIATE_TYPE,
                        "data": {
                            "text": "",
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
    if message["type"] == "button_pressed" and message["origin"] == "priority_button":
        castle["state"]["press_count"] += 1
        count = castle["state"]["press_count"]
        castle["state"]["button_enabled"] = count < 5
        rt.trace.append(f"castle handled priority_button; count is now {count}")
        project_demo_castle(castle)
    elif message["origin"] == "reset_button":
        castle["state"]["press_count"] = 0
        castle["state"]["button_enabled"] = True
        rt.trace.append("castle handled reset_button")
        project_demo_castle(castle)
    elif message["type"] == "window_resized":
        castle["state"]["window_width"] = message["payload"]["width"]
        castle["state"]["window_height"] = message["payload"]["height"]
        rt.trace.append(
            "castle handled window_resized; "
            f"size is {message['payload']['width']}x{message['payload']['height']}"
        )
        project_demo_castle(castle)


def project_demo_castle(castle):
    state = castle["state"]
    priority_button = rt.get_associate(castle, "priority_button")
    count_label = rt.get_associate(castle, "count_label")
    size_label = rt.get_associate(castle, "size_label")
    trace_label = rt.get_associate(castle, "trace_label")

    priority_button["data"]["enabled"] = state["button_enabled"]
    if state["button_enabled"]:
        remaining = 5 - state["press_count"]
        priority_button["data"]["text"] = f"Required ({remaining} left)"
    else:
        priority_button["data"]["text"] = "Required complete"

    count_label["data"]["text"] = f"Castle state: press_count = {state['press_count']}"
    if state["window_width"] is None or state["window_height"] is None:
        size_label["data"]["text"] = "Window frame: waiting for resize event"
    else:
        size_label["data"]["text"] = (
            f"Window frame: {state['window_width']} x {state['window_height']}"
        )

    recent_trace = rt.trace[-20:]
    if recent_trace:
        trace_label["data"]["text"] = "Recent RT trace:\n" + "\n".join(
            f"- {line}" for line in recent_trace
        )
    else:
        trace_label["data"]["text"] = "Recent RT trace: waiting"

    rt.mark_dirty(priority_button)
    rt.mark_dirty(count_label)
    rt.mark_dirty(size_label)
    rt.mark_dirty(trace_label)


def setup_tk_bootstrap():
    root = tk.Tk()
    root.withdraw()
    return root


def main():
    rt.reset()
    root = setup_tk_bootstrap()

    build_request = rt.make_build_request(
        name="demo",
        template_fn=demo_template,
        build_context={
            "tk_master": root,
            "trace_wraplength": 400,
        },
        activate_when_complete=True,
    )
    rt.submit_build_request(build_request)
    root.after(0, rt.runtime_tick, root)
    root.mainloop()


if __name__ == "__main__":
    main()
