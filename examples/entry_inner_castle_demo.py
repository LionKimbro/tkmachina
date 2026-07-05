"""
Entry associate demo with an inner castle and automatic bubble-up routing.

Run from the repository root:

    python examples/entry_inner_castle_demo.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tkmachina import rt
from tkmachina.associates import (
    ENTRY_ASSOCIATE_TYPE,
    LABEL_ASSOCIATE_TYPE,
    WINDOW_ASSOCIATE_TYPE,
)


def outer_template(_build_context=None):
    return {
        "kind": "castle_spec",
        "template_name": "entry_outer_castle",
        "state": {
            "latest_event": "waiting",
            "latest_text": "",
            "submitted_text": "",
            "focused": "unknown",
        },
        "handle_fn": handle_outer_message,
        "reconcile_fn": reconcile_outer_castle,
        "child_castles": [
            {
                "kind": "child_castle_spec",
                "name": "entry_panel",
                "template_fn": entry_panel_template,
            },
        ],
        "associates": [
            {
                "kind": "associate_spec",
                "name": "window",
                "associate_type": WINDOW_ASSOCIATE_TYPE,
                "do_not_listen": ["window_resized"],
                "desired": {
                    "title": "TkMachina Entry Castle Demo",
                    "desired_width": 480,
                    "desired_height": 220,
                    "min_width": 420,
                    "min_height": 200,
                    "content_padding": 16,
                },
            },
            {
                "kind": "associate_spec",
                "name": "heading_label",
                "associate_type": LABEL_ASSOCIATE_TYPE,
                "desired": {
                    "text": "Inner castle owns the Entry. Outer castle reports bubbled events.",
                    "wraplength": 430,
                },
            },
            {
                "kind": "associate_spec",
                "name": "structure_label",
                "associate_type": LABEL_ASSOCIATE_TYPE,
                "desired": {
                    "text": (
                        "Structure: the outer castle owns this window and the "
                        "report labels. It places an inner castle into one "
                        "spot; that inner castle owns the Entry, handles Entry "
                        "events, and sends summary events upward through the "
                        "automatic child-to-parent route."
                    ),
                    "wraplength": 430,
                },
            },
            {
                "kind": "associate_spec",
                "name": "event_label",
                "associate_type": LABEL_ASSOCIATE_TYPE,
                "desired": {"text": "Latest event: waiting"},
            },
            {
                "kind": "associate_spec",
                "name": "text_label",
                "associate_type": LABEL_ASSOCIATE_TYPE,
                "desired": {"text": "Text changed: "},
            },
            {
                "kind": "associate_spec",
                "name": "submit_label",
                "associate_type": LABEL_ASSOCIATE_TYPE,
                "desired": {"text": "Submitted: "},
            },
            {
                "kind": "associate_spec",
                "name": "focus_label",
                "associate_type": LABEL_ASSOCIATE_TYPE,
                "desired": {"text": "Focus: unknown"},
            },
        ],
        "spots": {
            "name": "window_spot",
            "layout": {"columnconfigure": {0: {"weight": 1}}},
            "children": [
                {
                    "name": "heading_spot",
                    "grid": {"row": 0, "column": 0, "sticky": "ew"},
                },
                {
                    "name": "entry_panel_spot",
                    "grid": {"row": 1, "column": 0, "sticky": "ew", "pady": (12, 12)},
                },
                {
                    "name": "structure_spot",
                    "grid": {"row": 2, "column": 0, "sticky": "w"},
                },
                {
                    "name": "event_spot",
                    "grid": {"row": 3, "column": 0, "sticky": "w"},
                },
                {
                    "name": "text_spot",
                    "grid": {"row": 4, "column": 0, "sticky": "w"},
                },
                {
                    "name": "submit_spot",
                    "grid": {"row": 5, "column": 0, "sticky": "w"},
                },
                {
                    "name": "focus_spot",
                    "grid": {"row": 6, "column": 0, "sticky": "w"},
                },
            ],
        },
        "placements": {
            "window_spot": {"kind": "associate", "name": "window"},
            "heading_spot": {"kind": "associate", "name": "heading_label"},
            "entry_panel_spot": {"kind": "child_castle", "name": "entry_panel"},
            "structure_spot": {"kind": "associate", "name": "structure_label"},
            "event_spot": {"kind": "associate", "name": "event_label"},
            "text_spot": {"kind": "associate", "name": "text_label"},
            "submit_spot": {"kind": "associate", "name": "submit_label"},
            "focus_spot": {"kind": "associate", "name": "focus_label"},
        },
    }


def entry_panel_template(_build_context=None):
    return {
        "kind": "castle_spec",
        "template_name": "entry_panel_castle",
        "state": {
            "text": "",
            "submitted": "",
            "focused": False,
        },
        "handle_fn": handle_entry_panel_message,
        "associates": [
            {
                "kind": "associate_spec",
                "name": "entry",
                "associate_type": ENTRY_ASSOCIATE_TYPE,
                "events": ["text_changed", "focused", "unfocused"],
                "desired": {
                    "text": "",
                    "width": 42,
                },
            },
        ],
    }


def handle_entry_panel_message(castle, message):
    if message["type"] not in ("submitted", "text_changed", "focused", "unfocused"):
        return rt.IGNORED

    payload = dict(message["payload"])
    if message["type"] in ("submitted", "text_changed"):
        castle["state"]["text"] = payload["text"]
    if message["type"] == "submitted":
        castle["state"]["submitted"] = payload["text"]
    if message["type"] in ("focused", "unfocused"):
        payload["focused"] = message["type"] == "focused"
        castle["state"]["focused"] = payload["focused"]

    castle["outbox"].append(
        {
            "kind": "event",
            "type": "entry_panel_event",
            "origin": castle["child_name"],
            "emitter": castle["template_name"],
            "payload": {
                "entry_event": message["type"],
                **payload,
            },
        }
    )
    return rt.HANDLED


def handle_outer_message(castle, message):
    if message["type"] != "entry_panel_event":
        return rt.IGNORED

    payload = message["payload"]
    castle["state"]["latest_event"] = payload["entry_event"]
    if "text" in payload:
        castle["state"]["latest_text"] = payload["text"]
    if payload["entry_event"] == "submitted":
        castle["state"]["submitted_text"] = payload["text"]
    if payload["entry_event"] in ("focused", "unfocused"):
        castle["state"]["focused"] = "yes" if payload["focused"] else "no"
    return rt.HANDLED_DIRTY


def reconcile_outer_castle(castle):
    state = castle["state"]

    rt.target_associate(rt.get_associate(castle, "event_label"))
    rt.set_desired("text", f"Latest event: {state['latest_event']}")

    rt.target_associate(rt.get_associate(castle, "text_label"))
    rt.set_desired("text", f"Text changed: {state['latest_text']}")

    rt.target_associate(rt.get_associate(castle, "submit_label"))
    rt.set_desired("text", f"Submitted: {state['submitted_text']}")

    rt.target_associate(rt.get_associate(castle, "focus_label"))
    rt.set_desired("text", f"Focus: {state['focused']}")


def main():
    rt.reset()
    rt.setup_tk_bootstrap()
    rt.submit_build_request(rt.make_build_request(outer_template))
    rt.run()


if __name__ == "__main__":
    main()
