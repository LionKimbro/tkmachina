# TkMachina Model

TkMachina is a machine-oriented GUI system built on top of Tkinter.

Tkinter is the rendering and input substrate. TkMachina is the application
world: a disciplined runtime where interface elements are treated as bounded
machines, events are data, queues mediate behavior, and the app author works in
controlled declarative structures rather than scattered callback glue.

The promise is quick-and-clean apps: applications that are fast to create
because their machinery is disciplined, inspectable, traceable, and safe.

## Core Thesis

A GUI should not be a loose callback graph.

In ordinary Tkinter, an interaction often looks like this:

```text
click -> callback -> arbitrary mutation
```

In TkMachina, an interaction should look like this:

```text
outside input
  -> gate
  -> event record
  -> queue
  -> castle machine
  -> state transition
  -> visible output and/or emitted event
```

The app author composes machines rather than wiring raw callbacks directly into
widgets.

Widgets do not own application behavior. Buttons do not call arbitrary
functions. Bindings do not leak into app code. Interface elements emit semantic
events, and those events pass through gates and queues into small, well-defined
machines.

## Design Commitments

TkMachina keeps these commitments at the center of the model:

- No raw callback sprawl.
- No invisible behavior.
- No casual mutation across machine boundaries.
- No mystery state.
- Everything enters through gates.
- Everything important becomes data.
- Every machine has a record.
- Every transition should be inspectable.
- Layout is separate from logic.
- Visual projection is separate from application state.
- Child embedding is a first-class operation, not an accidental frame trick.

## Main Concepts

The final conception rests on this stack:

```text
Castle
  logical machine/component

Surface
  declared visual morphology owned by a castle

Lady
  companion to one Tk widget

Slot
  declared place where a child castle may be mounted

Layout
  rules for arranging ladies and slots inside a surface

Route
  declared movement of messages between emitters, queues, and castles

Queue
  controlled place where event records wait to be processed

Gatehouse
  dispatch/routing/queue runtime

Trace
  inspectable history of events, transitions, and emissions
```

Compactly:

> A castle may have a surface. A surface contains ladies and slots. Ladies tend
> widgets. Slots host child castles. Layout arranges ladies and slots. Routes
> move messages between castles.

## Castle

A Castle is the logical unit of the application.

It is not merely a frame, widget, or object. It is a bounded machine with:

- a name or identity
- owned state
- declared inputs
- declared outputs
- queues
- routes
- lifecycle
- handlers or reducers
- an optional surface
- traceable transitions

A castle receives event records through controlled paths. It does not expose its
interior to arbitrary external mutation.

The castle is responsible for application meaning: what a pressed button means,
what a changed selection means, what state transition should occur, and what
messages or projections should result.

### Castle Boundary

The boundary is essential.

Outside code should not casually reach inside a castle and mutate its state or
widgets. Inputs enter through gates, queues, and declared routes. Outputs leave
as visible projection changes or emitted semantic messages.

This preserves the central discipline: every important thing that happens to a
castle should be visible as data.

### Castle State

Castle state belongs to the castle.

Widget state may mirror, project, or temporarily hold Tk-level details, but the
meaningful application state is owned by the castle. A Lady may know how to make
a button look disabled; the castle decides whether the button should be disabled
as part of its state and rules.

### Castle Lifecycle

A castle needs lifecycle phases because embedding and replacement are core
behaviors.

The exact API is unresolved, but the model needs phases for:

- creation
- queue setup
- route setup
- surface creation
- mounting
- start/activation
- event processing
- unmounting
- route teardown
- stopping
- destruction

Lifecycle is especially important for child castles mounted into slots.

## Surface

A Surface is the declared visual morphology of a castle.

The castle is logical. The surface is the castle's visible arrangement.

A surface contains:

- a host Lady, usually a container-like widget companion
- child Ladies
- Slots for child castles
- Layout rules

The visible part of a castle is not merely a bag of widgets. It is:

```text
surface = host lady + ladies + slots + layout
```

This concept solves an important problem: a castle may have visual structure
without making visual structure identical to the castle itself.

### Example Shape

```python
context_panel_surface = {
    "host": {"kind": "frame_lady", "name": "main"},
    "ladies": [
        {
            "kind": "label_lady",
            "name": "title",
            "data": {"text": "Context Jetpack"},
        },
        {
            "kind": "button_lady",
            "name": "priority",
            "data": {"text": "Required"},
        },
    ],
    "layout": [
        {
            "target": "title",
            "grid": {"row": 0, "column": 0, "sticky": "w"},
        },
        {
            "target": "priority",
            "grid": {"row": 1, "column": 0, "sticky": "ew"},
        },
    ],
}
```

The exact schema may change, but the separation should remain: declaration of
visual parts, declaration of layout, and runtime projection are distinct.

## Lady

A Lady is the dignified companion of a Tk widget.

It is not just a proxy, adapter, or wrapper. A Lady tends one widget's desired
presentation, projects state outward to Tkinter, receives raw Tk happenings, and
sends properly dressed semantic events through the gatehouse to the host castle.

Examples:

- `button_lady`
- `canvas_lady`
- `tree_lady`
- `window_lady`
- `frame_lady`
- `panel_lady`

Every widget has its Lady. The castle does not speak directly to the Tk
machinery without her.

### Lady Responsibilities

A Lady may know how to:

- create or attach to a Tk widget
- keep desired presentation data
- project desired presentation onto the widget
- translate raw Tk commands or bindings into semantic events
- report surface incidents through the gatehouse
- expose visible output in a controlled way

For a button, this might include:

- text
- enabled/disabled state
- visibility
- command hookup
- event emission when pressed

### What a Lady Does Not Own

A Lady does not own application behavior.

A button Lady can emit `button_pressed`. It should not decide what that press
means to the application.

A Lady also should not own layout decisions. A button Lady may know how to be
projected as a button, but it should not decide that it belongs at row 3,
column 2. That belongs to the host surface.

## Layout

Layout is the surface's placement discipline.

The gridding problem forced this distinction: layout cannot live inside each
individual Lady, because placement belongs to the containing visual surface, not
to the child widget itself.

A button can say:

```text
I am a button.
My name is "required_toggle".
My text is "Required".
```

The containing castle surface says:

```text
Put that button here.
Put this label there.
Give column 1 the stretch.
Make this area fill.
```

Therefore:

```text
Lady = widget companion
Layout spec = host's placement instruction
Host Lady = surface/container companion that applies concrete Tk layout
```

For Tkinter, the concrete implementation may use `.grid(...)`, grid weights,
sticky values, padding, and related options. But those details should be driven
by a layout declaration, not scattered imperative calls.

## Slot

A Slot is a declared place where a child castle may be mounted.

This is not the same as a child castle. The distinction matters:

```text
slot != child
```

A parent castle surface can declare slots such as:

- toolbar
- main
- inspector
- status

The slot provides a stable host location and contract. A child castle can then
be mounted into that slot.

### Slot Responsibilities

A slot may provide:

- visual host location
- layout placement
- lifecycle containment
- default parent-child routing
- replacement behavior
- teardown behavior
- an abstraction over the concrete Tk host

The slot may currently be implemented using a `frame_lady`, but the logical
contract is not "put a frame here." The contract is "mount a child castle here."

That leaves room for a slot to be backed by different visual mechanisms over
time, such as a frame, label frame, notebook tab, paned window pane, canvas
region, toplevel, or even a non-visible host.

## Embedding Castles

Embedding is a first-class operation.

Mounting a child castle into a parent is not equivalent to embedding a frame. It
requires runtime work across logic, routing, surface, and lifecycle.

To embed a child castle, the system must be able to:

1. Create or receive the child castle.
2. Attach it to the parent castle tree.
3. Create or attach its queues.
4. Establish default topology routes where appropriate.
5. Create its surface.
6. Provide its surface with a host widget from the parent slot.
7. Mount its Ladies.
8. Apply layout into the parent surface.
9. Start or activate its lifecycle.

The model therefore needs operations like:

```python
mount_castle(parent, child, slot="inspector")
```

or a data-shaped declaration like:

```python
{
    "kind": "castle_slot",
    "name": "inspector_area",
    "child": "inspector_castle",
    "grid": {"row": 0, "column": 1, "sticky": "nsew"},
}
```

The API is unresolved, but the behavior is part of the core model.

### Dynamic Replacement

Slots also solve dynamic replacement.

To replace the castle in a slot, the system should be able to:

1. Stop the old child castle.
2. Unmount its surface.
3. Destroy or detach its Ladies.
4. Remove its routes.
5. Mount the new child castle.
6. Create or activate its routes.
7. Project the new surface.

This keeps dynamic UI changes disciplined and traceable.

## Gatehouse

The Gatehouse is the runtime concept that controls entry, routing, queuing, and
dispatch.

Nothing should simply call into the application. Inputs enter through gates.

The gatehouse receives semantic events from Ladies or castles, places them into
the appropriate queues, routes them according to declarations, and supports
traceability.

It is the difference between:

```text
button calls arbitrary function
```

and:

```text
button_lady emits event record -> gatehouse routes it -> castle queue receives it
```

## Event Records

Events are data.

A Lady emits a semantic record rather than invoking arbitrary application code.
A representative event might look like:

```python
{
    "kind": "event",
    "type": "button_pressed",
    "origin": "priority_button",
    "emitter": "priority_button",
    "payload": {},
    "trace_id": "...",
}
```

Important fields include:

- `kind`: the record category
- `type`: semantic event type
- `origin`: where the event originated
- `emitter`: the declared emitter identity
- `payload`: event-specific data
- `trace_id`: identifier for inspection and debugging

The exact event schema is unresolved, but the principle is settled: user and UI
events become records before they become behavior.

## Queues

Queues mediate behavior.

A queue gives the system a controlled place to put event records before they are
processed by a castle. This supports traceability, ordering, and separation
between raw input and state transition.

The model assumes castles receive messages through queues rather than by direct
callback invocation.

Open questions remain around queue implementation, ordering rules, sync vs
async processing, reentrancy, failure handling, and whether there are multiple
queue classes.

## Routes

Routes move messages between emitters, queues, and castles.

Routes may match on:

- emitter
- event type
- origin
- source castle
- destination castle
- slot name
- child name

Representative declarations:

```python
{
    "from": "priority_button",
    "type": "button_pressed",
    "to": "context_panel",
}
```

```python
{
    "from": "file_list",
    "type": "selection_changed",
    "to": "inspector",
}
```

The final v0 conception does not require explicit channels. The simpler model
is named emitters plus typed messages plus declared routes. Channels can be
introduced later only if routing by type/source becomes too muddy.

## Trace

Trace is the inspectable history of the runtime.

TkMachina needs tracing because its value depends on visibility. If events,
routes, queue movement, state transitions, and projections remain visible, then
GUI behavior becomes understandable instead of mysterious.

A trace should eventually help answer questions like:

- What raw Tk happening occurred?
- Which Lady translated it?
- What event record was emitted?
- Which route matched?
- Which queue received it?
- Which castle handled it?
- What state changed?
- What output was projected?
- What new messages were emitted?

The trace system is not specified yet, but traceability is part of the core
promise.

## The Runtime Flow

A typical interaction should proceed like this:

```text
1. User interacts with a Tk widget.
2. The widget's Lady receives the raw Tk happening.
3. The Lady translates it into a semantic event record.
4. The event enters through the gatehouse.
5. The gatehouse routes the event to the appropriate castle queue.
6. The castle processes the queued event.
7. The castle updates owned state.
8. The castle emits any resulting semantic events.
9. The castle updates desired presentation data.
10. Ladies project the desired presentation onto Tk widgets.
11. Trace records the path.
```

This flow replaces hidden callback behavior with inspectable machine behavior.

## Mental Model Glossary

### Button

A button is not behavior. It is an input port.

The `button_lady` tends the actual Tk button and emits semantic button events.
The castle decides what those events mean.

### Frame

A frame is not merely a container. In TkMachina terms, it is usually part of a
surface and may serve as a host boundary.

If the frame is tending a surface, a `frame_lady` or `panel_lady` may apply
layout, host child Ladies, or back a Slot.

### Window

A window is not a pile of widgets. It is a runtime cell whose visible surface is
record-backed.

A `window_lady` may tend the Tk toplevel/root concerns, while the castle owns
the state and behavior.

### GUI

A GUI is not a callback graph. It is a visible society of communicating
machines.

## Resolved Hypotheticals And Challenges

### What if the author needs quick applications?

The model is not meant to make simple apps slow by burying them in ceremony. The
goal is quick-and-clean apps: make the clean way the fast way.

Resolution: provide disciplined defaults and declarative structures so the
author composes machines instead of hand-wiring callbacks.

### What if a widget needs to display state and report user interaction?

Raw widgets should not become application objects, and castles should not
manipulate Tk details directly.

Resolution: each widget has a Lady. The Lady tends projection and translates raw
Tk happenings into semantic events.

### What if a button press needs to trigger application behavior?

The button should not directly call arbitrary app code.

Resolution: the button Lady emits an event record such as `button_pressed`. The
gatehouse routes it to a castle queue. The castle handler or reducer decides
what behavior follows.

### What if the author needs gridding?

Gridding is a real abstraction leak if placed in the wrong layer. Individual
Ladies should not decide their own row, column, sticky behavior, or stretch
rules.

Resolution: layout belongs to the castle's surface declaration. A host Lady may
apply `.grid(...)`, but the layout decision belongs to the containing surface.

### What if the author needs embedded child components?

Embedding a child castle is more than embedding a frame. It involves the parent
tree, child queues, routes, surface mounting, host widgets, layout, and
lifecycle.

Resolution: use Slots. A parent surface declares stable places where child
castles may be mounted.

### What if the author needs to replace an embedded panel?

Dynamic replacement can become messy if the child is treated as a raw widget or
frame.

Resolution: replace the castle mounted in a Slot. The slot owns the host
location and replacement behavior; the runtime handles lifecycle, route
teardown, unmounting, mounting, and projection.

### What if a child castle needs to communicate with its parent?

Direct parent-child mutation would break boundaries.

Resolution: parent-child communication should use emitted messages, routes, and
queues. Slot topology may provide useful default routes, but behavior remains
declared.

### What if route declarations become too complex?

The final conception keeps v0 simpler by using named emitters, event types,
origins, and destinations rather than explicit channels.

Resolution: defer channels. Add them only if source/type routing becomes
insufficient.

### What if a visual host changes implementation later?

If the model talks directly in terms of frames, it becomes too coupled to the
current Tk implementation.

Resolution: the logical contract is Slot, not frame. A slot may be backed by a
frame today and something else later.

### What if behavior becomes hard to debug?

Hidden callbacks and casual mutation make GUI behavior opaque.

Resolution: events are records, transitions are handled by castles, routes are
declared, and trace IDs let the runtime tell the story of what happened.

## Structural Laws

These distinctions should remain sacred:

```text
Layout != logic
Slot != child
Surface != castle
Lady != widget
Button != behavior
Frame != application boundary by itself
Window != pile of widgets
GUI != callback graph
```

Positive form:

```text
Castle = logical machine
Surface = visual declaration
Lady = widget companion
Slot = child-castle host contract
Layout = placement rules
Route = message path
Queue = controlled message buffer
Gatehouse = routing and dispatch runtime
Trace = inspectable history
```

## Declarative Record Bias

TkMachina should prefer records over hidden imperative glue.

The following should be visible as data wherever practical:

- interface structure
- surface morphology
- layout
- bindings
- events
- routes
- state
- lifecycle relationships
- emitted outputs
- trace history

This does not mean there will be no Python code. It means the important
structure should not be trapped inside arbitrary callbacks where the runtime
cannot inspect it.

## Expected Author Experience

The app author should feel like they are assembling clean machinery:

- declare castles
- declare surfaces
- declare Ladies
- declare slots
- declare layout
- declare routes
- implement castle state transitions
- let the runtime handle gatekeeping, queuing, mounting, projection, and trace

The author should not need to remember where they hid a callback, which widget
mutates which variable, or which frame secretly owns which child behavior.

## Open Loose Ends

The conception is strong, but several design details remain unresolved.

### Exact Record Schemas

The model needs concrete schemas for:

- castle declarations
- surface declarations
- Lady declarations
- slot declarations
- layout declarations
- route declarations
- event records
- trace records

### Handler Or Reducer API

The castle processing model needs a concrete shape:

- reducer-style pure transitions
- handler-style imperative methods
- hybrid model
- return values for emitted events and projection changes
- access rules for state and runtime services

### Queue Semantics

The queue model needs decisions about:

- sync vs async processing
- ordering guarantees
- reentrancy
- batching
- priority
- cancellation
- error behavior
- backpressure

### Routing Semantics

Routes need precise rules for:

- matching
- priority
- fan-out
- default parent-child routes
- missing destination behavior
- route teardown
- dynamic route creation
- trace integration

### Lifecycle API

The system needs exact lifecycle hook names and guarantees for:

- creating
- mounting
- starting
- stopping
- unmounting
- replacing
- destroying
- error cleanup

### Layout Schema

The layout layer needs to specify:

- grid options
- row and column weights
- padding
- sticky behavior
- visibility
- responsive resizing
- nested surfaces
- validation

### Slot Semantics

Slots need rules for:

- whether a slot can be empty
- whether a slot can host multiple children
- replacement behavior
- default route topology
- lifecycle ownership
- visual host strategy
- non-visible slots

### Lady Catalog

The first set of Ladies needs to be chosen and specified.

Likely early Ladies include:

- window_lady
- frame_lady
- label_lady
- button_lady
- entry_lady
- list_lady or tree_lady
- canvas_lady

Each Lady needs a clear contract for desired presentation, emitted events, and
projection behavior.

### State Projection Rules

The system needs rules for how castle state becomes desired presentation data
and how desired presentation data is diffed or projected onto Tk widgets.

Open questions include:

- direct projection vs derived view records
- diffing vs full reconfigure
- ownership of transient widget values
- two-way data entry flows
- validation errors

### Trace Storage And Inspection

Trace is central but unspecified.

The model needs decisions about:

- in-memory trace format
- trace retention
- trace IDs
- parent-child trace correlation
- developer inspection tools
- logging integration

### Error Handling

The runtime needs a policy for:

- handler exceptions
- route failures
- projection failures
- invalid declarations
- lifecycle failures
- partial mount failures

### Testing Model

The machine structure suggests tests should be possible without a live Tk
surface in many cases.

The test story needs to define:

- castle transition tests
- route tests
- surface declaration validation
- Lady projection tests
- integration tests with Tk
- trace assertions

## Minimal First Experiment

The smallest useful experiment should include:

- Castle
- Surface
- Lady
- Slot
- Layout
- Route
- Queue
- Lifecycle
- Trace

It should omit explicit channels for now.

The first experiment should prove this loop:

```text
button_lady emits event
  -> gatehouse routes event
  -> castle queue receives event
  -> castle updates state
  -> state projects through Lady
  -> trace shows the path
```

It should also prove one embedded child castle mounted into one parent Slot.

## One-Sentence Model

TkMachina is a Tkinter-backed GUI runtime where bounded castle machines own
state and behavior, surfaces declare visual form, Ladies tend widgets, slots
host child castles, layout arranges visible parts, and the gatehouse routes
typed event records through queues so applications stay quick, clean,
inspectable, and controlled.
