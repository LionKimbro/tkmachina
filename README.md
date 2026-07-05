# tkmachina

## Tests

TkMachina currently has two small test tracks.

Runtime invariant tests use fake associate types and do not require real Tk
widgets:

```powershell
$env:PYTHONPATH='src'; python tests/run_runtime_invariants.py
```

Hosted Tk tests use `tkintertester` and run inside the real Tk event loop:

```powershell
$env:PYTHONPATH='src'; python guitests/test_runtime_hosted.py
$env:PYTHONPATH='src'; python guitests/test_entry_associate_hosted.py
```

From `cmd.exe`, run the whole suite:

```bat
run-tests.bat
```

## Examples

Entry associate demo with an inner castle and automatic child-to-parent
bubble-up routing:

```powershell
$env:PYTHONPATH='src'; python examples/entry_inner_castle_demo.py
```
