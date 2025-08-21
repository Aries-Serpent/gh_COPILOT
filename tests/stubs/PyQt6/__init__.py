"""Minimal PyQt6 stub for tests.

This package provides lightweight stand-ins for the subset of PyQt6
functionality exercised in the test suite.  It offers a tiny signal
implementation, a basic ``QObject`` base class, and a rudimentary
``QCoreApplication`` singleton.  Widget classes are simple placeholders
to satisfy imports.
"""

from __future__ import annotations

from types import ModuleType


class _Signal:
    """Very small replacement for ``pyqtSignal``."""

    def __init__(self, *args, **kwargs) -> None:
        self._slots: list = []

    def connect(self, slot) -> None:  # pragma: no cover - trivial
        self._slots.append(slot)

    def emit(self, *args, **kwargs) -> None:  # pragma: no cover - trivial
        for slot in list(self._slots):
            slot(*args, **kwargs)


class QObject:
    """Base class placeholder."""

    def __init__(self, *args, **kwargs) -> None:  # pragma: no cover - trivial
        pass


class QCoreApplication:
    """Barebones ``QCoreApplication`` implementation."""

    _instance: QCoreApplication | None = None

    def __init__(self, *args, **kwargs) -> None:  # pragma: no cover - trivial
        QCoreApplication._instance = self

    @staticmethod
    def instance() -> QCoreApplication | None:
        return QCoreApplication._instance

    def quit(self) -> None:  # pragma: no cover - trivial
        QCoreApplication._instance = None


# Build submodules --------------------------------------------------------

QtCore = ModuleType("PyQt6.QtCore")
QtCore.QObject = QObject
QtCore.pyqtSignal = _Signal
QtCore.QCoreApplication = QCoreApplication
QtCore.QThread = type("QThread", (), {"__init__": lambda self, *a, **k: None})


class _Widget:
    def __init__(self, *args, **kwargs) -> None:  # pragma: no cover - trivial
        pass


QtWidgets = ModuleType("PyQt6.QtWidgets")
QtWidgets.QApplication = _Widget
QtWidgets.QFileDialog = _Widget
QtWidgets.QHBoxLayout = _Widget
QtWidgets.QMessageBox = _Widget
QtWidgets.QPushButton = _Widget
QtWidgets.QTabWidget = _Widget
QtWidgets.QTextEdit = _Widget
QtWidgets.QTreeWidget = _Widget
QtWidgets.QTreeWidgetItem = _Widget
QtWidgets.QVBoxLayout = _Widget
QtWidgets.QWidget = _Widget


__all__ = ["QtCore", "QtWidgets", "QObject", "QCoreApplication"]

