DRY_RUN Analysis: snapshot conftest.py
=====================================

Observation
- Snapshot `conftest.py` mutates `sys.path` to include `src/`, sets GPU-related environment toggles, and influences global pytest collection.

Impact
- Our repository has its own test fixtures and broader suite. Adopting the snapshot conftest would interfere with global fixtures (we already observed DB migrations triggering).

Recommendation
- Do not ingest this file. Keep our minimal tests hermetic, and avoid global test side effects.

Decision
- Not applicable / risks conflicts. Add to deletion post-plan.

