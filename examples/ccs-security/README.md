# CCS Security Integration for Aider

This example demonstrates how to integrate [CCS (Credential & Compliance Standard)](https://github.com/Correctover/ccs-verifier)
into Aider for runtime command verification.

## What is CCS?

CCS is an IETF-standardized runtime verification framework that provides:
- **RCE Protection**: Detects dangerous shell commands (rm -rf, chmod 777, etc.)
- **SSRF Prevention**: Blocks requests to internal/cloud metadata endpoints
- **Credential Leak Detection**: Prevents exposure of secrets and API keys
- **Sub-millisecond Overhead**: P50 ≈ 7.5μs in-process verification

## Quick Start

```python
from examples.ccs_security.ccs_guard import ccs_verify_command

# Verify command before execution
allowed, reason = ccs_verify_command("rm -rf /")
if not allowed:
    print(f"Command blocked: {reason}")
```

## Integration with Aider

The `ccs_guard.py` module provides a wrapper for aider's `run_cmd` function:

```python
from examples.ccs_security.ccs_guard import wrap_run_cmd
from aider.run_cmd import run_cmd as original_run_cmd

# Wrap the original run_cmd with CCS verification
run_cmd = wrap_run_cmd(original_run_cmd)

# Now all commands are verified before execution
run_cmd("ls -la")  # Allowed
run_cmd("rm -rf /")  # Blocked
```

## References

- [CCS IETF Draft](https://datatracker.ietf.org/doc/draft-correctover-ccs/)
- [CCS PyPI Package](https://pypi.org/project/ccs-verifier/)
- [Zenodo DOI: 10.5281/zenodo.21783723](https://doi.org/10.5281/zenodo.21783723)
