#!/usr/bin/env python3
"""
Enhanced Platform Demo
======================

Demonstrates unique script generation capabilities with different parameters".""
"""

from comprehensive_script_generation_platform import (]
)
import sys
import os
from pathlib import Path
from datetime import datetime
import uuid

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def enhanced_demo():
  " "" """Enhanced demonstration with unique script generatio"n""."""
    prin"t""("[LAUNCH] ENHANCED SCRIPT GENERATION DEMONSTRATI"O""N")
    prin"t""("""=" * 60)

    platform = ComprehensiveScriptGenerationPlatform()

    # Generate a unique script with timestamp
    timestamp = datetime.now().strftim"e""("%Y%m%d_%H%M"%""S")
    unique_id = str(uuid.uuid4())[:8]

    request = ScriptGenerationRequest(]
        script_name"=""f"unique_analyzer_{timestamp}_{unique_id}."p""y",
        customizations={]
          " "" "SCRIPT_NA"M""E":" ""f"Unique Database Analyzer {timestam"p""}",
          " "" "AUTH"O""R"":"" "Enhanced Demo Platfo"r""m",
          " "" "VERSI"O""N"":"" "2.0".""0",
          " "" "CLASS_NA"M""E":" ""f"UniqueAnalyzer{unique_id.replac"e""('''-'','' ''')''}",
          " "" "ENVIRONME"N""T"":"" "stagi"n""g"
        },
        requirements"=""["sqlit"e""3"","" "pathl"i""b"","" "loggi"n""g"","" "js"o""n"","" "dateti"m""e"],
        description"=""f"Unique database analyzer generated at {timestam"p""}"
    )

    print"(""f"\n[WRENCH] Generating Unique Script: {request.script_nam"e""}")
    prin"t""("""-" * 60)

    result = platform.generate_script(request)

    if resul"t""["stat"u""s"] ="="" "succe"s""s":
        prin"t""("[SUCCESS] SUCCESS! Unique Script Generat"e""d")
        print"(""f"   [FOLDER] Script: {request.script_nam"e""}")
        print"(""f"   [?] Generation ID: {resul"t""['generation_'i''d'']''}")
        print(
           " ""f"   [BAR_CHART] Size: {resul"t""['metri'c''s'']''['content_size_byt'e''s']} byt'e''s")
        print"(""f"   [NOTES] Lines: {resul"t""['metri'c''s'']''['lines_of_co'd''e'']''}")
        print"(""f"   [?][?]  Time: {resul"t""['metri'c''s'']''['generation_time_'m''s']} 'm''s")
        print(
           " ""f"   [SUCCESS] Compliance: {resul"t""['compliance_stat'u''s'']''['complia'n''t'']''}")

        # Save the script
        generated_scripts_dir = Pat"h""("generated_scrip"t""s")
        generated_scripts_dir.mkdir(exist_ok=True)

        script_path = generated_scripts_dir / request.script_name
        with open(script_path","" """w", encodin"g""="utf"-""8") as f:
            f.write(resul"t""["generated_conte"n""t"])

        print"(""f"   [STORAGE] Saved to: {script_pat"h""}")

        # Show first few lines of generated script
        prin"t""("\n[?] Generated Script Previe"w"":")
        prin"t""("""-" * 30)
        lines = resul"t""["generated_conte"n""t"].spli"t""('''\n')
        for i, line in enumerate(lines[:10]):
            print'(''f"{i+1:2d}: {lin"e""}")
        prin"t""("    ."."".")

        # Show adaptations and enhancements
        if resul"t""["adaptations_appli"e""d"]:
            print(
               " ""f"\n[PROCESSING] Adaptations Applied ({len(resul"t""['adaptations_appli'e''d'])}')'':")
            for adaptation in resul"t""["adaptations_appli"e""d"]:
                print"(""f"   [?] {adaptatio"n""}")

        if resul"t""["copilot_enhancemen"t""s"]:
            print(
               " ""f"\n[?] Copilot Enhancements ({len(resul"t""['copilot_enhancemen't''s'])}')'':")
            for enhancement in resul"t""["copilot_enhancemen"t""s"]:
                print"(""f"   [?] {enhancemen"t""}")

        # Check compliance details
        compliance = resul"t""["compliance_stat"u""s"]
        if compliance.ge"t""("issu"e""s"):
            print(
               " ""f"\n[WARNING]  Compliance Issues ({len(complianc"e""['issu'e''s'])}')'':")
            for issue in complianc"e""["issu"e""s"]:
                print"(""f"   [?] {issu"e""}")

        if compliance.ge"t""("recommendatio"n""s"):
            print(
               " ""f"\n[LIGHTBULB] Recommendations ({len(complianc"e""['recommendatio'n''s'])}')'':")
            for rec in complianc"e""["recommendatio"n""s"]:
                print"(""f"   [?] {re"c""}")

    else:
        print(
           " ""f"[ERROR] Generation Failed: {result.ge"t""('err'o''r'','' 'Unknown err'o''r'')''}")

    print"(""f"\n[TARGET] Demo Complete - Unique script generated successfull"y""!")
    print"(""f"   Check the generated_scripts/ directory for your new scrip"t"".")


if __name__ ="="" "__main"_""_":
    enhanced_demo()"
""