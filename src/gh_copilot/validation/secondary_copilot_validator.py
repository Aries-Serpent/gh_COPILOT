class SecondaryCopilotValidator:
    """Fallback implementation when scripts.validation package is unavailable."""

    def validate(self, payload: dict) -> tuple[bool, str]:
        return True, "ok"
