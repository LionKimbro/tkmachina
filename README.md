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
```
