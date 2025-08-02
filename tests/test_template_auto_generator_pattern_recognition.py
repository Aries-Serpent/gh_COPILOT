from unittest.mock import patch

import template_engine.auto_generator as ag


def test_auto_generator_uses_pattern_recognizer():
    with patch.object(ag, "PatternRecognizer") as mock_recognizer, \
         patch.object(ag.TemplateAutoGenerator, "_load_patterns", return_value=["a", "b"]), \
         patch.object(ag.TemplateAutoGenerator, "_load_templates", return_value=[]), \
         patch.object(ag, "get_pattern_templates", return_value=[]), \
         patch.object(ag, "get_lesson_templates", return_value={}):
        ag.TemplateAutoGenerator()
        instance = mock_recognizer.return_value
        instance.learn.assert_called_once_with(["a", "b"])
        instance.recognize.assert_called_once_with(["a", "b"], db_path=ag.DEFAULT_ANALYTICS_DB)
