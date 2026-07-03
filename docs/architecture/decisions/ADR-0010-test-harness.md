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

