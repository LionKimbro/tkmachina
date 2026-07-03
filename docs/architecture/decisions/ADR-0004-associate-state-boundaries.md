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

