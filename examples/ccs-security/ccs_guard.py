"""
CCS Security Guard for Aider

Provides runtime command verification for aider's shell execution.
Integrates CCS (Credential & Compliance Standard) to prevent dangerous commands.

Usage:
    from examples.ccs_security.ccs_guard import ccs_verify_command
    
    # Before executing any command:
    allowed, reason = ccs_verify_command("rm -rf /")
    if not allowed:
        print(f"Command blocked: {reason}")
"""

import logging
from typing import Tuple, Optional

try:
    from ccs_verifier import Verifier, Command
    from ccs_verifier.builtin_rules import RCERule, SSRFRule, CredentialLeakRule
    CCS_AVAILABLE = True
except ImportError:
    CCS_AVAILABLE = False

logger = logging.getLogger(__name__)

_verifier: Optional[Verifier] = None

def _get_verifier() -> Optional[Verifier]:
    """Lazy-initialize the CCS verifier."""
    global _verifier
    if _verifier is None and CCS_AVAILABLE:
        rules = [RCERule(), SSRFRule(), CredentialLeakRule()]
        _verifier = Verifier(rules=rules)
        logger.info("CCS security guard initialized for aider")
    return _verifier


def ccs_verify_command(command: str) -> Tuple[bool, str]:
    """
    Verify a command using CCS security rules.
    
    Args:
        command: The shell command to verify
        
    Returns:
        Tuple of (allowed: bool, reason: str)
        - If allowed is True, command is safe to execute
        - If allowed is False, reason explains why it was blocked
    """
    if not CCS_AVAILABLE:
        logger.warning("ccs-verifier not installed, skipping security check")
        return True, "CCS not available"
    
    verifier = _get_verifier()
    if verifier is None:
        return True, "Verifier initialization failed"
    
    try:
        cmd = Command(
            agent_id="aider",
            tool="shell",
            params={"command": command}
        )
        result = verifier.verify(cmd)
        
        if result.verdict.value == "deny":
            reason = getattr(result, "reason", "CCS security policy violation")
            logger.warning(f"CCS blocked command: {command[:80]}... Reason: {reason}")
            return False, reason
        
        return True, "CCS verified safe"
        
    except Exception as e:
        logger.error(f"CCS verification error: {e}")
        # Fail open: allow command if verification fails
        return True, f"CCS verification error: {e}"


def wrap_run_cmd(original_run_cmd):
    """
    Wrap aider's run_cmd function with CCS verification.
    
    Usage in aider's code:
        from examples.ccs_security.ccs_guard import wrap_run_cmd
        from aider.run_cmd import run_cmd as original_run_cmd
        
        run_cmd = wrap_run_cmd(original_run_cmd)
    """
    def wrapped(command, verbose=False, error_print=None, cwd=None):
        allowed, reason = ccs_verify_command(command)
        if not allowed:
            error_msg = f"Command blocked by CCS security: {reason}"
            if error_print:
                error_print(error_msg)
            else:
                print(error_msg)
            return 1, error_msg
        return original_run_cmd(command, verbose=verbose, error_print=error_print, cwd=cwd)
    
    return wrapped


def demo():
    """Demonstrate CCS security guard for aider."""
    print("=" * 60)
    print("CCS Security Guard for Aider - Demo")
    print("=" * 60)
    
    test_commands = [
        ("ls -la", "List files"),
        ("git status", "Git status"),
        ("rm -rf /", "Destructive RCE"),
        ("cat /etc/shadow", "Sensitive file access"),
        ("curl http://169.254.169.254/latest/meta-data/", "AWS metadata SSRF"),
    ]
    
    for cmd, description in test_commands:
        allowed, reason = ccs_verify_command(cmd)
        status = "✓ ALLOW" if allowed else "✗ DENY"
        print(f"{status} | {description:<30} | {cmd[:40]}")
        if not allowed:
            print(f"       Reason: {reason}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    demo()
