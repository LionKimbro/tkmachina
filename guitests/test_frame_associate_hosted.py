"""Hosted Tk tests for the Frame associate."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tkintertester import harness

from tkmachina import rt
from tkmachina.associates import (
    FRAME_ASSOCIATE_TYPE,
    LABEL_ASSOCIATE_TYPE,
    WINDOW_ASSOCIATE_TYPE,
)


app = {
    "build": None,
    "castle": None,
    "frame": None,
    "label": None,
}


def frame_template(_build_context=None):
    return {
        "kind": "castle_spec",
        "template_name": "frame_test_castle",
        "associates": [
            {
                "kind": "associate_spec",
                "name": "window",
                "associate_type": WINDOW_ASSOCIATE_TYPE,
                "do_not_listen": ["window_resized"],
                "desired": {
                    "title": "Frame Associate Test",
                    "desired_width": 260,
                    "desired_height": 140,
                    "content_padding": 8,
                },
            },
            {
                "kind": "associate_spec",
                "name": "panel",
                "associate_type": FRAME_ASSOCIATE_TYPE,
                "desired": {
                    "padding": 10,
                },
            },
            {
                "kind": "associate_spec",
                "name": "inside_label",
                "associate_type": LABEL_ASSOCIATE_TYPE,
                "desired": {
                    "text": "inside frame",
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
    rt.submit_build_request(rt.make_build_request(frame_template))
    pump_once()

    build = rt.completed_builds[-1]
    castle = rt.castles[build["castle_ids"][0]]
    app["build"] = build
    app["castle"] = castle
    app["frame"] = rt.get_associate(castle, "panel")
    app["label"] = rt.get_associate(castle, "inside_label")


def reset():
    rt.destroy_all()
    app["build"] = None
    app["castle"] = None
    app["frame"] = None
    app["label"] = None


def test_frame_hosts_child_label():
    def step_verify_relationship():
        frame = app["frame"]
        label = app["label"]
        if not frame["associate_type"]["can_host_children"]:
            return ("fail", "frame type should host children")
        if not frame["associate_type"]["embeddable"]:
            return ("fail", "frame type should be embeddable")
        if frame["child_tk_parent"] is not frame["tk"]:
            return ("fail", "frame child_tk_parent should be the frame widget")
        if label["parent_associate"] != frame["id"]:
            return ("fail", "label parent_associate should be the frame")
        if label["tk"].master is not frame["tk"]:
            return ("fail", "label Tk master should be the frame widget")
        if label["tk"].cget("text") != "inside frame":
            return ("fail", "label projection did not run")
        return ("success", None)

    return [step_verify_relationship]


def test_frame_projects_padding():
    def step_project_padding():
        frame = app["frame"]
        rt.target_associate(frame)
        rt.set_desired("padding", 18)
        rt.project_dirty_associates()
        return ("next", None)

    def step_verify_padding():
        if app["frame"]["private"].get("projected_padding") == 18:
            return ("success", None)
        return (
            "fail",
            f"projected padding was {app['frame']['private'].get('projected_padding')!r}",
        )

    return [step_project_padding, step_verify_padding]


if __name__ == "__main__":
    harness.set_timeout(3000)
    harness.set_resetfn(reset)
    harness.add_test("frame hosts child label", test_frame_hosts_child_label())
    harness.add_test("frame projects padding", test_frame_projects_padding())
    harness.run_host(entry, "x")
    harness.print_results()
    if any(test["status"] != "success" for test in harness.tests):
        raise SystemExit(1)
