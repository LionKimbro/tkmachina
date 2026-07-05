# Rules

This file records working rules we want to keep following across TkMachina
design and implementation.

## Documentation Source Rule

- Status: Active
- Origin date: 2026-07-05
- Source: manual HTML snapshot discussion

Update `docs/manual/` as the living manual source.

Do not treat `docs/manual-html/` as the source of truth. It is an occasional
HTML snapshot for friendly reading and presentation.

During ordinary coding and design work, update `docs/manual/` only.

Update `docs/manual-html/` on special occasions, such as after several days of
coding or when we intentionally want a refreshed public/manual snapshot.

## Manual Public Surface Rule

- Status: Active
- Origin date: 2026-07-05
- Source: guidance4 follow-up

Keep `docs/manual/` up to date when changing TkMachina's public surface,
conceptual model, associate contracts, runtime vocabulary, or user-facing
architecture.

The manual does not need to become polished before development can continue,
but it should remain structurally honest about what the system currently
promises.

## Associate Test Coverage Rule

- Status: Active
- Origin date: 2026-07-05
- Source: guidance4 follow-up

When adding or changing associate behavior, add at least one relevant test.

Use fake-associate runtime invariant tests when the behavior is about RT
contracts. Use hosted Tk tests when the behavior depends on real Tk lifecycle,
bindings, projection, widget state, or event-loop behavior.
