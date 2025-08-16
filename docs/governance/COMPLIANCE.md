# Compliance Model & Enforcement

**Composite Score (𝓢)**
\[
  \mathcal{S} = 100 \times \left(
    0.30 \cdot \frac{L}{100} +
    0.40 \cdot \frac{T}{100} +
    0.15 \cdot \frac{P}{100} +
    0.15 \cdot \frac{S_e}{100}
  \right)
\]

**Threshold:** \( \mathcal{S} \ge 85 \)

**Signals:**
- **L (Lint):** Ruff violations mapped to score
- **T (Tests):** Pytest pass ratio
- **P (Placeholders):** TODO/FIXME density per KLOC (lower is better)
- **S_e (Sessions):** % session entries without error (if source present; neutral otherwise)

**Enforcement Semantics:**
- Block when score < 85 (exit code 2), record in `docs/status_index.json`.
- Never modify or activate `.github/workflows/*`.
