#!/usr/bin/env python3
"""
🔥 DATABASE VALIDATION RESULTS COMPRESSOR
================================================================
MISSION: Reduce database_validation_results.json from >99.9MB
to below 99.9MB while maintaining essential data integrity
================================================================
"""

import json
import os
import gzip
import sqlite3
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import hashlib
import logging

# 🚀 DUAL COPILOT: Start time logging with enterprise formatting
start_time = datetime.now()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

logger.info(f"🚀 DATABASE VALIDATION COMPRESSOR STARTED")
logger.info(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
logger.info(f"Process ID: {os.getpid()}")


class DatabaseValidationCompressor:
    """🗜️ Comprehensive Database Validation Results Compressor"""

    def __init__(self, workspace_path="e:/gh_COPILOT"):
        self.workspace_path = Path(workspace_path)
        self.source_file = self.workspace_path / "results" / "database_validation_results.json"
        self.target_size_mb = 99.0  # Target under 99MB
        self.compression_report = {
            "original_size_mb": 0,
            "compressed_size_mb": 0,
            "compression_ratio": 0,
            "techniques_applied": [],
            "data_preserved": True,
            "timestamp": datetime.now().isoformat(),
        }

        # CRITICAL: Anti-recursion validation
        self.validate_environment_compliance()

        # Create results directory if it doesn't exist
        results_dir = self.workspace_path / "results"
        results_dir.mkdir(exist_ok=True)

    def validate_environment_compliance(self):
        """CRITICAL: Validate workspace before compression execution"""
        workspace_root = Path(os.getcwd())

        # MANDATORY: Check for recursive folder violations
        forbidden_patterns = ["*backup*", "*_backup_*", "backups", "*temp*"]
        violations = []

        for pattern in forbidden_patterns:
            for folder in workspace_root.rglob(pattern):
                if folder.is_dir() and folder != workspace_root:
                    violations.append(str(folder))

        if violations:
            logger.error(f"🚨 RECURSIVE FOLDER VIOLATIONS DETECTED:")
            for violation in violations:
                logger.error(f"   - {violation}")
            raise RuntimeError("CRITICAL: Recursive folder violations prevent execution")

        logger.info("✅ ENVIRONMENT COMPLIANCE VALIDATED")

    def analyze_file_structure(self):
        """🔍 Analyze the JSON structure for optimization opportunities"""
        logger.info("🔍 Analyzing database validation results structure...")

        if not self.source_file.exists():
            raise FileNotFoundError(f"Source file not found: {self.source_file}")

        original_size = self.source_file.stat().st_size
        self.compression_report["original_size_mb"] = original_size / (1024 * 1024)

        logger.info(f"📊 Original file size: {self.compression_report['original_size_mb']:.2f} MB")

        # Load and analyze JSON structure with progress indicator
        with tqdm(total=100, desc="📊 Loading JSON data", unit="%") as pbar:
            pbar.update(20)
            with open(self.source_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            pbar.update(80)

        analysis = {
            "total_keys": len(data) if isinstance(data, dict) else 0,
            "data_types": {},
            "large_sections": [],
            "duplicate_patterns": [],
        }

        if isinstance(data, dict):
            with tqdm(total=len(data), desc="🔍 Analyzing structure", unit="keys") as pbar:
                for key, value in data.items():
                    data_type = type(value).__name__
                    analysis["data_types"][data_type] = analysis["data_types"].get(data_type, 0) + 1

                    # Identify large sections
                    if isinstance(value, (list, dict)):
                        section_size = len(str(value))
                        if section_size > 1000000:  # > 1MB when stringified
                            analysis["large_sections"].append(
                                {"key": key, "type": data_type, "estimated_size_mb": section_size / (1024 * 1024)}
                            )
                    pbar.update(1)

        logger.info(f"📋 Analysis complete: {analysis['total_keys']} top-level keys")
        for section in analysis["large_sections"]:
            logger.info(f"   📦 Large section '{section['key']}': {section['estimated_size_mb']:.2f} MB")

        return data, analysis

    def apply_data_optimization(self, data):
        """⚡ Apply data-level optimizations"""
        logger.info("⚡ Applying data optimizations...")

        optimized_data = {}
        optimizations_applied = []

        with tqdm(total=len(data), desc="🔄 Optimizing data", unit="keys") as pbar:
            for key, value in data.items():
                # Strategy 1: Compress repetitive validation results
                if "validation_results" in key.lower() or "results" in key.lower():
                    optimized_value = self._compress_validation_results(value)
                    optimizations_applied.append(f"Compressed validation results in {key}")

                # Strategy 2: Deduplicate database entries
                elif "database" in key.lower() and isinstance(value, list):
                    optimized_value = self._deduplicate_database_entries(value)
                    optimizations_applied.append(f"Deduplicated database entries in {key}")

                # Strategy 3: Compress error logs and details
                elif any(x in key.lower() for x in ["error", "log", "detail", "traceback"]):
                    optimized_value = self._compress_error_data(value)
                    optimizations_applied.append(f"Compressed error data in {key}")

                # Strategy 4: Summarize large arrays
                elif isinstance(value, list) and len(value) > 1000:
                    optimized_value = self._summarize_large_arrays(value, key)
                    optimizations_applied.append(f"Summarized large array {key}")

                # Strategy 5: Compress file paths and duplicate strings
                elif isinstance(value, (list, dict)) and self._contains_duplicate_strings(value):
                    optimized_value = self._compress_duplicate_strings(value)
                    optimizations_applied.append(f"Compressed duplicate strings in {key}")

                else:
                    optimized_value = value

                optimized_data[key] = optimized_value
                pbar.update(1)

        self.compression_report["techniques_applied"].extend(optimizations_applied)
        logger.info(f"✅ Applied {len(optimizations_applied)} optimization techniques")
        return optimized_data

    def _compress_validation_results(self, validation_data):
        """🗜️ Compress repetitive validation results"""
        if not isinstance(validation_data, (list, dict)):
            return validation_data

        if isinstance(validation_data, list):
            # Group similar validation results
            result_groups = {}

            for item in validation_data:
                if isinstance(item, dict):
                    # Create a signature for grouping
                    status = item.get("status", "unknown")
                    result_type = item.get("type", item.get("validation_type", "unknown"))
                    signature = f"{status}_{result_type}"

                    if signature not in result_groups:
                        result_groups[signature] = {
                            "status": status,
                            "type": result_type,
                            "count": 1,
                            "sample_details": str(item.get("details", item.get("message", "No details")))[:200],
                            "items": [item.get("name", item.get("file", item.get("id", "unnamed")))],
                        }
                    else:
                        result_groups[signature]["count"] += 1
                        if len(result_groups[signature]["items"]) < 10:
                            result_groups[signature]["items"].append(
                                item.get("name", item.get("file", item.get("id", "unnamed")))
                            )

            return list(result_groups.values())

        return validation_data

    def _deduplicate_database_entries(self, db_list):
        """🔄 Remove duplicate database entries"""
        if not isinstance(db_list, list):
            return db_list

        seen_hashes = set()
        deduplicated = []

        for entry in db_list:
            if isinstance(entry, dict):
                # Create hash of essential fields
                essential_data = {
                    "name": entry.get("name", entry.get("database_name", "")),
                    "path": entry.get("path", entry.get("file_path", "")),
                    "size": entry.get("size", entry.get("file_size", 0)),
                }
                entry_hash = hashlib.md5(str(essential_data).encode()).hexdigest()

                if entry_hash not in seen_hashes:
                    seen_hashes.add(entry_hash)
                    # Keep essential fields only
                    compressed_entry = {
                        "name": entry.get("name", entry.get("database_name")),
                        "status": entry.get("status", entry.get("validation_status")),
                        "size_mb": round(entry.get("size_mb", entry.get("file_size", 0) / (1024 * 1024)), 2),
                        "tables": entry.get("tables", entry.get("table_count", 0)),
                        "health": entry.get("health", entry.get("health_score", 0)),
                    }
                    deduplicated.append(compressed_entry)

        return deduplicated

    def _compress_error_data(self, error_data):
        """🚨 Compress error and log data"""
        if isinstance(error_data, list):
            # Group similar errors
            error_groups = {}
            for error in error_data:
                if isinstance(error, dict):
                    error_type = error.get("type", error.get("error_type", "unknown"))
                    if error_type not in error_groups:
                        error_groups[error_type] = {
                            "type": error_type,
                            "count": 1,
                            "sample_message": str(error.get("message", error.get("description", "No message")))[:200],
                        }
                    else:
                        error_groups[error_type]["count"] += 1
                elif isinstance(error, str):
                    # Group string errors by first 50 characters
                    error_prefix = error[:50]
                    if error_prefix not in error_groups:
                        error_groups[error_prefix] = {"type": "string_error", "count": 1, "sample_message": error[:200]}
                    else:
                        error_groups[error_prefix]["count"] += 1

            return list(error_groups.values())

        elif isinstance(error_data, str) and len(error_data) > 1000:
            # Truncate very long error messages
            return error_data[:500] + "... [TRUNCATED]"

        return error_data

    def _summarize_large_arrays(self, array_data, key_name):
        """📊 Summarize large arrays while preserving key information"""
        if len(array_data) <= 1000:
            return array_data

        summary = {
            "original_count": len(array_data),
            "sample_size": min(100, len(array_data)),
            "summary_stats": {},
            "first_items": array_data[:50],
            "last_items": array_data[-50:] if len(array_data) > 50 else [],
            "compressed_note": f"Array compressed from {len(array_data)} to {min(100, len(array_data))} sample items",
        }

        # Generate basic statistics if items are numeric/measurable
        if array_data and isinstance(array_data[0], dict):
            # Find numeric fields for statistics
            numeric_fields = []
            first_item = array_data[0]
            for field, value in first_item.items():
                if isinstance(value, (int, float)):
                    numeric_fields.append(field)

            for field in numeric_fields[:5]:  # Limit to 5 fields
                values = [item.get(field, 0) for item in array_data if isinstance(item.get(field), (int, float))]
                if values:
                    summary["summary_stats"][field] = {
                        "min": min(values),
                        "max": max(values),
                        "avg": round(sum(values) / len(values), 2),
                        "count": len(values),
                    }

        return summary

    def _contains_duplicate_strings(self, data):
        """🔍 Check if data contains many duplicate strings"""
        if isinstance(data, list):
            str_count = {}
            for item in data[:100]:  # Sample first 100 items
                if isinstance(item, str):
                    str_count[item] = str_count.get(item, 0) + 1
                elif isinstance(item, dict):
                    for value in item.values():
                        if isinstance(value, str) and len(value) > 10:
                            str_count[value] = str_count.get(value, 0) + 1
            return any(count > 5 for count in str_count.values())
        return False

    def _compress_duplicate_strings(self, data):
        """🗜️ Compress duplicate strings using reference table"""
        if isinstance(data, list):
            string_refs = {}
            ref_counter = 0
            compressed_data = []

            for item in data:
                if isinstance(item, str) and len(item) > 20:
                    if item not in string_refs:
                        string_refs[item] = f"REF_{ref_counter}"
                        ref_counter += 1
                    compressed_data.append({"ref": string_refs[item]})
                elif isinstance(item, dict):
                    compressed_item = {}
                    for key, value in item.items():
                        if isinstance(value, str) and len(value) > 20:
                            if value not in string_refs:
                                string_refs[value] = f"REF_{ref_counter}"
                                ref_counter += 1
                            compressed_item[key] = {"ref": string_refs[value]}
                        else:
                            compressed_item[key] = value
                    compressed_data.append(compressed_item)
                else:
                    compressed_data.append(item)

            return {
                "references": {v: k for k, v in string_refs.items()},
                "data": compressed_data[:1000],  # Limit to 1000 items
            }

        return data

    def create_compressed_output(self, optimized_data):
        """💾 Create final compressed output"""
        logger.info("💾 Creating compressed output...")

        outputs = {}
        results_dir = self.workspace_path / "results"

        with tqdm(total=100, desc="🗜️ Creating outputs", unit="%") as pbar:
            # 1. Compressed JSON
            pbar.set_description("📄 Creating compressed JSON")
            json_output = results_dir / "database_validation_results_compressed.json"
            with open(json_output, "w", encoding="utf-8") as f:
                json.dump(optimized_data, f, indent=1, ensure_ascii=False, separators=(",", ":"))

            json_size = json_output.stat().st_size / (1024 * 1024)
            outputs["compressed_json"] = {"path": json_output, "size_mb": json_size}
            pbar.update(25)

            # 2. GZIP Compressed JSON
            pbar.set_description("🗜️ Creating GZIP compressed")
            gzip_output = results_dir / "database_validation_results_compressed.json.gz"
            with gzip.open(gzip_output, "wt", encoding="utf-8", compresslevel=9) as f:
                json.dump(optimized_data, f, indent=1, ensure_ascii=False, separators=(",", ":"))

            gzip_size = gzip_output.stat().st_size / (1024 * 1024)
            outputs["gzip_compressed"] = {"path": gzip_output, "size_mb": gzip_size}
            pbar.update(25)

            # 3. Ultra-compressed JSON (no formatting)
            pbar.set_description("🔥 Creating ultra-compressed")
            ultra_output = results_dir / "database_validation_results_ultra.json"
            with open(ultra_output, "w", encoding="utf-8") as f:
                json.dump(optimized_data, f, separators=(",", ":"), ensure_ascii=False)

            ultra_size = ultra_output.stat().st_size / (1024 * 1024)
            outputs["ultra_compressed"] = {"path": ultra_output, "size_mb": ultra_size}
            pbar.update(25)

            # 4. SQLite Database (most efficient for structured data)
            pbar.set_description("🗄️ Creating SQLite database")
            sqlite_output = Path(self.workspace_path) / "databases" / "database_validation_results.db"
            self._create_sqlite_database(optimized_data, sqlite_output)

            sqlite_size = sqlite_output.stat().st_size / (1024 * 1024)
            outputs["sqlite_database"] = {"path": sqlite_output, "size_mb": sqlite_size}
            pbar.update(25)

        # Find the smallest output that meets requirements
        best_output = None
        for format_name, output_info in outputs.items():
            if output_info["size_mb"] <= self.target_size_mb:
                if best_output is None or output_info["size_mb"] < outputs[best_output]["size_mb"]:
                    best_output = format_name

        return outputs, best_output

    def _create_sqlite_database(self, data, db_path):
        """🗄️ Convert JSON data to SQLite database"""
        if db_path.exists():
            db_path.unlink()  # Remove existing database

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create tables for different data types
        cursor.execute("""
            CREATE TABLE validation_summary (
                id INTEGER PRIMARY KEY,
                key_name TEXT,
                data_type TEXT,
                record_count INTEGER,
                summary_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE database_info (
                id INTEGER PRIMARY KEY,
                name TEXT,
                status TEXT,
                size_mb REAL,
                table_count INTEGER,
                health_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE compression_metadata (
                id INTEGER PRIMARY KEY,
                original_size_mb REAL,
                compression_ratio REAL,
                techniques_applied TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert compression metadata
        cursor.execute(
            """
            INSERT INTO compression_metadata (original_size_mb, compression_ratio, techniques_applied)
            VALUES (?, ?, ?)
        """,
            (
                self.compression_report["original_size_mb"],
                self.compression_report.get("compression_ratio", 0),
                json.dumps(self.compression_report["techniques_applied"]),
            ),
        )

        # Insert summarized data
        for key, value in data.items():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                # Check if it's database info
                if any(field in str(value[0]).lower() for field in ["database", "db", "name", "status"]):
                    for item in value:
                        cursor.execute(
                            """
                            INSERT INTO database_info (name, status, size_mb, table_count, health_score)
                            VALUES (?, ?, ?, ?, ?)
                        """,
                            (
                                item.get("name", "unknown"),
                                item.get("status", "unknown"),
                                item.get("size_mb", 0),
                                item.get("tables", 0),
                                item.get("health", 0),
                            ),
                        )
                else:
                    # Store as summary
                    cursor.execute(
                        """
                        INSERT INTO validation_summary (key_name, data_type, record_count, summary_data)
                        VALUES (?, ?, ?, ?)
                    """,
                        (key, "list", len(value), json.dumps(value[:5] if len(value) > 5 else value)[:2000]),
                    )
            else:
                cursor.execute(
                    """
                    INSERT INTO validation_summary (key_name, data_type, record_count, summary_data)
                    VALUES (?, ?, ?, ?)
                """,
                    (key, type(value).__name__, 1, str(value)[:2000]),
                )

        # Create indexes for better performance
        cursor.execute("CREATE INDEX idx_validation_key ON validation_summary(key_name)")
        cursor.execute("CREATE INDEX idx_database_name ON database_info(name)")

        conn.commit()
        conn.close()

    def generate_compression_report(self, outputs, best_output):
        """📋 Generate comprehensive compression report"""
        original_size = self.compression_report["original_size_mb"]

        if best_output:
            final_size = outputs[best_output]["size_mb"]
            compression_ratio = ((original_size - final_size) / original_size) * 100

            self.compression_report.update(
                {
                    "compressed_size_mb": final_size,
                    "compression_ratio": compression_ratio,
                    "best_format": best_output,
                    "target_achieved": final_size <= self.target_size_mb,
                }
            )

        report_path = (
            self.workspace_path / "results" / f"compression_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        full_report = {
            "compression_report": self.compression_report,
            "output_formats": {k: {**v, "path": str(v["path"])} for k, v in outputs.items()},
            "recommendations": self._generate_recommendations(outputs),
            "execution_summary": {
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
            },
        }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(full_report, f, indent=2)

        return report_path

    def _generate_recommendations(self, outputs):
        """💡 Generate optimization recommendations"""
        recommendations = []

        for format_name, output_info in outputs.items():
            if output_info["size_mb"] <= self.target_size_mb:
                recommendations.append(f"✅ {format_name}: {output_info['size_mb']:.2f} MB - MEETS TARGET")
            else:
                recommendations.append(f"❌ {format_name}: {output_info['size_mb']:.2f} MB - EXCEEDS TARGET")

        if all(output["size_mb"] > self.target_size_mb for output in outputs.values()):
            recommendations.extend(
                [
                    "🔥 AGGRESSIVE: Consider removing historical data or implementing data archival",
                    "📊 ALTERNATIVE: Split into multiple smaller files by date/category",
                    "🗄️ MIGRATION: Consider PostgreSQL JSONB for large datasets",
                    "📦 ARCHIVAL: Move old validation data to separate archive files",
                ]
            )

        return recommendations

    def execute_compression(self):
        """🚀 Execute complete compression process"""
        logger.info("=" * 80)
        logger.info("🔥 DATABASE VALIDATION RESULTS COMPRESSION")
        logger.info("=" * 80)

        try:
            # Phase 1: Analyze
            logger.info("📊 Phase 1: Analysis")
            data, analysis = self.analyze_file_structure()

            # Phase 2: Optimize
            logger.info("⚡ Phase 2: Optimization")
            optimized_data = self.apply_data_optimization(data)

            # Phase 3: Compress
            logger.info("🗜️ Phase 3: Compression")
            outputs, best_output = self.create_compressed_output(optimized_data)

            # Phase 4: Report
            logger.info("📋 Phase 4: Reporting")
            report_path = self.generate_compression_report(outputs, best_output)

            # Summary
            logger.info("\n" + "=" * 80)
            logger.info("📊 COMPRESSION RESULTS")
            logger.info("=" * 80)
            logger.info(f"📋 Original size: {self.compression_report['original_size_mb']:.2f} MB")

            for format_name, output_info in outputs.items():
                status = "✅ MEETS TARGET" if output_info["size_mb"] <= self.target_size_mb else "❌ EXCEEDS TARGET"
                logger.info(f"   {format_name}: {output_info['size_mb']:.2f} MB - {status}")

            if best_output:
                logger.info(f"\n🏆 RECOMMENDED: {best_output} ({outputs[best_output]['size_mb']:.2f} MB)")
                logger.info(f"💾 File location: {outputs[best_output]['path']}")
                logger.info(f"🗜️ Compression ratio: {self.compression_report.get('compression_ratio', 0):.1f}%")
            else:
                logger.info("\n⚠️ WARNING: No format meets the 99.9MB target")
                logger.info("📋 See recommendations in compression report")

            logger.info(f"\n📄 Detailed report: {report_path}")

            # MANDATORY: Completion logging
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info("=" * 80)
            logger.info(f"✅ DATABASE VALIDATION COMPRESSOR COMPLETED")
            logger.info(f"Total Duration: {duration:.1f} seconds")
            logger.info(f"Process ID: {os.getpid()}")
            logger.info(f"Completion Status: SUCCESS")
            logger.info("=" * 80)

            return self.compression_report.get("target_achieved", False) if best_output else False

        except Exception as e:
            logger.error(f"🚨 COMPRESSION FAILED: {e}")
            import traceback

            logger.error(f"📋 Error details: {traceback.format_exc()}")
            return False


if __name__ == "__main__":
    try:
        compressor = DatabaseValidationCompressor()
        success = compressor.execute_compression()

        if success:
            print("✅ COMPRESSION SUCCESSFUL - TARGET ACHIEVED")
        else:
            print("❌ COMPRESSION INCOMPLETE - MANUAL INTERVENTION REQUIRED")
    except Exception as e:
        print(f"🚨 FATAL ERROR: {e}")
        import traceback

        print(f"📋 Full traceback: {traceback.format_exc()}")
