# Monitoring Guidelines

This document outlines configuration options for the Unified Monitoring Optimization System.

## Configuration

- `contamination`: float between 0 and 0.5 controlling expected fraction of anomalies for `detect_anomalies` and `auto_heal_session`.
- `db_path`: optional path to `analytics.db` for storing metrics, anomaly results and quantum scores.
- `table`: metrics table name for `push_metrics`. Names must contain only
  letters, numbers, and underscores.
- `session_id`: identifier linking metrics to session lifecycle data.

## Quantum Integration

The monitoring utilities support a quantum placeholder. When `quantum_algorithm_library_expansion.quantum_score_stub` is available, its value is used for anomaly scoring and via `record_quantum_score`. In environments without the stub a deterministic average of metric values is used instead, providing repeatable behavior while leaving room for future quantum enhancements.

