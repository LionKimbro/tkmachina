"""Runtime invariant tests for TkMachina.

These tests intentionally avoid real Tk widgets. They use fake associate types
so the runtime's construction, routing, dirty projection, cleanup, and
structural mutation behavior can be checked directly.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tkmachina import rt


class FakeWidget:
    def __init__(self, name):
        self.name = name
        self.destroyed = False
        self.grid_options = None

    def grid(self, **options):
        self.grid_options = dict(options)

    def destroy(self):
        self.destroyed = True


def setup_fake_associate(associate, parent):
    if associate["desired"].get("fail_setup"):
        raise RuntimeError("deliberate setup failure")

    associate["tk"] = FakeWidget(associate["name"])


def setup_fake_container_associate(associate, parent):
    setup_fake_associate(associate, parent)
    associate["child_tk_parent"] = FakeWidget(f"{associate['name']}.children")


def project_fake_associate(associate):
    associate["private"]["project_count"] = associate["private"].get("project_count", 0) + 1


def destroy_fake_associate(associate):
    widget = associate.get("tk")
    if widget is not None:
        widget.destroy()
        associate["tk"] = None
    associate["child_tk_parent"] = None


FAKE_ASSOCIATE_TYPE = {
    "name": "fake",
    "can_host_children": False,
    "embeddable": True,
    "default_events": ["fake_event"],
    "setup_fn": setup_fake_associate,
    "project_fn": project_fake_associate,
    "destroy_fn": destroy_fake_associate,
}


FAKE_CONTAINER_ASSOCIATE_TYPE = {
    "name": "fake_container",
    "can_host_children": True,
    "embeddable": True,
    "default_events": [],
    "setup_fn": setup_fake_container_associate,
    "project_fn": project_fake_associate,
    "destroy_fn": destroy_fake_associate,
}


def reset_fake_runtime():
    rt.reset()
    rt.tk_master = FakeWidget("tk_master")


def pump_runtime_once():
    rt.process_incoming_builds()
    rt.deliver_messages()
    rt.process_castle_messages()
    rt.reconcile_dirty_castles()
    rt.process_structural_requests()
    rt.project_dirty_associates()


def simple_template(build_context=None):
    return {
        "kind": "castle_spec",
        "template_name": "simple_castle",
        "state": {"handled": 0},
        "handle_fn": handle_simple_message,
        "reconcile_fn": reconcile_simple_castle,
        "associates": [
            {
                "kind": "associate_spec",
                "name": "source",
                "associate_type": FAKE_ASSOCIATE_TYPE,
                "desired": {},
            },
            {
                "kind": "associate_spec",
                "name": "target",
                "associate_type": FAKE_ASSOCIATE_TYPE,
                "desired": {"value": 0},
            },
        ],
    }


def handle_simple_message(castle, message):
    if message["type"] == "fake_event":
        castle["state"]["handled"] += 1
        castle["state"]["last_payload"] = message["payload"]
        return rt.HANDLED_DIRTY
    return rt.IGNORED


def reconcile_simple_castle(castle):
    target = rt.get_associate(castle, "target")
    rt.target_associate(target)
    rt.set_desired("value", castle["state"]["handled"])


def failing_template(build_context=None):
    return {
        "kind": "castle_spec",
        "template_name": "failing_castle",
        "associates": [
            {
                "kind": "associate_spec",
                "name": "broken",
                "associate_type": FAKE_ASSOCIATE_TYPE,
                "desired": {"fail_setup": True},
            },
        ],
    }


def child_template(build_context=None):
    label = (build_context or {}).get("label", "initial_child")
    return {
        "kind": "castle_spec",
        "template_name": label,
        "associates": [
            {
                "kind": "associate_spec",
                "name": "child_root",
                "associate_type": FAKE_ASSOCIATE_TYPE,
                "desired": {},
            },
        ],
    }


def parent_with_child_template(build_context=None):
    return {
        "kind": "castle_spec",
        "template_name": "parent_castle",
        "child_castles": [
            {
                "kind": "child_castle_spec",
                "name": "child",
                "template_fn": child_template,
                "build_context": {"label": "initial_child"},
            },
        ],
        "associates": [
            {
                "kind": "associate_spec",
                "name": "container",
                "associate_type": FAKE_CONTAINER_ASSOCIATE_TYPE,
                "desired": {},
            },
        ],
        "spots": {
            "name": "root_spot",
            "children": [
                {
                    "name": "child_spot",
                    "grid": {"row": 0, "column": 0},
                },
            ],
        },
        "placements": {
            "root_spot": {"kind": "associate", "name": "container"},
            "child_spot": {"kind": "child_castle", "name": "child"},
        },
    }


def build_template(template_fn, build_context=None):
    request = rt.make_build_request(template_fn, build_context or {})
    return rt.execute_build_request(request)


class RuntimeInvariantTests(unittest.TestCase):
    def setUp(self):
        reset_fake_runtime()

    def tearDown(self):
        rt.reset()

    def test_build_allocates_and_activates_runtime_records(self):
        build = build_template(simple_template)

        self.assertEqual(build["status"], "completed")
        self.assertEqual(len(rt.castles), 1)
        self.assertEqual(len(rt.associates), 2)
        self.assertEqual(len(rt.routes), 2)
        self.assertTrue(all(castle["active"] for castle in rt.castles.values()))
        self.assertTrue(all(associate["active"] for associate in rt.associates.values()))
        self.assertTrue(all(route["active"] for route in rt.routes))

        source = next(a for a in rt.associates.values() if a["name"] == "source")
        self.assertEqual(source["effective_events"], {"fake_event"})

    def test_failed_build_cleans_up_partial_records(self):
        build = build_template(failing_template)

        self.assertIsNone(build)
        self.assertEqual(len(rt.faulty_builds), 1)
        self.assertEqual(rt.castles, {})
        self.assertEqual(rt.associates, {})
        self.assertEqual(rt.routes, [])
        self.assertEqual(rt.dirty_associates, set())

    def test_default_route_delivers_associate_outbox_to_host_castle(self):
        build_template(simple_template)
        castle = next(iter(rt.castles.values()))
        source = rt.get_associate(castle, "source")

        source["outbox"].append(
            {
                "kind": "event",
                "type": "fake_event",
                "origin": "source",
                "emitter": "source",
                "payload": {"n": 1},
            }
        )
        rt.deliver_messages()

        self.assertEqual(source["outbox"], [])
        self.assertEqual(len(castle["inbox"]), 1)
        self.assertEqual(castle["inbox"][0]["payload"], {"n": 1})

    def test_dirty_projection_runs_for_active_and_skips_inactive_associates(self):
        build_template(simple_template)
        associate = next(iter(rt.associates.values()))

        associate["private"]["project_count"] = 0
        rt.mark_dirty(associate)
        rt.project_dirty_associates()
        self.assertEqual(associate["private"]["project_count"], 1)

        associate["active"] = False
        rt.mark_dirty(associate)
        rt.project_dirty_associates()
        self.assertEqual(associate["private"]["project_count"], 1)
        self.assertEqual(rt.dirty_associates, set())

    def test_two_builds_do_not_cross_route_messages(self):
        first_build = build_template(simple_template)
        second_build = build_template(simple_template)
        first_castle = rt.castles[first_build["castle_ids"][0]]
        second_castle = rt.castles[second_build["castle_ids"][0]]
        first_source = rt.get_associate(first_castle, "source")
        second_source = rt.get_associate(second_castle, "source")

        first_source["outbox"].append(
            {
                "kind": "event",
                "type": "fake_event",
                "origin": "source",
                "emitter": "source",
                "payload": {"source": "first"},
            }
        )
        second_source["outbox"].append(
            {
                "kind": "event",
                "type": "fake_event",
                "origin": "source",
                "emitter": "source",
                "payload": {"source": "second"},
            }
        )

        rt.deliver_messages()

        self.assertEqual(first_castle["inbox"][0]["payload"], {"source": "first"})
        self.assertEqual(second_castle["inbox"][0]["payload"], {"source": "second"})

    def test_message_processing_reconciles_and_projects_dirty_associates(self):
        build_template(simple_template)
        castle = next(iter(rt.castles.values()))
        source = rt.get_associate(castle, "source")
        target = rt.get_associate(castle, "target")

        source["outbox"].append(
            {
                "kind": "event",
                "type": "fake_event",
                "origin": "source",
                "emitter": "source",
                "payload": {},
            }
        )
        pump_runtime_once()

        self.assertEqual(castle["state"]["handled"], 1)
        self.assertEqual(target["desired"]["value"], 1)
        self.assertGreaterEqual(target["private"].get("project_count", 0), 1)

    def test_destroy_all_clears_runtime_records_and_queues(self):
        build_template(simple_template)
        rt.incoming_builds.append({"kind": "build_request"})
        rt.structural_requests.append({"kind": "clearing"})

        rt.destroy_all()

        self.assertEqual(rt.castles, {})
        self.assertEqual(rt.associates, {})
        self.assertEqual(rt.routes, [])
        self.assertEqual(rt.completed_builds, [])
        self.assertEqual(rt.incoming_builds, [])
        self.assertEqual(rt.structural_requests, [])

    def test_structural_replacement_replaces_spot_child_castle(self):
        build_template(parent_with_child_template)
        parent = next(
            castle for castle in rt.castles.values()
            if castle["template_name"] == "parent_castle"
        )
        original_child_id = parent["children"]["child"]

        rt.target_castle(parent)
        rt.schedule_replacement(
            "child_spot",
            child_template,
            {"label": "replacement_child"},
        )
        rt.process_structural_requests()

        replacement_child_id = parent["children"]["child"]
        self.assertNotEqual(original_child_id, replacement_child_id)
        self.assertNotIn(original_child_id, rt.castles)
        self.assertEqual(rt.castles[replacement_child_id]["template_name"], "replacement_child")
        self.assertEqual(parent["spots"]["child_spot"]["occupant"]["id"], replacement_child_id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
