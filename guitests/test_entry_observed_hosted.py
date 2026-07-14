"""Hosted Tk tests for Entry observed state independent of event interest."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tkintertester import harness

from tkmachina import rt
from tkmachina.associates import (
    ENTRY_ASSOCIATE_TYPE,
    WINDOW_ASSOCIATE_TYPE,
)


app = {
    "build": None,
    "castle": None,
    "entry": None,
    "muted_entry": None,
}


def quiet_entry_template(_build_context=None):
    return {
        "kind": "castle_spec",
        "template_name": "quiet_entry_castle",
        "associates": [
            {
                "kind": "associate_spec",
                "name": "window",
                "associate_type": WINDOW_ASSOCIATE_TYPE,
                "do_not_listen": ["window_resized"],
                "desired": {
                    "title": "Quiet Entry Observed Test",
                    "desired_width": 220,
                    "desired_height": 90,
                    "content_padding": 8,
                },
            },
            {
                "kind": "associate_spec",
                "name": "entry",
                "associate_type": ENTRY_ASSOCIATE_TYPE,
                "desired": {
                    "text": "",
                    "width": 24,
                },
            },
            {
                "kind": "associate_spec",
                "name": "muted_entry",
                "associate_type": ENTRY_ASSOCIATE_TYPE,
                "do_not_listen": ["submitted"],
                "desired": {
                    "text": "",
                    "width": 24,
                },
            },
        ],
        "spots": {
            "name": "window_spot",
            "children": [
                {
                    "name": "entry_spot",
                    "grid": {"row": 0, "column": 0},
                },
                {
                    "name": "muted_entry_spot",
                    "grid": {"row": 1, "column": 0},
                },
            ],
        },
        "placements": {
            "window_spot": {"kind": "associate", "name": "window"},
            "entry_spot": {"kind": "associate", "name": "entry"},
            "muted_entry_spot": {"kind": "associate", "name": "muted_entry"},
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
    rt.submit_build_request(rt.make_build_request(quiet_entry_template))
    pump_once()

    build = rt.completed_builds[-1]
    castle = rt.castles[build["castle_ids"][0]]
    app["build"] = build
    app["castle"] = castle
    app["entry"] = rt.get_associate(castle, "entry")
    app["muted_entry"] = rt.get_associate(castle, "muted_entry")


def reset():
    rt.destroy_all()
    app["build"] = None
    app["castle"] = None
    app["entry"] = None
    app["muted_entry"] = None


def test_default_entry_emits_submitted_event():
    def step_type_and_focus():
        app["entry"]["tk"].delete(0, "end")
        app["entry"]["tk"].insert(0, "default submit")
        app["entry"]["tk"].focus_set()
        app["entry"]["tk"].focus_force()
        return ("next", None)

    def step_wait_for_focus():
        if app["entry"]["tk"].focus_get() is app["entry"]["tk"]:
            return ("next", None)
        app["entry"]["tk"].focus_force()
        return ("wait", 25)

    def step_submit():
        app["entry"]["tk"].event_generate("<Return>")
        return ("next", 25)

    def step_verify_submitted():
        messages = app["entry"]["outbox"]
        if len(messages) != 1:
            return ("fail", f"expected one submitted message, got {messages!r}")
        message = messages[0]
        if message["type"] != "submitted":
            return ("fail", f"expected submitted, got {message['type']!r}")
        if message["payload"] != {"text": "default submit"}:
            return ("fail", f"unexpected payload: {message['payload']!r}")
        return ("success", None)

    return [step_type_and_focus, step_wait_for_focus, step_submit, step_verify_submitted]


def test_do_not_listen_suppresses_default_submitted_event():
    def step_verify_effective_events():
        if "submitted" in app["muted_entry"]["effective_events"]:
            return (
                "fail",
                f"submitted was not suppressed: {app['muted_entry']['effective_events']!r}",
            )
        return ("next", None)

    def step_type_and_focus():
        app["muted_entry"]["tk"].delete(0, "end")
        app["muted_entry"]["tk"].insert(0, "muted submit")
        app["muted_entry"]["tk"].focus_set()
        app["muted_entry"]["tk"].focus_force()
        return ("next", None)

    def step_wait_for_focus():
        if app["muted_entry"]["tk"].focus_get() is app["muted_entry"]["tk"]:
            return ("next", None)
        app["muted_entry"]["tk"].focus_force()
        return ("wait", 25)

    def step_submit():
        app["muted_entry"]["tk"].event_generate("<Return>")
        return ("next", 25)

    def step_verify_no_message():
        if app["muted_entry"]["outbox"]:
            return ("fail", f"unexpected messages: {app['muted_entry']['outbox']!r}")
        return ("success", None)

    return [
        step_verify_effective_events,
        step_type_and_focus,
        step_wait_for_focus,
        step_submit,
        step_verify_no_message,
    ]


def test_observed_text_updates_without_text_changed_event_interest():
    def step_type_text():
        app["entry"]["tk"].delete(0, "end")
        app["entry"]["tk"].insert(0, "observed only")
        return ("next", None)

    def step_verify_observed_without_message():
        entry_associate = app["entry"]
        if entry_associate["observed"]["text"] != "observed only":
            return (
                "fail",
                f"observed text was {entry_associate['observed']['text']!r}",
            )
        if entry_associate["outbox"]:
            return ("fail", f"unexpected outbox messages: {entry_associate['outbox']!r}")
        return ("success", None)

    return [step_type_text, step_verify_observed_without_message]


def test_observed_focus_updates_without_focus_event_interest():
    def step_focus():
        app["entry"]["tk"].event_generate("<FocusIn>")
        return ("next", None)

    def step_verify_observed_without_message():
        entry_associate = app["entry"]
        if entry_associate["observed"]["focused"] is not True:
            return (
                "fail",
                f"observed focused was {entry_associate['observed']['focused']!r}",
            )
        if entry_associate["outbox"]:
            return ("fail", f"unexpected outbox messages: {entry_associate['outbox']!r}")
        return ("success", None)

    return [step_focus, step_verify_observed_without_message]


if __name__ == "__main__":
    harness.set_timeout(3000)
    harness.set_resetfn(reset)
    harness.add_test(
        "default Entry emits submitted event",
        test_default_entry_emits_submitted_event(),
    )
    harness.add_test(
        "do_not_listen suppresses default submitted event",
        test_do_not_listen_suppresses_default_submitted_event(),
    )
    harness.add_test(
        "entry observed text updates without text_changed interest",
        test_observed_text_updates_without_text_changed_event_interest(),
    )
    harness.add_test(
        "entry observed focus updates without focus interest",
        test_observed_focus_updates_without_focus_event_interest(),
    )
    harness.run_host(entry, "x")
    harness.print_results()
    if any(test["status"] != "success" for test in harness.tests):
        raise SystemExit(1)
