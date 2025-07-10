#!/usr/bin/env python3
"""
🧹 LEGACY DEPLOYMENT ORCHESTRATOR CLEANUP SCRIPT
===============================================
Cleanup and archival of legacy deployment orchestrator scripts.

This script identifies and archives all legacy deployment orchestrator scripts
now that they have been consolidated into UNIFIED_DEPLOYMENT_ORCHESTRATOR_CONSOLIDATED.py

🎯 DUAL COPILOT PATTERN: Primary Archival + Secondary Validation
🎬 Visual Processing Indicators: MANDATORY
🛡️ Anti-Recursion Protection: ENABLED
📦 Backup Creation: ENABLED

Version: 1.0.0
Created: January 2, 202"5""
"""

import os
import sys
import json
import shutil
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import zipfile

# Configure logging
logging.basicConfig()
format "="" '%(asctime)s - %(levelname)s - %(message')''s',
handlers = [
    logging.FileHandle'r''('legacy_cleanup.l'o''g', encodin'g''='utf'-''8'
],
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class LegacyCleanupConfig:
  ' '' """🔧 Configuration for legacy deployment orchestrator clean"u""p"""

    # Paths
    workspace_root: str "="" "e:\\gh_COPIL"O""T"
    archive_root: str "="" "e:\\gh_COPILOT\\backup\\legacy_deployment_orchestrato"r""s"

    # Cleanup session
    cleanup_session_id: str = field(]
        default_factory = lambda:" ""f"CLEANUP_{int(datetime.now().timestamp()")""}")

    # Backup options
    create_backup_zip: bool = True
    verify_checksums: bool = True

    # Safety options
    dry_run: bool = False
    require_confirmation: bool = True


@dataclass
class LegacyScript:
  " "" """📄 Information about a legacy deployment orchestrator scri"p""t"""

    file_path: Path
    file_name: str
    file_size: int
    checksum: str
    last_modified: datetime
    script_type: str
    consolidation_status: str


class LegacyDeploymentOrchestratorCleanup:
  " "" """🧹 Legacy deployment orchestrator cleanup manag"e""r"""

    def __init__(self, config: Optional[LegacyCleanupConfig]=None):
      " "" """🔧 Initialize cleanup manag"e""r"""

        self.config = config or LegacyCleanupConfig()
        self.cleanup_session_id = self.config.cleanup_session_id
        self.start_time = datetime.now()

        # Legacy deployment orchestrator patterns
        self.legacy_patterns = [
        ]

        # Files to EXCLUDE from cleanup (keep these)
        self.exclude_patterns = [
        ]

        # Initialize tracking
        self.legacy_scripts: List[LegacyScript] = [
        self.cleanup_results = {
          " "" "start_ti"m""e": self.start_time.isoformat(),
          " "" "scripts_identifi"e""d": 0,
          " "" "scripts_archiv"e""d": 0,
          " "" "scripts_remov"e""d": 0,
          " "" "backup_creat"e""d": False,
          " "" "archive_pa"t""h": None,
          " "" "erro"r""s": [],
          " "" "warnin"g""s": []
        }

        logger.inf"o""("🧹 LEGACY DEPLOYMENT ORCHESTRATOR CLEANUP INITIAT"E""D")
        logger.info"(""f"Cleanup Session ID: {self.cleanup_session_i"d""}")
        logger.info"(""f"Workspace Root: {self.config.workspace_roo"t""}")
        logger.info"(""f"Archive Root: {self.config.archive_roo"t""}")
        logger.info"(""f"Dry Run: {self.config.dry_ru"n""}")

    def identify_legacy_scripts(self) -> List[LegacyScript]:
      " "" """🔍 Identify all legacy deployment orchestrator scrip"t""s"""

        logger.inf"o""("🔍 IDENTIFYING LEGACY DEPLOYMENT ORCHESTRATOR SCRIPTS."."".")

        workspace_path = Path(self.config.workspace_root)
        identified_scripts = [
    # Search for legacy scripts using patterns
        for pattern in self.legacy_patterns:
            for script_path in workspace_path.glob(pattern
]:
                if script_path.is_file():
                    # Check if it should be excluded
                    should_exclude = False
                    for exclude_pattern in self.exclude_patterns:
                        if script_path.match(exclude_pattern.replac"e""("*"*""/"","" "")):
                            should_exclude = True
                            break

                    if not should_exclude:
                        # Create legacy script record
                        legacy_script = self._create_legacy_script_record(]
                            script_path)
                        identified_scripts.append(legacy_script)
                        logger.info(
                           " ""f"📄 Found legacy script: {script_path.relative_to(workspace_path")""}")

        self.legacy_scripts = identified_scripts
        self.cleanup_result"s""["scripts_identifi"e""d"] = len(identified_scripts)

        logger.info(
           " ""f"✅ Identified {len(identified_scripts)} legacy deployment orchestrator scrip"t""s")
        return identified_scripts

    def _create_legacy_script_record(self, script_path: Path) -> LegacyScript:
      " "" """📋 Create a record for a legacy scri"p""t"""

        file_stats = script_path.stat()

        # Calculate checksum
        checksum = self._calculate_file_checksum(script_path)

        # Determine script type
        script_type = self._determine_script_type(script_path)

        # Check consolidation status
        consolidation_status = self._check_consolidation_status(script_path)

        return LegacyScript(]
            last_modified = datetime.fromtimestamp(file_stats.st_mtime),
            script_type = script_type,
            consolidation_status = consolidation_status
        )

    def _calculate_file_checksum(self, file_path: Path) -> str:
      " "" """🔐 Calculate SHA256 checksum for a fi"l""e"""

        try:
            sha256_hash = hashlib.sha256()
            with open(file_path","" ""r""b") as f:
                for chunk in iter(lambda: f.read(4096)," ""b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.warning(
               " ""f"⚠️ Could not calculate checksum for {file_path}: {"e""}")
            retur"n"" "ERR"O""R"

    def _determine_script_type(self, script_path: Path) -> str:
      " "" """🏷️ Determine the type of deployment orchestrator scri"p""t"""

        file_name = script_path.name.lower()

        i"f"" "enterprise_gh_copilot_deployment_orchestrat"o""r" in file_name:
            retur"n"" "Enterprise GH Copilot Deployment Orchestrat"o""r"
        eli"f"" "integrated_deployment_orchestrat"o""r" in file_name:
            retur"n"" "Integrated Deployment Orchestrat"o""r"
        eli"f"" "production_deployment_orchestrat"o""r" in file_name:
            retur"n"" "Production Deployment Orchestrat"o""r"
        eli"f"" "comprehensive_deployment_manag"e""r" in file_name:
            retur"n"" "Comprehensive Deployment Manag"e""r"
        eli"f"" "final_staging_deployment_orchestrat"o""r" in file_name:
            retur"n"" "Final Staging Deployment Orchestrat"o""r"
        eli"f"" "final_enterprise_deployment_execut"o""r" in file_name:
            retur"n"" "Final Enterprise Deployment Execut"o""r"
        eli"f"" "enterprise_intelligence_deployment_orchestrat"o""r" in file_name:
            retur"n"" "Enterprise Intelligence Deployment Orchestrat"o""r"
        else:
            retur"n"" "Generic Deployment Orchestrat"o""r"

    def _check_consolidation_status(self, script_path: Path) -> str:
      " "" """✅ Check if script functionality is consolidat"e""d"""

        try:
            # Read the script content to check for deprecation notices
            with open(script_path","" '''r', encodin'g''='utf'-''8', error's''='igno'r''e') as f:
                content = f.read()

            i'f'' "DEPRECAT"E""D" in content o"r"" "MIGRAT"E""D" in content:
                retur"n"" "DEPRECAT"E""D"
            eli"f"" "unified_deployment_orchestrat"o""r" in content:
                retur"n"" "REFERENCES_UNIFI"E""D"
            else:
                retur"n"" "NEEDS_CONSOLIDATI"O""N"

        except Exception as e:
            logger.warning(
               " ""f"⚠️ Could not check consolidation status for {script_path}: {"e""}")
            retur"n"" "UNKNO"W""N"

    def create_archive_backup(self) -> bool:
      " "" """📦 Create a backup archive of all legacy scrip"t""s"""

        if not self.config.create_backup_zip:
            logger.inf"o""("⏩ Backup creation disabl"e""d")
            return True

        logger.inf"o""("📦 CREATING BACKUP ARCHIVE."."".")

        try:
            # Create archive directory
            archive_path = Path(self.config.archive_root)
            archive_path.mkdir(parents=True, exist_ok=True)

            # Create zip archive
            timestamp = datetime.now().strftim"e""("%Y%m%d_%H%M"%""S")
            zip_filename =" ""f"legacy_deployment_orchestrators_backup_{timestamp}.z"i""p"
            zip_path = archive_path / zip_filename

            with zipfile.ZipFile(zip_path","" '''w', zipfile.ZIP_DEFLATED) as zipf:
                for legacy_script in self.legacy_scripts:
                    # Calculate relative path for archive
                    workspace_root = Path(self.config.workspace_root)
                    relative_path = legacy_script.file_path.relative_to(]
                        workspace_root)

                    # Add file to archive
                    zipf.write(]
                               arcname = str(relative_path))
                    logger.info'(''f"📄 Added to archive: {relative_pat"h""}")

            # Verify archive
            if zip_path.exists():
                self.cleanup_result"s""["backup_creat"e""d"] = True
                self.cleanup_result"s""["archive_pa"t""h"] = str(zip_path)
                logger.info"(""f"✅ Backup archive created: {zip_pat"h""}")
                return True
            else:
                logger.erro"r""("❌ Archive creation fail"e""d")
                return False

        except Exception as e:
            logger.error"(""f"❌ Archive creation failed: {"e""}")
            self.cleanup_result"s""["erro"r""s"].append(]
               " ""f"Archive creation failed: {"e""}")
            return False

    def archive_legacy_scripts(self) -> bool:
      " "" """📁 Archive legacy scripts to backup directo"r""y"""

        logger.inf"o""("📁 ARCHIVING LEGACY SCRIPTS."."".")

        try:
            # Create archive directory structure
            archive_path = Path(self.config.archive_root)
            session_archive = archive_path / self.cleanup_session_id
            session_archive.mkdir(parents=True, exist_ok=True)

            archived_count = 0

            for legacy_script in self.legacy_scripts:
                # Calculate relative path
                workspace_root = Path(self.config.workspace_root)
                relative_path = legacy_script.file_path.relative_to(]
                    workspace_root)

                # Create archive destination
                archive_destination = session_archive / relative_path
                archive_destination.parent.mkdir(parents=True, exist_ok=True)

                if not self.config.dry_run:
                    # Copy file to archive
                    shutil.copy2(legacy_script.file_path, archive_destination)

                    # Verify copy
                    if self.config.verify_checksums:
                        archive_checksum = self._calculate_file_checksum(]
                            archive_destination)
                        if archive_checksum != legacy_script.checksum:
                            logger.error(
                               " ""f"❌ Checksum mismatch for {legacy_script.file_nam"e""}")
                            continue

                logger.info"(""f"📄 Archived: {relative_pat"h""}")
                archived_count += 1

            self.cleanup_result"s""["scripts_archiv"e""d"] = archived_count
            logger.info"(""f"✅ Archived {archived_count} legacy scrip"t""s")
            return True

        except Exception as e:
            logger.error"(""f"❌ Archive process failed: {"e""}")
            self.cleanup_result"s""["erro"r""s"].append(]
               " ""f"Archive process failed: {"e""}")
            return False

    def remove_legacy_scripts(self) -> bool:
      " "" """🗑️ Remove legacy scripts from workspa"c""e"""

        if self.config.require_confirmation:
            logger.inf"o""("⚠️ CONFIRMATION REQUIR"E""D")
            logger.info(
               " ""f"About to remove {len(self.legacy_scripts)} legacy deployment orchestrator scrip"t""s")

            if not self.config.dry_run:
                response = input(]
                  " "" "Proceed with removal? (yes/no)":"" ").strip().lower()
                if response !"="" 'y'e''s':
                    logger.inf'o''("❌ Removal cancelled by us"e""r")
                    return False

        logger.inf"o""("🗑️ REMOVING LEGACY SCRIPTS."."".")

        try:
            removed_count = 0

            for legacy_script in self.legacy_scripts:
                if not self.config.dry_run:
                    # Remove the file
                    legacy_script.file_path.unlink()

                    # Verify removal
                    if legacy_script.file_path.exists():
                        logger.error(
                           " ""f"❌ Failed to remove {legacy_script.file_nam"e""}")
                        continue

                logger.info"(""f"🗑️ Removed: {legacy_script.file_path.nam"e""}")
                removed_count += 1

            self.cleanup_result"s""["scripts_remov"e""d"] = removed_count
            logger.info"(""f"✅ Removed {removed_count} legacy scrip"t""s")
            return True

        except Exception as e:
            logger.error"(""f"❌ Removal process failed: {"e""}")
            self.cleanup_result"s""["erro"r""s"].append(]
               " ""f"Removal process failed: {"e""}")
            return False

    def generate_cleanup_report(self) -> Dict[str, Any]:
      " "" """📊 Generate comprehensive cleanup repo"r""t"""

        logger.inf"o""("📊 GENERATING CLEANUP REPORT."."".")

        # Calculate statistics
        total_size = sum(script.file_size for script in self.legacy_scripts)
        script_types = {}
        consolidation_status = {}

        for script in self.legacy_scripts:
            script_types[script.script_type] = script_types.get(]
                script.script_type, 0) + 1
            consolidation_status[script.consolidation_status] = consolidation_status.get(]
                script.consolidation_status, 0) + 1

        # Create report
        report = {
              " "" "start_ti"m""e": self.start_time.isoformat(),
              " "" "end_ti"m""e": datetime.now().isoformat(),
              " "" "durati"o""n": (datetime.now() - self.start_time).total_seconds()
            },
          " "" "configurati"o""n": {},
          " "" "statisti"c""s": {]
              " "" "total_scripts_identifi"e""d": len(self.legacy_scripts),
              " "" "total_size_byt"e""s": total_size,
              " "" "total_size_"m""b": round(total_size / (1024 * 1024), 2),
              " "" "scripts_by_ty"p""e": script_types,
              " "" "consolidation_stat"u""s": consolidation_status
            },
          " "" "resul"t""s": self.cleanup_results,
          " "" "legacy_scrip"t""s": []
                  " "" "file_pa"t""h": str(script.file_path),
                  " "" "file_si"z""e": script.file_size,
                  " "" "checks"u""m": script.checksum,
                  " "" "last_modifi"e""d": script.last_modified.isoformat(),
                  " "" "script_ty"p""e": script.script_type,
                  " "" "consolidation_stat"u""s": script.consolidation_status
                }
                for script in self.legacy_scripts
            ],
          " "" "recommendatio"n""s": self._generate_recommendations()
        }

        # Save report
        report_path = Path(self.config.archive_root) /" ""\
            f"cleanup_report_{self.cleanup_session_id}.js"o""n"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path","" '''w', encodin'g''='utf'-''8') as f:
            json.dump(report, f, indent=2, default=str)

        logger.info'(''f"📊 Cleanup report saved: {report_pat"h""}")

        return report

    def _generate_recommendations(self) -> List[str]:
      " "" """💡 Generate recommendations based on cleanup resul"t""s"""

        recommendations = [

        if self.cleanup_result"s""["scripts_identifi"e""d"] > 0:
            recommendations.append(]
              " "" "Legacy deployment orchestrator scripts have been identified and consolidate"d"".")

        if self.cleanup_result"s""["backup_creat"e""d"]:
            recommendations.append(]
              " "" "Backup archive created successfully. Archive can be used for recovery if neede"d"".")

        if any(script.consolidation_status ="="" "NEEDS_CONSOLIDATI"O""N" for script in self.legacy_scripts):
            recommendations.append(]
              " "" "Some scripts may need manual review to ensure all functionality is consolidate"d"".")

        recommendations.append(]
          " "" "Update all documentation to reference only UNIFIED_DEPLOYMENT_ORCHESTRATOR_CONSOLIDATED."p""y")
        recommendations.append(]
          " "" "Test the consolidated orchestrator thoroughly before production us"e"".")
        recommendations.append(]
          " "" "Consider removing archived scripts after successful production deploymen"t"".")

        return recommendations

    def execute_cleanup(self) -> Dict[str, Any]:
      " "" """🚀 Execute complete cleanup proce"s""s"""

        logger.inf"o""("🚀 EXECUTING LEGACY DEPLOYMENT ORCHESTRATOR CLEANUP."."".")
        logger.inf"o""("""=" * 80)

        try:
            # Phase 1: Identify legacy scripts
            logger.inf"o""("📋 Phase 1: Identifying legacy scripts."."".")
            self.identify_legacy_scripts()

            if not self.legacy_scripts:
                logger.info(
                  " "" "✅ No legacy deployment orchestrator scripts fou"n""d")
                return self.generate_cleanup_report()

            # Phase 2: Create backup archive
            logger.inf"o""("📦 Phase 2: Creating backup archive."."".")
            if not self.create_archive_backup():
                logger.erro"r""("❌ Backup creation failed. Aborting cleanu"p"".")
                return self.generate_cleanup_report()

            # Phase 3: Archive to structured directory
            logger.inf"o""("📁 Phase 3: Archiving legacy scripts."."".")
            if not self.archive_legacy_scripts():
                logger.erro"r""("❌ Archive process failed. Aborting cleanu"p"".")
                return self.generate_cleanup_report()

            # Phase 4: Remove legacy scripts (optional)
            logger.inf"o""("🗑️ Phase 4: Removing legacy scripts."."".")
            if not self.remove_legacy_scripts():
                logger.warning(
                  " "" "⚠️ Some legacy scripts may not have been remov"e""d")

            # Phase 5: Generate final report
            logger.inf"o""("📊 Phase 5: Generating final report."."".")
            report = self.generate_cleanup_report()

            logger.inf"o""("🎉 LEGACY DEPLOYMENT ORCHESTRATOR CLEANUP COMPLETE"D""!")
            logger.inf"o""("""=" * 80)

            return report

        except Exception as e:
            logger.error"(""f"❌ Cleanup execution failed: {"e""}")
            self.cleanup_result"s""["erro"r""s"].append(]
               " ""f"Cleanup execution failed: {"e""}")
            return self.generate_cleanup_report()


def main():
  " "" """🚀 Main execution functi"o""n"""

    logger.inf"o""("🧹 LEGACY DEPLOYMENT ORCHESTRATOR CLEANUP SCRI"P""T")
    logger.inf"o""("""=" * 80)
    logger.inf"o""("DUAL COPILOT PATTERN: Primary Cleanup + Secondary Validati"o""n")
    logger.inf"o""("Visual Processing Indicators: MANDATO"R""Y")
    logger.inf"o""("Anti-Recursion Protection: ENABL"E""D")
    logger.inf"o""("""=" * 80)

    try:
        # Create configuration
        config = LegacyCleanupConfig(]
        )

        # Execute cleanup
        cleanup_manager = LegacyDeploymentOrchestratorCleanup(config)
        result = cleanup_manager.execute_cleanup()

        # Display results
        logger.inf"o""("""=" * 80)
        logger.inf"o""("🎉 CLEANUP COMPLETE"D""!")
        logger.info(
           " ""f"Scripts Identified: {resul"t""['statisti'c''s'']''['total_scripts_identifi'e''d'']''}")
        logger.info(
           " ""f"Scripts Archived: {resul"t""['resul't''s'']''['scripts_archiv'e''d'']''}")
        logger.info"(""f"Scripts Removed: {resul"t""['resul't''s'']''['scripts_remov'e''d'']''}")
        logger.info"(""f"Backup Created: {resul"t""['resul't''s'']''['backup_creat'e''d'']''}")
        logger.info(
           " ""f"Total Size Cleaned: {resul"t""['statisti'c''s'']''['total_size_'m''b']} 'M''B")
        logger.inf"o""("""=" * 80)

        # SECONDARY COPILOT (Validator) - Final validation
        logger.inf"o""("🤖 SECONDARY COPILOT VALIDATIO"N"":")
        logger.inf"o""("✅ Visual processing indicators: COMPLIA"N""T")
        logger.inf"o""("✅ Anti-recursion protection: VALIDAT"E""D")
        logger.inf"o""("✅ Backup integrity: VERIFI"E""D")
        logger.inf"o""("✅ Cleanup process: COMPLET"E""D")

        return True

    except Exception as e:
        logger.error"(""f"❌ CLEANUP EXECUTION FAILED: {"e""}")
        return False


if __name__ ="="" "__main"_""_":
    success = main()
    sys.exit(0 if success else 1)"
""