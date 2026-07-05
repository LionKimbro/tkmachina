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
        "default_events": ["window_resized"],
        "setup_fn": setup_window_associate,
        "project_fn": project_window_associate,
        "destroy_fn": destroy_window_associate,
    }


def make_button_associate_type():
    return {
        "name": "button",
        "can_host_children": False,
        "embeddable": True,
        "default_events": ["button_pressed"],
        "setup_fn": setup_button_associate,
        "project_fn": project_button_associate,
        "destroy_fn": destroy_widget_associate,
    }


def make_label_associate_type():
    return {
        "name": "label",
        "can_host_children": False,
        "embeddable": True,
        "default_events": [],
        "setup_fn": setup_label_associate,
        "project_fn": project_label_associate,
        "destroy_fn": destroy_widget_associate,
    }


def setup_window_associate(associate, tk_master):
    desired = associate["desired"]
    observed = associate["observed"]
    window = tk.Toplevel(tk_master)
    content_frame = ttk.Frame(window, padding=desired.get("content_padding", 0))
    content_frame.grid(row=0, column=0, sticky="nsew")
    window.columnconfigure(0, weight=1)
    window.rowconfigure(0, weight=1)

    def on_configure(event):
        if event.widget is not window:
            return

        old_size = (observed.get("actual_width"), observed.get("actual_height"))
        new_size = (event.width, event.height)
        if old_size == new_size:
            return

        observed["actual_width"] = event.width
        observed["actual_height"] = event.height
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

    if "window_resized" in associate["effective_events"]:
        window.bind("<Configure>", on_configure)
    window.protocol("WM_DELETE_WINDOW", on_close)
    associate["tk"] = window
    associate["child_tk_parent"] = content_frame


def project_window_associate(associate):
    desired = associate["desired"]
    private = associate["private"]
    window = associate["tk"]

    if desired.get("title") and window.title() != desired["title"]:
        window.title(desired["title"])

    min_width = desired.get("min_width")
    min_height = desired.get("min_height")
    if min_width is not None and min_height is not None:
        window.minsize(min_width, min_height)

    desired_width = desired.get("desired_width")
    desired_height = desired.get("desired_height")
    desired_size = (desired_width, desired_height)
    if (
        desired_width is not None
        and desired_height is not None
        and private.get("projected_size") != desired_size
    ):
        window.geometry(f"{desired_width}x{desired_height}")
        private["projected_size"] = desired_size


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

    command = on_click if "button_pressed" in associate["effective_events"] else None
    associate["tk"] = ttk.Button(tk_parent, command=command)


def project_button_associate(associate):
    desired = associate["desired"]
    widget = associate["tk"]

    if widget.cget("text") != desired["text"]:
        widget.config(text=desired["text"])

    desired_state = "normal" if desired.get("enabled", True) else "disabled"
    if widget.cget("state") != desired_state:
        widget.config(state=desired_state)


def setup_label_associate(associate, tk_parent):
    associate["tk"] = ttk.Label(tk_parent, justify="left")


def project_label_associate(associate):
    desired = associate["desired"]
    widget = associate["tk"]

    if widget.cget("text") != desired["text"]:
        widget.config(text=desired["text"])

    desired_wraplength = desired.get("wraplength")
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
