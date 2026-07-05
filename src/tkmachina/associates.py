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


def make_entry_associate_type():
    return {
        "name": "entry",
        "can_host_children": False,
        "embeddable": True,
        "default_events": ["submitted"],
        "setup_fn": setup_entry_associate,
        "project_fn": project_entry_associate,
        "destroy_fn": destroy_entry_associate,
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


def setup_entry_associate(associate, tk_parent):
    desired = associate["desired"]
    observed = associate["observed"]
    private = associate["private"]

    text_var = tk.StringVar(value=desired.get("text", ""))
    observed["text"] = text_var.get()
    observed.setdefault("focused", False)
    private["text_var"] = text_var
    private["projected_text"] = text_var.get()
    private["suppress_text_changed"] = False

    widget = ttk.Entry(tk_parent, textvariable=text_var)

    def emit(event_type, payload):
        associate["outbox"].append(
            {
                "kind": "event",
                "type": event_type,
                "origin": associate["name"],
                "emitter": associate["name"],
                "payload": payload,
            }
        )

    def on_text_changed(*_args):
        text = text_var.get()
        if observed.get("text") == text:
            return

        observed["text"] = text
        if private.get("suppress_text_changed"):
            return

        if "text_changed" in associate["effective_events"]:
            emit("text_changed", {"text": text})

    def on_submitted(_event):
        text = text_var.get()
        observed["text"] = text
        emit("submitted", {"text": text})
        return "break"

    def on_focus_changed(focused):
        if observed.get("focused") == focused:
            return

        observed["focused"] = focused
        emit("focus_changed", {"focused": focused})

    if "text_changed" in associate["effective_events"]:
        private["text_trace"] = text_var.trace_add("write", on_text_changed)
    if "submitted" in associate["effective_events"]:
        widget.bind("<Return>", on_submitted)
    if "focus_changed" in associate["effective_events"]:
        widget.bind("<FocusIn>", lambda _event: on_focus_changed(True))
        widget.bind("<FocusOut>", lambda _event: on_focus_changed(False))

    associate["tk"] = widget


def project_entry_associate(associate):
    desired = associate["desired"]
    private = associate["private"]
    widget = associate["tk"]
    text_var = private["text_var"]

    if "text" in desired and private.get("projected_text") != desired["text"]:
        private["suppress_text_changed"] = True
        text_var.set(desired["text"])
        private["suppress_text_changed"] = False
        associate["observed"]["text"] = desired["text"]
        private["projected_text"] = desired["text"]

    desired_state = "normal" if desired.get("enabled", True) else "disabled"
    if widget.cget("state") != desired_state:
        widget.config(state=desired_state)

    desired_width = desired.get("width")
    if desired_width is not None and widget.cget("width") != desired_width:
        widget.config(width=desired_width)


def destroy_widget_associate(associate):
    widget = associate.get("tk")
    if widget is not None:
        widget.destroy()
        associate["tk"] = None


def destroy_entry_associate(associate):
    private = associate["private"]
    text_var = private.get("text_var")
    text_trace = private.get("text_trace")
    if text_var is not None and text_trace is not None:
        try:
            text_var.trace_remove("write", text_trace)
        except tk.TclError:
            pass

    destroy_widget_associate(associate)
    private.pop("text_var", None)
    private.pop("text_trace", None)


def destroy_window_associate(associate):
    widget = associate.get("tk")
    if widget is not None:
        widget.destroy()
        associate["tk"] = None
        associate["child_tk_parent"] = None


WINDOW_ASSOCIATE_TYPE = make_window_associate_type()
BUTTON_ASSOCIATE_TYPE = make_button_associate_type()
LABEL_ASSOCIATE_TYPE = make_label_associate_type()
ENTRY_ASSOCIATE_TYPE = make_entry_associate_type()
