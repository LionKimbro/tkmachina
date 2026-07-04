"""
Associate type definitions for TkMachina.

Associates are the Little-Castle-side companions to Tk widgets. They own
desired widget-facing data, translate raw Tk activity into semantic outbox
messages, and project desired data onto concrete widgets.
"""

import tkinter as tk
from tkinter import ttk


def make_window_associate_type():
    return {
        "name": "window",
        "can_host_children": True,
        "embeddable": False,
        "setup_fn": setup_window_associate,
        "project_fn": project_window_associate,
        "destroy_fn": destroy_window_associate,
    }


def make_button_associate_type():
    return {
        "name": "button",
        "can_host_children": False,
        "embeddable": True,
        "setup_fn": setup_button_associate,
        "project_fn": project_button_associate,
        "destroy_fn": destroy_widget_associate,
    }


def make_label_associate_type():
    return {
        "name": "label",
        "can_host_children": False,
        "embeddable": True,
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
        from tkmachina import rt

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
