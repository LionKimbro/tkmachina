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


def make_frame_associate_type():
    return {
        "name": "frame",
        "can_host_children": True,
        "embeddable": True,
        "default_events": [],
        "setup_fn": setup_frame_associate,
        "project_fn": project_frame_associate,
        "destroy_fn": destroy_frame_associate,
    }


def make_label_frame_associate_type():
    return {
        "name": "label_frame",
        "can_host_children": True,
        "embeddable": True,
        "default_events": [],
        "setup_fn": setup_label_frame_associate,
        "project_fn": project_label_frame_associate,
        "destroy_fn": destroy_label_frame_associate,
    }


def wants_event(associate, event_type):
    return event_type in associate.get("effective_events", set())


def emit_event(associate, event_type, payload=None):
    associate["outbox"].append(
        {
            "kind": "event",
            "type": event_type,
            "origin": associate["name"],
            "emitter": associate["name"],
            "payload": payload or {},
        }
    )


def bind_common_widget_events(associate):
    bind_focus_events(associate)
    bind_pointer_enter_leave_events(associate)
    bind_mouse_click_events(associate)
    bind_key_events(associate)
    bind_configure_event(associate)


def bind_focus_events(associate):
    widget = associate["tk"]
    should_observe_focus = (
        "focused" in associate["observed"]
        or wants_event(associate, "focused")
        or wants_event(associate, "unfocused")
    )

    if should_observe_focus:
        widget.bind(
            "<FocusIn>",
            lambda _event: handle_common_focus_event(associate, True),
            add="+",
        )
        widget.bind(
            "<FocusOut>",
            lambda _event: handle_common_focus_event(associate, False),
            add="+",
        )


def handle_common_focus_event(associate, focused):
    if associate["observed"].get("focused") == focused:
        return

    associate["observed"]["focused"] = focused
    event_type = "focused" if focused else "unfocused"
    if wants_event(associate, event_type):
        emit_event(associate, event_type)


def bind_pointer_enter_leave_events(associate):
    widget = associate["tk"]

    if wants_event(associate, "pointer_entered"):
        widget.bind(
            "<Enter>",
            lambda event: emit_event(associate, "pointer_entered", pointer_payload(event)),
            add="+",
        )

    if wants_event(associate, "pointer_left"):
        widget.bind(
            "<Leave>",
            lambda event: emit_event(associate, "pointer_left", pointer_payload(event)),
            add="+",
        )


def bind_mouse_click_events(associate):
    widget = associate["tk"]

    if wants_event(associate, "clicked"):
        widget.bind(
            "<Button-1>",
            lambda event: emit_event(associate, "clicked", pointer_payload(event)),
            add="+",
        )

    if wants_event(associate, "double_clicked"):
        widget.bind(
            "<Double-Button-1>",
            lambda event: emit_event(associate, "double_clicked", pointer_payload(event)),
            add="+",
        )

    if wants_event(associate, "middle_clicked"):
        widget.bind(
            "<Button-2>",
            lambda event: emit_event(associate, "middle_clicked", pointer_payload(event)),
            add="+",
        )

    if wants_event(associate, "right_clicked"):
        widget.bind(
            "<Button-3>",
            lambda event: emit_event(associate, "right_clicked", pointer_payload(event)),
            add="+",
        )


def bind_key_events(associate):
    widget = associate["tk"]

    if wants_event(associate, "key_pressed"):
        widget.bind(
            "<KeyPress>",
            lambda event: emit_event(associate, "key_pressed", key_payload(event)),
            add="+",
        )

    if wants_event(associate, "key_released"):
        widget.bind(
            "<KeyRelease>",
            lambda event: emit_event(associate, "key_released", key_payload(event)),
            add="+",
        )


def bind_configure_event(associate):
    if not wants_event(associate, "configured"):
        return

    associate["tk"].bind(
        "<Configure>",
        lambda event: emit_event(associate, "configured", configure_payload(event)),
        add="+",
    )


def pointer_payload(event):
    return {
        "x": event.x,
        "y": event.y,
        "x_root": event.x_root,
        "y_root": event.y_root,
    }


def key_payload(event):
    return {
        "keysym": event.keysym,
        "char": event.char,
        "keycode": event.keycode,
        "state": event.state,
    }


def configure_payload(event):
    return {
        "width": event.width,
        "height": event.height,
        "x": event.x,
        "y": event.y,
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
        emit_event(
            associate,
            "window_resized",
            {
                "width": event.width,
                "height": event.height,
            },
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
    bind_common_widget_events(associate)


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


def setup_frame_associate(associate, tk_parent):
    desired = associate["desired"]
    frame = ttk.Frame(tk_parent, padding=desired.get("padding", 0))
    setup_container_associate(associate, frame)


def project_frame_associate(associate):
    project_container_associate_fields(associate)


def setup_label_frame_associate(associate, tk_parent):
    desired = associate["desired"]
    observed = associate["observed"]
    text = desired.get("text", observed.get("text", ""))
    label_frame = ttk.LabelFrame(
        tk_parent,
        text=text,
        padding=desired.get("padding", 0),
    )
    observed["text"] = text
    associate["private"]["projected_text"] = text
    setup_container_associate(associate, label_frame)


def project_label_frame_associate(associate):
    desired = associate["desired"]
    private = associate["private"]
    widget = associate["tk"]

    project_container_associate_fields(associate)

    if "text" in desired and widget.cget("text") != desired["text"]:
        widget.config(text=desired["text"])
        private["projected_text"] = desired["text"]

    associate["observed"]["text"] = widget.cget("text")


def setup_container_associate(associate, widget):
    associate["tk"] = widget
    associate["child_tk_parent"] = widget
    associate["private"]["projected_padding"] = associate["desired"].get("padding", 0)
    bind_common_widget_events(associate)


def project_container_associate_fields(associate):
    desired = associate["desired"]
    private = associate["private"]
    widget = associate["tk"]

    desired_padding = desired.get("padding")
    if (
        desired_padding is not None
        and private.get("projected_padding") != desired_padding
    ):
        widget.config(padding=desired_padding)
        private["projected_padding"] = desired_padding

    desired_width = desired.get("width")
    if desired_width is not None and widget.cget("width") != desired_width:
        widget.config(width=desired_width)

    desired_height = desired.get("height")
    if desired_height is not None and widget.cget("height") != desired_height:
        widget.config(height=desired_height)


def setup_button_associate(associate, tk_parent):
    def on_click():
        emit_event(associate, "button_pressed")

    command = on_click if "button_pressed" in associate["effective_events"] else None
    associate["tk"] = ttk.Button(tk_parent, command=command)
    bind_common_widget_events(associate)


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
    bind_common_widget_events(associate)


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

    def on_text_changed(*_args):
        text = text_var.get()
        if observed.get("text") == text:
            return

        observed["text"] = text
        if private.get("suppress_text_changed"):
            return

        if wants_event(associate, "text_changed"):
            emit_event(associate, "text_changed", {"text": text})

    def on_submitted(_event):
        text = text_var.get()
        observed["text"] = text
        emit_event(associate, "submitted", {"text": text})
        return "break"

    private["text_trace"] = text_var.trace_add("write", on_text_changed)
    if wants_event(associate, "submitted"):
        widget.bind("<Return>", on_submitted, add="+")

    associate["tk"] = widget
    bind_common_widget_events(associate)


def project_entry_associate(associate):
    desired = associate["desired"]
    private = associate["private"]
    widget = associate["tk"]
    text_var = private["text_var"]

    if "text" in desired and private.get("projected_text") != desired["text"]:
        private["suppress_text_changed"] = True
        try:
            text_var.set(desired["text"])
        finally:
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


def destroy_frame_associate(associate):
    destroy_container_associate(associate)


def destroy_label_frame_associate(associate):
    destroy_container_associate(associate)
    associate["private"].pop("projected_text", None)


def destroy_container_associate(associate):
    destroy_widget_associate(associate)
    associate["child_tk_parent"] = None
    associate["private"].pop("projected_padding", None)


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
    private.pop("projected_text", None)
    private.pop("suppress_text_changed", None)


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
FRAME_ASSOCIATE_TYPE = make_frame_associate_type()
LABEL_FRAME_ASSOCIATE_TYPE = make_label_frame_associate_type()
