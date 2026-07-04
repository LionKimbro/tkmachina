# ADR-0004: Associate State Boundaries

## Discussion Item

Desired data and observed data are mixed together.

Associates currently keep one `data` dictionary. That dictionary contains
desired values:

```python
"title"
"desired_width"
"desired_height"
"min_width"
```

It also contains observed values and projection bookkeeping:

```python
"actual_width"
"actual_height"
"_projected_size"
```

The window associate mutates `actual_width` and `actual_height` from Tk
configure events, while the castle also stores window size in castle state.

The design may need a sharper distinction:

```python
associate["desired"]   # what the castle/RT wants projected
associate["observed"]  # what Tk reported back
associate["private"]   # projection bookkeeping and Tk-specific state
```

Example:

```python
associate["desired"]["text"] = "Required (4 left)"
associate["observed"]["actual_width"] = 460
associate["private"]["projected_size"] = (460, 480)
```

This would clarify the roles:

- castles write desired semantic state
- associates observe raw GUI reality
- RT moves messages
- projectors compare desired/private against Tk


## Codex Implementation Amendment

ADR-0004 is approved for the current runtime.

Associate records now separate state into three dictionaries:

```python
associate["desired"]   # values RT/castles want projected onto Tk
associate["observed"]  # values reported by Tk or the associate's widget layer
associate["private"]   # projector and widget bookkeeping
```

`associate_spec["desired"]` is the preferred way to declare initial projection
targets. `associate_spec["observed"]` may declare initial observed values when
needed. `associate_spec["private"]` is reserved for projector implementation
details.

For transition only, `associate_spec["data"]` is still accepted as a fallback
source for `associate["desired"]` if `desired` is not provided.

Runtime-facing mutation should use:

```python
rt.target_associate(associate)
rt.set_desired("text", "Required (4 left)")
```

`rt.set_data(...)` remains as a temporary compatibility alias for
`rt.set_desired(...)`.

Castles should not write `associate["observed"]` directly. Observed values are
owned by associates and their widget callbacks. If a castle needs to remember
or interpret observed reality, it should receive a message and store the
semantic interpretation in castle state.

