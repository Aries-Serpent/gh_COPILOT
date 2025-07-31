import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock

from scripts.utilities.self_healing_self_learning_system import (
    SelfHealingSelfLearningSystem,
    SystemHealth,
)
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import json
import pickle
import sqlite3


class TestSelfHealingSelfLearningSystem:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        Path(self.temp_dir, "databases").mkdir(exist_ok=True)

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def test_models_load(self):
        system = SelfHealingSelfLearningSystem(workspace_path=self.temp_dir)
        assert isinstance(system.ml_models["anomaly_detector"], IsolationForest)
        assert isinstance(system.ml_models["scaler"], StandardScaler)

    def test_anomaly_detection_uses_scaler(self):
        system = SelfHealingSelfLearningSystem(workspace_path=self.temp_dir)
        # Train models with dummy data
        data = [[100, 0, 0], [50, 1, 1]]
        system.ml_models["scaler"].fit(data)
        scaled = system.ml_models["scaler"].transform(data)
        system.ml_models["anomaly_detector"].fit(scaled)
        # Patch methods
        system.ml_models["scaler"].transform = MagicMock(wraps=system.ml_models["scaler"].transform)
        system.ml_models["anomaly_detector"].predict = MagicMock(wraps=system.ml_models["anomaly_detector"].predict)
        system._generate_healing_strategy = MagicMock(return_value="noop")
        system._execute_healing_action = MagicMock(return_value={"result": "ok", "success": True})

        metrics = {
            "comp": SystemHealth(
                component="comp",
                health_score=40.0,
                issues=["i"],
                recommendations=[],
                timestamp=datetime.now(),
            )
        }
        system.detect_anomalies_and_heal(metrics)
        assert system.ml_models["scaler"].transform.called
        assert system.ml_models["anomaly_detector"].predict.called

    def test_model_training_and_anomaly_detection(self):
        system = SelfHealingSelfLearningSystem(workspace_path=self.temp_dir)
        import numpy as np

        rng = np.random.default_rng(42)
        normal = rng.normal(0, 1, size=(50, 3)).tolist()
        outlier = [[10, 10, 10]]
        system.ml_models["scaler"].fit(normal)
        transformed = system.ml_models["scaler"].transform(normal)
        system.ml_models["anomaly_detector"].fit(transformed)

        models_dir = Path(self.temp_dir) / "models" / "autonomous"
        models_dir.mkdir(parents=True, exist_ok=True)
        with open(models_dir / "scaler.pkl", "wb") as f:
            pickle.dump(system.ml_models["scaler"], f)
        with open(models_dir / "anomaly_detector.pkl", "wb") as f:
            pickle.dump(system.ml_models["anomaly_detector"], f)

        new_system = SelfHealingSelfLearningSystem(workspace_path=self.temp_dir)
        scaled_outlier = new_system.ml_models["scaler"].transform(outlier)
        prediction = new_system.ml_models["anomaly_detector"].predict(scaled_outlier)[0]
        assert prediction == -1

    def test_copilot_initialization_records_validation(self):
        system = SelfHealingSelfLearningSystem(workspace_path=self.temp_dir)
        assert system is not None
        db_path = Path(self.temp_dir, "databases", "v3_self_learning_engine.db")
        with sqlite3.connect(db_path) as conn:
            row = conn.execute(
                "SELECT response_data FROM copilot_interactions WHERE interaction_type='INITIALIZATION' ORDER BY id DESC LIMIT 1"
            ).fetchone()
        data = json.loads(row[0])
        assert data["validation"]["primary_check"] is True
        assert isinstance(data["validation"]["secondary_check"], bool)
