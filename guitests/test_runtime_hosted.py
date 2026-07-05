"""Hosted Tk runtime test using tkintertester."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tkintertester import harness

from tkmachina import rt
from tkmachina.associates import (
    BUTTON_ASSOCIATE_TYPE,
    LABEL_ASSOCIATE_TYPE,
    WINDOW_ASSOCIATE_TYPE,
)


app = {
    "build": None,
    "castle": None,
}


def hosted_template(build_context=None):
    return {
        "kind": "castle_spec",
        "template_name": "hosted_test_castle",
        "state": {"count": 0},
        "handle_fn": handle_hosted_message,
        "reconcile_fn": reconcile_hosted_castle,
        "associates": [
            {
                "kind": "associate_spec",
                "name": "window",
                "associate_type": WINDOW_ASSOCIATE_TYPE,
                "do_not_listen": ["window_resized"],
                "desired": {
                    "title": "TkMachina Hosted Test",
                    "desired_width": 240,
                    "desired_height": 120,
                    "content_padding": 8,
                },
            },
            {
                "kind": "associate_spec",
                "name": "button",
                "associate_type": BUTTON_ASSOCIATE_TYPE,
                "desired": {
                    "text": "Increment",
                    "enabled": True,
                },
            },
            {
                "kind": "associate_spec",
                "name": "label",
                "associate_type": LABEL_ASSOCIATE_TYPE,
                "desired": {
                    "text": "Count: 0",
                },
            },
        ],
        "spots": {
            "name": "window_spot",
            "children": [
                {
                    "name": "button_spot",
                    "grid": {"row": 0, "column": 0},
                },
                {
                    "name": "label_spot",
                    "grid": {"row": 1, "column": 0},
                },
            ],
        },
        "placements": {
            "window_spot": {"kind": "associate", "name": "window"},
            "button_spot": {"kind": "associate", "name": "button"},
            "label_spot": {"kind": "associate", "name": "label"},
        },
    }


def handle_hosted_message(castle, message):
    if message["type"] == "button_pressed" and message["origin"] == "button":
        castle["state"]["count"] += 1
        return rt.HANDLED_DIRTY
    return rt.IGNORED


def reconcile_hosted_castle(castle):
    label = rt.get_associate(castle, "label")
    rt.target_associate(label)
    rt.set_desired("text", f"Count: {castle['state']['count']}")


def pump_once():
    rt.process_incoming_builds()
    rt.deliver_messages()
    rt.process_castle_messages()
    rt.reconcile_dirty_castles()
    rt.process_structural_requests()
    rt.project_dirty_associates()


def entry():
    rt.reset()
    rt.tk_master = harness.g["root"]
    rt.setup_global_castles()
    request = rt.make_build_request(hosted_template)
    rt.submit_build_request(request)
    pump_once()
    app["build"] = rt.completed_builds[-1]
    app["castle"] = rt.castles[app["build"]["castle_ids"][0]]


def reset():
    rt.destroy_all()
    app["build"] = None
    app["castle"] = None


def test_button_event_updates_label():
    def step_click_button():
        button = rt.get_associate(app["castle"], "button")
        button["tk"].invoke()
        return ("next", None)

    def step_pump_runtime():
        pump_once()
        return ("next", None)

    def step_verify_label():
        label = rt.get_associate(app["castle"], "label")
        actual = label["tk"].cget("text")
        if actual == "Count: 1":
            return ("success", None)
        return ("fail", f"expected label to show Count: 1, got {actual!r}")

    return [step_click_button, step_pump_runtime, step_verify_label]


if __name__ == "__main__":
    harness.set_timeout(3000)
    harness.set_resetfn(reset)
    harness.add_test("button event updates label", test_button_event_updates_label())
    harness.run_host(entry, "x")
    harness.print_results()
    if any(test["status"] != "success" for test in harness.tests):
        raise SystemExit(1)
