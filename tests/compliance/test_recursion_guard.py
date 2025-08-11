import os
from types import SimpleNamespace

import pytest

from enterprise_modules.compliance import ComplianceError, enforce_anti_recursion


def test_enforce_anti_recursion_tracks_lineage():
    ctx = SimpleNamespace()
    enforce_anti_recursion(ctx)
    assert ctx.pid == os.getpid()
    assert ctx.parent_pid == os.getppid()
    assert ctx.ancestors == [os.getpid()]
    if ctx.recursion_depth > 0:
        ctx.recursion_depth -= 1
    ctx.ancestors.pop()


def test_enforce_anti_recursion_pid_loop():
    pid = os.getpid()
    ctx = SimpleNamespace(ancestors=[pid])
    with pytest.raises(ComplianceError):
        enforce_anti_recursion(ctx)


def test_enforce_anti_recursion_parent_mismatch():
    ctx = SimpleNamespace(parent_pid=-1)
    with pytest.raises(ComplianceError):
        enforce_anti_recursion(ctx)

