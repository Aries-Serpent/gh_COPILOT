#!/usr/bin/env python3

from copilot.orchestrators.final_enterprise_orchestrator import (
    FinalEnterpriseOrchestrator,
)


def main():
    orchestrator = FinalEnterpriseOrchestrator()
    score = orchestrator.run()
    print(f"Final system efficiency: {score:.1f}%")


if __name__ == "__main__":
    main()
