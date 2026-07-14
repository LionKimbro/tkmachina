"""Hosted Tk tests for the LabelFrame associate."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tkintertester import harness

from tkmachina import rt
from tkmachina.associates import (
    LABEL_ASSOCIATE_TYPE,
    LABEL_FRAME_ASSOCIATE_TYPE,
    WINDOW_ASSOCIATE_TYPE,
)


app = {
    "build": None,
    "castle": None,
    "label_frame": None,
    "label": None,
}


def label_frame_template(_build_context=None):
    return {
        "kind": "castle_spec",
        "template_name": "label_frame_test_castle",
        "associates": [
            {
                "kind": "associate_spec",
                "name": "window",
                "associate_type": WINDOW_ASSOCIATE_TYPE,
                "do_not_listen": ["window_resized"],
                "desired": {
                    "title": "LabelFrame Associate Test",
                    "desired_width": 300,
                    "desired_height": 160,
                    "content_padding": 8,
                },
            },
            {
                "kind": "associate_spec",
                "name": "panel",
                "associate_type": LABEL_FRAME_ASSOCIATE_TYPE,
                "desired": {
                    "text": "Outer Controls",
                    "padding": 10,
                },
            },
            {
                "kind": "associate_spec",
                "name": "inside_label",
                "associate_type": LABEL_ASSOCIATE_TYPE,
                "desired": {
                    "text": "inside labeled frame",
                },
            },
        ],
        "spots": {
            "name": "window_spot",
            "children": [
                {
                    "name": "panel_spot",
                    "grid": {"row": 0, "column": 0},
                    "children": [
                        {
                            "name": "label_spot",
                            "grid": {"row": 0, "column": 0},
                        },
                    ],
                },
            ],
        },
        "placements": {
            "window_spot": {"kind": "associate", "name": "window"},
            "panel_spot": {"kind": "associate", "name": "panel"},
            "label_spot": {"kind": "associate", "name": "inside_label"},
        },
    }


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
    rt.submit_build_request(rt.make_build_request(label_frame_template))
    pump_once()

    build = rt.completed_builds[-1]
    castle = rt.castles[build["castle_ids"][0]]
    app["build"] = build
    app["castle"] = castle
    app["label_frame"] = rt.get_associate(castle, "panel")
    app["label"] = rt.get_associate(castle, "inside_label")


def reset():
    rt.destroy_all()
    app["build"] = None
    app["castle"] = None
    app["label_frame"] = None
    app["label"] = None


def test_label_frame_hosts_child_label():
    def step_verify_relationship():
        label_frame = app["label_frame"]
        label = app["label"]
        if not label_frame["associate_type"]["can_host_children"]:
            return ("fail", "label_frame type should host children")
        if not label_frame["associate_type"]["embeddable"]:
            return ("fail", "label_frame type should be embeddable")
        if label_frame["child_tk_parent"] is not label_frame["tk"]:
            return (
                "fail",
                "label_frame child_tk_parent should be the label frame widget",
            )
        if label["parent_associate"] != label_frame["id"]:
            return ("fail", "label parent_associate should be the label_frame")
        if label["tk"].master is not label_frame["tk"]:
            return ("fail", "label Tk master should be the label_frame widget")
        if label["tk"].cget("text") != "inside labeled frame":
            return ("fail", "inner label projection did not run")
        return ("success", None)

    return [step_verify_relationship]


def test_label_frame_text_is_desired_and_observed():
    def step_verify_initial_text():
        label_frame = app["label_frame"]
        if label_frame["tk"].cget("text") != "Outer Controls":
            return ("fail", "initial desired text was not projected")
        if label_frame["observed"]["text"] != "Outer Controls":
            return ("fail", "initial observed text was not maintained")
        return ("next", None)

    def step_project_new_text():
        label_frame = app["label_frame"]
        rt.target_associate(label_frame)
        rt.set_desired("text", "Renamed Controls")
        rt.project_dirty_associates()
        return ("next", None)

    def step_verify_projected_text():
        label_frame = app["label_frame"]
        if label_frame["tk"].cget("text") != "Renamed Controls":
            return ("fail", "updated desired text was not projected")
        if label_frame["observed"]["text"] != "Renamed Controls":
            return (
                "fail",
                f"observed text was {label_frame['observed']['text']!r}",
            )
        return ("success", None)

    return [step_verify_initial_text, step_project_new_text, step_verify_projected_text]


def test_label_frame_projects_padding():
    def step_project_padding():
        label_frame = app["label_frame"]
        rt.target_associate(label_frame)
        rt.set_desired("padding", 18)
        rt.project_dirty_associates()
        return ("next", None)

    def step_verify_padding():
        if app["label_frame"]["private"].get("projected_padding") == 18:
            return ("success", None)
        return (
            "fail",
            "projected padding was "
            f"{app['label_frame']['private'].get('projected_padding')!r}",
        )

    return [step_project_padding, step_verify_padding]


if __name__ == "__main__":
    harness.set_timeout(3000)
    harness.set_resetfn(reset)
    harness.add_test(
        "label_frame hosts child label",
        test_label_frame_hosts_child_label(),
    )
    harness.add_test(
        "label_frame text is desired and observed",
        test_label_frame_text_is_desired_and_observed(),
    )
    harness.add_test(
        "label_frame projects padding",
        test_label_frame_projects_padding(),
    )
    harness.run_host(entry, "x")
    harness.print_results()
    if any(test["status"] != "success" for test in harness.tests):
        raise SystemExit(1)
