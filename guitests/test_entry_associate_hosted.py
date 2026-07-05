"""Hosted Tk tests for the Entry associate and child-castle bubble route."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from tkintertester import harness

from examples.entry_inner_castle_demo import outer_template
from tkmachina import rt


app = {
    "build": None,
    "outer": None,
    "inner": None,
    "entry": None,
}


def pump_once():
    rt.process_incoming_builds()
    rt.deliver_messages()
    rt.process_castle_messages()
    rt.reconcile_dirty_castles()
    rt.process_structural_requests()
    rt.project_dirty_associates()


def pump_bubble_route():
    pump_once()
    pump_once()


def entry():
    rt.reset()
    rt.tk_master = harness.g["root"]
    rt.setup_global_castles()
    rt.submit_build_request(rt.make_build_request(outer_template))
    pump_once()

    build = rt.completed_builds[-1]
    outer = next(
        rt.castles[castle_id]
        for castle_id in build["castle_ids"]
        if rt.castles[castle_id]["template_name"] == "entry_outer_castle"
    )
    inner = next(
        rt.castles[castle_id]
        for castle_id in build["castle_ids"]
        if rt.castles[castle_id]["template_name"] == "entry_panel_castle"
    )

    app["build"] = build
    app["outer"] = outer
    app["inner"] = inner
    app["entry"] = rt.get_associate(inner, "entry")


def reset():
    rt.destroy_all()
    app["build"] = None
    app["outer"] = None
    app["inner"] = None
    app["entry"] = None


def get_label_text(name):
    return rt.get_associate(app["outer"], name)["tk"].cget("text")


def set_entry_text(text):
    widget = app["entry"]["tk"]
    widget.delete(0, "end")
    widget.insert(0, text)


def test_text_changed_bubbles_to_outer_castle():
    def step_type():
        set_entry_text("lion")
        return ("next", None)

    def step_pump():
        pump_bubble_route()
        return ("next", None)

    def step_verify():
        if get_label_text("text_label") == "Text changed: lion":
            return ("success", None)
        return ("fail", get_label_text("text_label"))

    return [step_type, step_pump, step_verify]


def test_submitted_bubbles_to_outer_castle():
    def step_type_and_focus():
        set_entry_text("submitted text")
        app["entry"]["tk"].focus_force()
        return ("next", 25)

    def step_submit():
        app["entry"]["tk"].event_generate("<Return>")
        return ("next", 25)

    def step_pump():
        pump_bubble_route()
        return ("next", None)

    def step_verify():
        if get_label_text("submit_label") == "Submitted: submitted text":
            return ("success", None)
        return ("fail", get_label_text("submit_label"))

    return [step_type_and_focus, step_submit, step_pump, step_verify]


def test_focused_bubbles_to_outer_castle():
    def step_focus():
        app["entry"]["tk"].event_generate("<FocusIn>")
        return ("next", None)

    def step_pump():
        pump_bubble_route()
        return ("next", None)

    def step_verify():
        if get_label_text("focus_label") == "Focus: yes":
            return ("success", None)
        return ("fail", get_label_text("focus_label"))

    return [step_focus, step_pump, step_verify]


def test_entry_effective_events_include_opt_ins():
    def step_verify_effective_events():
        if app["entry"]["effective_events"] == {
            "submitted",
            "text_changed",
            "focused",
            "unfocused",
        }:
            return ("success", None)
        return ("fail", f"unexpected events: {app['entry']['effective_events']!r}")

    return [step_verify_effective_events]


def test_projection_does_not_emit_text_changed():
    def step_project_desired_text():
        entry_associate = app["entry"]
        entry_associate["outbox"].clear()
        rt.target_associate(entry_associate)
        rt.set_desired("text", "projected text")
        rt.project_dirty_associates()
        return ("next", None)

    def step_verify_no_text_changed():
        entry_associate = app["entry"]
        if entry_associate["observed"]["text"] != "projected text":
            return (
                "fail",
                f"observed text was {entry_associate['observed']['text']!r}",
            )
        if entry_associate["outbox"]:
            return ("fail", f"projection emitted messages: {entry_associate['outbox']!r}")
        return ("success", None)

    return [step_project_desired_text, step_verify_no_text_changed]


if __name__ == "__main__":
    harness.set_timeout(3000)
    harness.set_resetfn(reset)
    harness.add_test("entry text_changed bubbles to outer castle", test_text_changed_bubbles_to_outer_castle())
    harness.add_test("entry submitted bubbles to outer castle", test_submitted_bubbles_to_outer_castle())
    harness.add_test("entry focused bubbles to outer castle", test_focused_bubbles_to_outer_castle())
    harness.add_test("entry effective events include opt-ins", test_entry_effective_events_include_opt_ins())
    harness.add_test("entry projection does not emit text_changed", test_projection_does_not_emit_text_changed())
    harness.run_host(entry, "x")
    harness.print_results()
    if any(test["status"] != "success" for test in harness.tests):
        raise SystemExit(1)
