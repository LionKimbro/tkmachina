# ADR-0010: Test Harness

## Discussion Item

There is no test harness or headless proof mode yet.

The architecture wants tests because this system is a tiny runtime, and
runtimes need invariants.

The first tests should not need to be Tk visual tests. They can be runtime
tests using fake associate types.

Useful invariant tests:

```text
building a template allocates one castle
building a template allocates N associates
failed build cleans up all records
destroy_all clears routes/castles/associates
button event routes to owning castle
castle handler marks associate dirty
dirty associate projection is skipped when inactive
two builds do not cross-route messages
```

Fake associate types could let the runtime be tested without real Tk.

## Status

Approved in principle.

## Decision

TkMachina should have a test strategy with two complementary layers.

First, runtime invariant tests should exercise RT behavior using fake associate
types where possible. These tests should verify construction, cleanup, routing,
dirty projection, failed builds, structural replacement, and isolation between
builds without requiring real Tk widgets.

Second, TkMachina should support event-loop-native hosted Tk tests for behavior
that depends on the real Tk lifecycle. These tests may use `tkintertester` or a
compatible harness. The goal is not screenshot-based visual testing, but live
runtime testing inside the actual Tk event loop.

Hosted Tk tests are appropriate for widget creation, projection, Tk callbacks,
`after(...)` timing, teardown, window close behavior, structural replacement,
and ensuring destroyed or inactive associates do not continue to emit or
project.

The test harness should remain outside the core runtime semantics. RT should
expose enough stable inspection helpers for tests, but normal runtime behavior
should not depend on the harness.

## Consequences

Fake associate tests keep core runtime invariants fast and direct.

Hosted Tk tests catch lifecycle and event-loop bugs that fake associates cannot.

The same application entry path should be reusable for normal runtime and test
runtime where practical.

