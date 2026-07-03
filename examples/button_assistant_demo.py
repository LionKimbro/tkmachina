"""
Tiny TkMachina Assistant demo, version 2.

This is intentionally not a full Little Castles runtime. It demonstrates one
light castle hosting button and label Assistants. The only raw Tk widgets are
the root and one container frame. User action enters through Assistant outboxes,
and display updates happen through Assistant data plus projection.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


def make_button_assistant_type():
    return {
        "name": "button",
        "setup_fn": setup_button_assistant,
        "project_fn": project_button_assistant,
        "destroy_fn": destroy_widget_assistant,
    }


def make_label_assistant_type():
    return {
        "name": "label",
        "setup_fn": setup_label_assistant,
        "project_fn": project_label_assistant,
        "destroy_fn": destroy_widget_assistant,
    }


def make_button_assistant(name, assistant_type, text, enabled=True):
    return {
        "kind": "assistant",
        "name": name,
        "assistant_type": assistant_type,
        "data": {
            "text": text,
            "enabled": enabled,
        },
        "tk": None,
        "outbox": [],
    }


def make_label_assistant(name, assistant_type, text="", wraplength=None):
    return {
        "kind": "assistant",
        "name": name,
        "assistant_type": assistant_type,
        "data": {
            "text": text,
            "wraplength": wraplength,
        },
        "tk": None,
        "outbox": [],
    }


def project_button_assistant(assistant):
    data = assistant["data"]
    widget = assistant["tk"]

    if widget.cget("text") != data["text"]:
        widget.config(text=data["text"])

    desired_state = "normal" if data.get("enabled", True) else "disabled"
    if widget.cget("state") != desired_state:
        widget.config(state=desired_state)


def project_label_assistant(assistant):
    data = assistant["data"]
    widget = assistant["tk"]

    if widget.cget("text") != data["text"]:
        widget.config(text=data["text"])

    desired_wraplength = data.get("wraplength")
    if (
        desired_wraplength is not None
        and widget.cget("wraplength") != desired_wraplength
    ):
        widget.config(wraplength=desired_wraplength)


def setup_button_assistant(assistant, tk_parent):
    def on_click():
        assistant["outbox"].append(
            {
                "kind": "event",
                "type": "button_pressed",
                "origin": assistant["name"],
                "emitter": assistant["name"],
                "payload": {},
            }
        )

    assistant["tk"] = ttk.Button(tk_parent, command=on_click)
    project_button_assistant(assistant)


def setup_label_assistant(assistant, tk_parent):
    assistant["tk"] = ttk.Label(tk_parent, justify="left")
    project_label_assistant(assistant)


def destroy_widget_assistant(assistant):
    widget = assistant.get("tk")
    if widget is not None:
        widget.destroy()
        assistant["tk"] = None


def make_demo_castle(root):
    button_type = make_button_assistant_type()
    label_type = make_label_assistant_type()

    priority_button = make_button_assistant(
        name="priority_button",
        assistant_type=button_type,
        text="Required",
        enabled=True,
    )
    reset_button = make_button_assistant(
        name="reset_button",
        assistant_type=button_type,
        text="Reset",
        enabled=True,
    )
    count_label = make_label_assistant(
        name="count_label",
        assistant_type=label_type,
    )
    trace_label = make_label_assistant(
        name="trace_label",
        assistant_type=label_type,
        wraplength=360,
    )

    return {
        "kind": "castle",
        "name": "demo_castle",
        "tk_root": root,
        "state": {
            "press_count": 0,
            "button_enabled": True,
        },
        "assistants": {
            priority_button["name"]: priority_button,
            reset_button["name"]: reset_button,
            count_label["name"]: count_label,
            trace_label["name"]: trace_label,
        },
        "inbox": [],
        "trace": [],
    }


def setup_castle_surface(castle):
    root = castle["tk_root"]
    root.title("TkMachina Assistant Demo")
    root.geometry("420x220")
    root.minsize(360, 190)

    frame = ttk.Frame(root, padding=16)
    frame.grid(row=0, column=0, sticky="nsew")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    placements = {
        "priority_button": {"row": 0, "column": 0, "sticky": "ew"},
        "count_label": {"row": 1, "column": 0, "sticky": "w", "pady": (14, 4)},
        "trace_label": {"row": 2, "column": 0, "sticky": "ew"},
        "reset_button": {"row": 3, "column": 0, "sticky": "e", "pady": (14, 0)},
    }

    for name, grid_options in placements.items():
        assistant = castle["assistants"][name]
        assistant["assistant_type"]["setup_fn"](assistant, frame)
        assistant["tk"].grid(**grid_options)

    project_castle(castle)


def collect_assistant_events(castle):
    for assistant in castle["assistants"].values():
        while assistant["outbox"]:
            message = assistant["outbox"].pop(0)
            castle["inbox"].append(message)
            castle["trace"].append(f"collected {message['type']} from {message['origin']}")


def process_castle_inbox(castle):
    changed = False

    while castle["inbox"]:
        message = castle["inbox"].pop(0)
        if message["type"] == "button_pressed" and message["origin"] == "priority_button":
            castle["state"]["press_count"] += 1
            count = castle["state"]["press_count"]
            castle["state"]["button_enabled"] = count < 5
            castle["trace"].append(f"handled button_pressed; count is now {count}")
            changed = True
        elif message["type"] == "button_pressed" and message["origin"] == "reset_button":
            castle["state"]["press_count"] = 0
            castle["state"]["button_enabled"] = True
            castle["trace"].append("handled reset button press")
            changed = True

    if changed:
        project_castle(castle)


def project_castle(castle):
    state = castle["state"]
    button = castle["assistants"]["priority_button"]
    count_label = castle["assistants"]["count_label"]
    trace_label = castle["assistants"]["trace_label"]

    button["data"]["enabled"] = state["button_enabled"]

    if state["button_enabled"]:
        remaining = 5 - state["press_count"]
        button["data"]["text"] = f"Required ({remaining} left)"
    else:
        button["data"]["text"] = "Required complete"

    count_label["data"]["text"] = f"Castle state: press_count = {state['press_count']}"

    recent_trace = castle["trace"][-4:]
    if recent_trace:
        trace_label["data"]["text"] = "Trace:\n" + "\n".join(
            f"- {line}" for line in recent_trace
        )
    else:
        trace_label["data"]["text"] = "Trace: waiting for a button event"

    for assistant in castle["assistants"].values():
        assistant["assistant_type"]["project_fn"](assistant)


def runtime_tick(castle):
    collect_assistant_events(castle)
    process_castle_inbox(castle)
    castle["tk_root"].after(50, runtime_tick, castle)


def destroy_castle(castle):
    for assistant in castle["assistants"].values():
        assistant["assistant_type"]["destroy_fn"](assistant)


def main():
    root = tk.Tk()
    castle = make_demo_castle(root)
    setup_castle_surface(castle)

    def on_close():
        destroy_castle(castle)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.after(50, runtime_tick, castle)
    root.mainloop()


if __name__ == "__main__":
    main()
