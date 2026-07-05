# TkMachina Manual

This is the living manual for TkMachina. It is intentionally rough at first:
the purpose is to make the public promises of the system visible before the
associate library grows much larger.

## Table Of Contents

### 1. Tutorial

Planned tutorial path:

- Tutorial 1: A window with a button and label
- Tutorial 2: Entry input and semantic events
- Tutorial 3: A child castle inside a spot
- Tutorial 4: Replacing a child castle
- Tutorial 5: Reading the global trace

### 2. Conceptual Overview

- [How Associates Work](concepts-associates.md)
- Planned: Castles
- Planned: Spots and placements
- Planned: Routes and messages
- Planned: Builds
- Planned: Dirty projection
- Planned: Structural changes
- Planned: Global castles

### 3. Core Mechanics

Planned lifecycle chapters:

- Build request submission
- Template expansion
- Castle, associate, and spot allocation
- Placement validation
- Widget construction
- Layout
- Route wiring
- Activation
- Runtime ticks
- Message delivery
- Castle reconciliation
- Associate projection
- Scheduled structural mutation
- Destruction

### 4. Associate Reference

- [Associate Reference](associate-reference.md)
- Current associates:
  - `window`
  - `button`
  - `label`
  - `entry`
- Deferred associate families:
  - Text-backed associates
  - Treeview-backed associates
  - Canvas-backed associates

### 5. API Reference

Planned API entries:

- `setup_tk_bootstrap`
- `make_build_request`
- `submit_build_request`
- `run`
- `target_castle`
- `schedule_clearing`
- `schedule_building`
- `schedule_replacement`
- `target_associate`
- `get_desired`
- `get_observed`
- `set_desired`
- `set_data`
- `mark_dirty`
- `add_trace`
- `get_trace_entries`
- `destroy_all`

### 6. Glossary

- [Glossary](glossary.md)

## Current Manual Priorities

The manual should answer:

- What is a castle?
- What is an associate?
- What is `desired`?
- What is `observed`?
- What is `private`?
- What is a spot?
- What is a placement?
- What is a route?
- What is an event?
- What is a structural request?
- What does a user get to rely on?

The manual is also an architecture test. If an associate reference page cannot
describe one clear public promise, the associate may need to be split.
