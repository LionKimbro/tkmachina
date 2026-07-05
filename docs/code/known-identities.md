date: 2026-07-05
source-conversation: https://chatgpt.com/c/6a48c3b0-6e48-83e8-ab6c-dd152ae4a4f9


context: I'm evaluating ADR-0005, about name scoping,
         and trying to understand the extent of names in
	 the system as it is today, right now;

  STILL.  These diagrams (that follow) are ridiculously useful
  for understanding the system.  And should the system evolve
  into something new, I'll STILL want something that works similar
  to how these diagrams work -- just updated for whatever future
  reality we have.


== WARNING ==
date: 2026-07-05

The system is changing rapidly. This note has been updated through ADR-0005,
including the rename from castle["name"] to castle["template_name"].


== Runtime-level name/ID knowledge ==
date: 2026-07-05

rt module
│
├── castles
│   └── { castle_id: castle_object }
│
│       Example:
│       {
│         "castle:1": <demo_castle object>,
│         "castle:2": <trace_log_castle object>,
│         "castle:3": <demo_castle object>,
│         ...
│       }
│
│       Important:
│       - keyed by runtime ID
│       - NOT keyed by castle["template_name"]
│       - many castles may have the same castle["template_name"]
│
├── associates
│   └── { associate_id: associate_object }
│
│       Example:
│       {
│         "associate:1": <main_window associate>,
│         "associate:2": <priority_button associate>,
│         ...
│       }
│
│       Important:
│       - keyed by runtime ID
│       - NOT keyed by associate["name"]
│
├── routes
│   └── list of route records
│
│       Routes store resolved runtime IDs:
│       {
│         "from_kind": "associate",
│         "from_id": "associate:2",
│         "to_kind": "castle",
│         "to_id": "castle:1",
│         ...
│       }
│
├── global_castles
│   └── { global_name: castle_id }
│
│       Example:
│       {
│         "global_trace": "castle:1"
│       }
│
│       Important:
│       - this is the explicit global namespace
│       - ordinary template names do NOT automatically enter here
│
└── build queues / structural queues
    ├── incoming_builds
    ├── active_builds
    ├── completed_builds
    ├── faulty_builds
    └── structural_requests


== Castle Knowledge ==
date: 2026-07-05

castle
│
├── "id"
│   └── runtime identity
│       Example: "castle:7"
│
├── "template_name"
│   └── descriptive template name copied from the castle spec
│       Example: "demo_castle"
│
│       Important:
│       - not globally unique
│       - not the runtime address
│       - useful for traces, diagnostics, and build-local lookup
│
├── "parent"
│   └── parent castle ID or None
│
├── "child_name"
│   └── the name by which the parent knows this castle
│       Example: "trace_log"
│
│       Important:
│       - this is parent-local
│       - different from castle["template_name"]
│
├── "state"
│   └── castle-owned semantic state
│
├── "associates"
│   └── { local_associate_name: associate_id }
│
│       Example:
│       {
│         "priority_button": "associate:2",
│         "count_label": "associate:3",
│         "size_label": "associate:4"
│       }
│
│       Important:
│       - associate names are local to this castle
│       - another castle can also have "priority_button"
│
├── "children"
│   └── { parent_local_child_name: child_castle_id }
│
│       Example:
│       {
│         "trace_log": "castle:2"
│       }
│
│       Important:
│       - child names are local to the parent castle
│       - this is how the parent knows its children
│
├── "spots"
│   └── { local_spot_name: spot_record }
│
│       Example:
│       {
│         "trace_log_spot": {
│           "occupant": {
│             "kind": "child_castle",
│             "id": "castle:2"
│           }
│         }
│       }
│
├── "placements"
│   └── { local_spot_name: placement_spec }
│
│       Example:
│       {
│         "trace_log_spot": {
│           "kind": "child_castle",
│           "name": "trace_log"
│         }
│       }
│
├── "inbox"
├── "outbox"
├── "active"
├── "handle_fn"
└── "reconcile_fn"


== Take-aways, 2026-07-05 ==
date: 2026-07-05

  - the runtime-assigned "id" is the true unique identifier for a
    castle or associate

  - runtime ids are the true live-object addresses

  - "template_name" values are descriptive metadata, not addresses

  - "child_name" -- the name by which this castle is known
    by the castle's parent -- is actually more of a name
    than "template_name" ..! -- since it's actually used somewhere
    (by the parent castle)

  - local_associate_name is known and resolved within a castle


== Reflections, 2026-07-05 ==
date: 2026-07-05

It seems downright wrong to me to have a "name" that doesn't actually
do anything, isn't used by anyone.  In fact, the entire
"parent_local_child_name" and "child_name" system, seems to be working
AROUND the fact of a "name," and that's -- pretty dang weird.

The "name" is basically like making up a name for yourself,
calling yourself it interally, never telling anybody, and
that seems just a bit odd and counter-intuitive.  (Violates
the old programmer's "principle of least surprise," pretty
substantially.)

I also wonder if it wouldn't be better, with ids, to just -- have a
sequential number assigned to every object in the system, and just --
be done with these descriptive string names being minted.  That said,
it IS nice to look at an id, and have an idea of what kind of thing
it's pointing to.  OK, we keep the descriptive-minting-names.  There's
no performance difference, strings with the same id and ints compare
at comparable time spans, I believe.  We're not doing character by
character string comparisons here.


== Corrections from Wing-Cat, 2026-07-05 ==
date: 2026-07-05

Wing-Cat says, about the "decorative" nature of template names:

  castle["template_name"] is copied from the template spec into the castle
  object during shell allocation.

  It is used in traces and error messages, so it is not useless. But
  it is not the primary way the runtime finds a castle. It is
  descriptive metadata.

  The one place where template names currently matter more than
  decoration is build-local route/export
  resolution. find_built_castle_id_by_template_name(build, template_name) searches
  through castles created by the current build and returns the one
  whose castle["template_name"] matches.

    -- note: this is during the resolution of a build request

Otherwise, Wing-Cat says I'm right about (id) and about (child_name).


== ADR-0005 Decision Update, 2026-07-05 ==

TkMachina does not use castle template names as global object addresses.

Runtime communication is governed by routes, and routes store resolved runtime
IDs.

Runtime IDs are the true live-object identity.

Names are local authoring labels:

  - associate names are local to a castle
  - child names are local to a parent castle
  - template names describe what was built
  - global names exist only through explicit global export

No general path language is introduced by ADR-0005.
