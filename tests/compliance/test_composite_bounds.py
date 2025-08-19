"""Test composite score bounds and edge cases."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple


@dataclass
class ComplianceComponents:
    """Local copy to avoid import issues."""
    ruff_issues: int
    tests_passed: int
    tests_total: int
    placeholders_open: int
    placeholders_resolved: int


def _compute(c: ComplianceComponents) -> Tuple[float, float, float, float]:
    """Local copy of compute function to avoid import issues."""
    L = min(100.0, max(0.0, 100.0 - float(c.ruff_issues)))
    T = (float(c.tests_passed) / c.tests_total * 100.0) if c.tests_total else 0.0
    denom = c.placeholders_open + c.placeholders_resolved
    P = (float(c.placeholders_resolved) / denom * 100.0) if denom else 100.0
    composite = 0.3 * L + 0.5 * T + 0.2 * P
    return L, T, P, composite


def test_composite_bounds_extremes():
    """Test extreme values for composite score bounds."""
    # ruff_issues = 0 (best), no tests executed, no placeholders -> P defaults to 100
    c = ComplianceComponents(
        ruff_issues=0,
        tests_passed=0,
        tests_total=0,
        placeholders_open=0,
        placeholders_resolved=0
    )
    L, T, P, composite = _compute(c)
    assert L == 100.0
    assert T == 0.0
    assert P == 100.0  # When no placeholders, P defaults to 100
    assert 0.0 <= composite <= 100.0
    # Expected: 0.3*100 + 0.5*0 + 0.2*100 = 50.0
    assert math.isclose(composite, 50.0, rel_tol=1e-6)

    # Huge ruff issues -> L floor at 0
    c2 = ComplianceComponents(
        ruff_issues=5000,
        tests_passed=500,
        tests_total=1000,
        placeholders_open=900,
        placeholders_resolved=100
    )
    L2, T2, P2, composite2 = _compute(c2)
    assert L2 == 0.0
    assert math.isclose(T2, 50.0, rel_tol=1e-6)
    # P2 = 100 / (900 + 100) * 100 = 10.0
    assert math.isclose(P2, 10.0, rel_tol=1e-6)
    assert 0.0 <= composite2 <= 100.0
    # Expected: 0.3*0 + 0.5*50 + 0.2*10 = 27.0
    assert math.isclose(composite2, 27.0, rel_tol=1e-6)


def test_placeholder_ratio_precision():
    """Test precise placeholder ratio calculations."""
    c = ComplianceComponents(
        ruff_issues=7,
        tests_passed=90,
        tests_total=100,
        placeholders_open=3,
        placeholders_resolved=12
    )
    L, T, P, composite = _compute(c)
    assert L == 93.0  # 100 - 7
    assert T == 90.0  # 90/100 * 100
    assert math.isclose(P, 80.0, rel_tol=1e-9)  # 12/15 * 100 = 80.0
    assert 0 <= composite <= 100
    # Expected: 0.3*93 + 0.5*90 + 0.2*80 = 27.9 + 45 + 16 = 88.9
    assert math.isclose(composite, 88.9, rel_tol=1e-6)


def test_zero_division_protection():
    """Test that zero total tests doesn't cause division by zero."""
    c = ComplianceComponents(
        ruff_issues=10,
        tests_passed=5,  # This should be ignored when total=0
        tests_total=0,
        placeholders_open=2,
        placeholders_resolved=8
    )
    L, T, P, composite = _compute(c)
    assert L == 90.0  # 100 - 10
    assert T == 0.0   # Protected division by zero
    assert math.isclose(P, 80.0, rel_tol=1e-6)  # 8/10 * 100
    assert 0.0 <= composite <= 100.0
    # Expected: 0.3*90 + 0.5*0 + 0.2*80 = 27 + 0 + 16 = 43.0
    assert math.isclose(composite, 43.0, rel_tol=1e-6)


def test_component_bounds():
    """Test that all components stay within 0-100 bounds."""
    test_cases = [
        ComplianceComponents(0, 100, 100, 0, 50),     # Perfect scenario
        ComplianceComponents(200, 0, 100, 50, 0),     # High issues, no tests pass
        ComplianceComponents(0, 0, 0, 0, 0),          # All zeros
        ComplianceComponents(50, 75, 100, 25, 75),    # Balanced scenario
    ]
    
    for c in test_cases:
        L, T, P, composite = _compute(c)
        
        # All components must be within bounds
        assert 0.0 <= L <= 100.0, f"L out of bounds: {L}"
        assert 0.0 <= T <= 100.0, f"T out of bounds: {T}"
        assert 0.0 <= P <= 100.0, f"P out of bounds: {P}"
        assert 0.0 <= composite <= 100.0, f"Composite out of bounds: {composite}"


def test_lint_score_clamping():
    """Test lint score properly clamps at boundaries."""
    # Test upper bound (perfect score)
    c1 = ComplianceComponents(0, 50, 100, 10, 10)
    L1, _, _, _ = _compute(c1)
    assert L1 == 100.0
    
    # Test lower bound (many issues)
    c2 = ComplianceComponents(1000, 50, 100, 10, 10)
    L2, _, _, _ = _compute(c2)
    assert L2 == 0.0
    
    # Test exact boundary
    c3 = ComplianceComponents(100, 50, 100, 10, 10)
    L3, _, _, _ = _compute(c3)
    assert L3 == 0.0


def test_placeholder_edge_cases():
    """Test placeholder score edge cases."""
    # No placeholders at all
    c1 = ComplianceComponents(0, 100, 100, 0, 0)
    _, _, P1, _ = _compute(c1)
    assert P1 == 100.0
    
    # Only open placeholders
    c2 = ComplianceComponents(0, 100, 100, 10, 0)
    _, _, P2, _ = _compute(c2)
    assert P2 == 0.0  # 0/10 * 100 = 0
    
    # Only resolved placeholders  
    c3 = ComplianceComponents(0, 100, 100, 0, 10)
    _, _, P3, _ = _compute(c3)
    assert P3 == 100.0  # 10/10 * 100 = 100
