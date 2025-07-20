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
        system.ml_models["scaler"].transform = MagicMock(
            wraps=system.ml_models["scaler"].transform
        )
        system.ml_models["anomaly_detector"].predict = MagicMock(
            wraps=system.ml_models["anomaly_detector"].predict
        )
        system._generate_healing_strategy = MagicMock(return_value="noop")
        system._execute_healing_action = MagicMock(
            return_value={"result": "ok", "success": True}
        )

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
