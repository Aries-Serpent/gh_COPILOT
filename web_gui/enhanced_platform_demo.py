#!/usr/bin/env python3
"""
Enhanced Platform Demo
======================

Demonstrates unique script generation capabilities with different parameters.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import uuid

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from comprehensive_script_generation_platform import (
    ComprehensiveScriptGenerationPlatform,
    ScriptGenerationRequest
)

def enhanced_demo():
    """Enhanced demonstration with unique script generation."""
    print("[LAUNCH] ENHANCED SCRIPT GENERATION DEMONSTRATION")
    print("=" * 60)

    platform = ComprehensiveScriptGenerationPlatform()

    # Generate a unique script with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]

    request = ScriptGenerationRequest(
        template_name="enterprise_database_analyzer",
        target_environment="staging",  # Different environment
        script_name=f"unique_analyzer_{timestamp}_{unique_id}.py",
        customizations={
            "SCRIPT_NAME": f"Unique Database Analyzer {timestamp}",
            "AUTHOR": "Enhanced Demo Platform",
            "VERSION": "2.0.0",
            "CLASS_NAME": f"UniqueAnalyzer{unique_id.replace('-', '')}",
            "ENVIRONMENT": "staging"
        },
        requirements=["sqlite3", "pathlib", "logging", "json", "datetime"],
        description=f"Unique database analyzer generated at {timestamp}"
    )

    print(f"\n[WRENCH] Generating Unique Script: {request.script_name}")
    print("-" * 60)

    result = platform.generate_script(request)

    if result["status"] == "success":
        print("[SUCCESS] SUCCESS! Unique Script Generated")
        print(f"   [FOLDER] Script: {request.script_name}")
        print(f"   [?] Generation ID: {result['generation_id']}")
        print(f"   [BAR_CHART] Size: {result['metrics']['content_size_bytes']} bytes")
        print(f"   [NOTES] Lines: {result['metrics']['lines_of_code']}")
        print(f"   [?][?]  Time: {result['metrics']['generation_time_ms']} ms")
        print(f"   [SUCCESS] Compliance: {result['compliance_status']['compliant']}")

        # Save the script
        generated_scripts_dir = Path("generated_scripts")
        generated_scripts_dir.mkdir(exist_ok=True)

        script_path = generated_scripts_dir / request.script_name
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(result["generated_content"])

        print(f"   [STORAGE] Saved to: {script_path}")

        # Show first few lines of generated script
        print("\n[?] Generated Script Preview:")
        print("-" * 30)
        lines = result["generated_content"].split('\n')
        for i, line in enumerate(lines[:10]):
            print(f"{i+1:2d}: {line}")
        print("    ...")

        # Show adaptations and enhancements
        if result["adaptations_applied"]:
            print(f"\n[PROCESSING] Adaptations Applied ({len(result['adaptations_applied'])}):")
            for adaptation in result["adaptations_applied"]:
                print(f"   [?] {adaptation}")

        if result["copilot_enhancements"]:
            print(f"\n[?] Copilot Enhancements ({len(result['copilot_enhancements'])}):")
            for enhancement in result["copilot_enhancements"]:
                print(f"   [?] {enhancement}")

        # Check compliance details
        compliance = result["compliance_status"]
        if compliance.get("issues"):
            print(f"\n[WARNING]  Compliance Issues ({len(compliance['issues'])}):")
            for issue in compliance["issues"]:
                print(f"   [?] {issue}")

        if compliance.get("recommendations"):
            print(f"\n[LIGHTBULB] Recommendations ({len(compliance['recommendations'])}):")
            for rec in compliance["recommendations"]:
                print(f"   [?] {rec}")

    else:
        print(f"[ERROR] Generation Failed: {result.get('error', 'Unknown error')}")

    print("\n[TARGET] Demo Complete - Unique script generated successfully!")
    print("   Check the generated_scripts/ directory for your new script.")

if __name__ == "__main__":
    enhanced_demo()
