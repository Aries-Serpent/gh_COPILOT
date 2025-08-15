"""SOX compliance stub routing to `update_compliance_metrics`."""
from scripts.compliance.update_compliance_metrics import update_compliance_metrics

def main() -> float:
    """Run compliance metrics update and return composite score."""
    return update_compliance_metrics()

if __name__ == "__main__":  # pragma: no cover
    main()
