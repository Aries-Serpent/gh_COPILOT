#!/usr/bin/env python3
"""
🧹 DOCUMENTATION DATABASE COMPREHENSIVE CLEANUP & ANALYSIS
Enterprise Database Consolidation and Modularization System
Version: 2.0.0
"""

import sqlite3

import json

from pathlib import Path
from datetime import datetime


import logging
import re

# Configure logging
logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig)
logger = logging.getLogger(__name__)


class DocumentationDatabaseCleanup:
    """🧹 Comprehensive Documentation Database Cleanup and Analysis"""

    def __init__(self, workspace_path: str = "e:/gh_COPILOT"):
        self.start_time = datetime.now()
        self.workspace_path = Path(workspace_path)
        self.db_path = self.workspace_path / "databases" / "documentation.db"
        self.backup_path = self.workspace_path / "databases" / f"documentation_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

        # Analysis results
        self.analysis_results = {
            "duplicates_found": {},
            "backup_files_removed": [],
            "convo_files_removed": [],
            "consolidation_opportunities": {},
            "modularization_suggestions": {},
            "statistics": {},
            "cleanup_summary": {}
        }

        logger.info("🚀 Documentation Database Cleanup Started")
        logger.info(f"Database: {self.db_path}")

    def perform_comprehensive_cleanup(self) -> Dict[str, Any]:
        """🧹 Execute comprehensive cleanup and analysis"""

        try:
            # Step 1: Create backup
            logger.info("📋 Step 1: Creating database backup")
            self._create_backup()

            # Step 2: Connect to database
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row

            # Step 3: Analyze current state
            logger.info("📊 Step 2: Analyzing current database state")
            self._analyze_current_state(conn)

            # Step 4: Remove backup files
            logger.info("🗑️ Step 3: Removing backup files")
            self._remove_backup_files(conn)

            # Step 5: Remove conversation files
            logger.info("🗑️ Step 4: Removing conversation files")
            self._remove_conversation_files(conn)

            # Step 6: Identify and consolidate duplicates
            logger.info("🔄 Step 5: Consolidating duplicates")
            self._consolidate_duplicates(conn)

            # Step 7: Analyze modularization opportunities
            logger.info("🧩 Step 6: Analyzing modularization opportunities")
            self._analyze_modularization(conn)

            # Step 8: Generate final statistics
            logger.info("📈 Step 7: Generating final statistics")
            self._generate_final_statistics(conn)

            # Step 9: Vacuum database
            logger.info("🔧 Step 8: Optimizing database")
            conn.execute("VACUUM")

            conn.close()

            # Step 10: Generate report
            logger.info("📄 Step 9: Generating cleanup report")
            self._generate_cleanup_report()

            logger.info("✅ Comprehensive cleanup completed successfully")
            return self.analysis_results

        except Exception as e:
            logger.error(f"❌ Cleanup failed: {str(e)}")
            raise

    def _create_backup(self):
        """📋 Create database backup before cleanup"""
        import shutil
        shutil.copy2(self.db_path, self.backup_path)
        logger.info(f"✅ Backup created: {self.backup_path}")

    def _analyze_current_state(self, conn: sqlite3.Connection):
        """📊 Analyze current database state"""
        cursor = conn.cursor()

        # Get total document count
        cursor.execute("SELECT COUNT(*) FROM enterprise_documentation")
        total_docs = cursor.fetchone()[0]

        # Get document types breakdown
        cursor.execute("""
            SELECT doc_type, COUNT(*) as count
            FROM enterprise_documentation
            GROUP BY doc_type
            ORDER BY count DESC
        """)
        doc_types = dict(cursor.fetchall())

        # Get size analysis
        cursor.execute("""
            SELECT
                AVG(LENGTH(content)) as avg_content_length,
                MAX(LENGTH(content)) as max_content_length,
                MIN(LENGTH(content)) as min_content_length
            FROM enterprise_documentation
        """)
        size_stats = dict(cursor.fetchone())

        self.analysis_results["statistics"]["initial"] = {
            "total_documents": total_docs,
            "document_types": doc_types,
            "content_size_stats": size_stats
        }

        logger.info(f"📊 Initial analysis: {total_docs} documents")
        for doc_type, count in doc_types.items():
            logger.info(f"  - {doc_type}: {count}")

    def _remove_backup_files(self, conn: sqlite3.Connection):
        """🗑️ Remove backup files from database"""
        cursor = conn.cursor()

        # Find backup files
        cursor.execute("""
            SELECT doc_id, title, source_path
            FROM enterprise_documentation
            WHERE
                title LIKE '%backup%' OR
                title LIKE '%_backup' OR
                source_path LIKE '%backup%' OR
                source_path LIKE '%_backup%' OR
                doc_type = 'BACKUP_LOG'
        """)

        backup_files = cursor.fetchall()
        backup_ids = [row[0] for row in backup_files]

        if backup_files:
            logger.info(f"🗑️ Found {len(backup_files)} backup files to remove")

            # Remove from analytics first (foreign key constraint)
            if backup_ids:
                placeholders = ','.join(['?' for _ in backup_ids])
                cursor.execute(f"""
                    DELETE FROM documentation_analytics
                    WHERE doc_id IN ({placeholders})
                """, backup_ids)

                # Remove backup files
                cursor.execute(f"""
                    DELETE FROM enterprise_documentation
                    WHERE doc_id IN ({placeholders})
                """, backup_ids)

                conn.commit()

                self.analysis_results["backup_files_removed"] = [
                    {"doc_id": row[0], "title": row[1], "source_path": row[2]}
                    for row in backup_files
                ]

                logger.info(f"✅ Removed {len(backup_files)} backup files")
        else:
            logger.info("ℹ️ No backup files found")

    def _remove_conversation_files(self, conn: sqlite3.Connection):
        """🗑️ Remove conversation files from database"""
        cursor = conn.cursor()

        # Find conversation files
        cursor.execute("""
            SELECT doc_id, title, source_path
            FROM enterprise_documentation
            WHERE
                title LIKE '%_convo%' OR
                title LIKE '%convo_%' OR
                source_path LIKE '%_convo.md' OR
                source_path LIKE '%convo_%'
        """)

        convo_files = cursor.fetchall()
        convo_ids = [row[0] for row in convo_files]

        if convo_files:
            logger.info(f"🗑️ Found {len(convo_files)} conversation files to remove")

            # Remove from analytics first
            if convo_ids:
                placeholders = ','.join(['?' for _ in convo_ids])
                cursor.execute(f"""
                    DELETE FROM documentation_analytics
                    WHERE doc_id IN ({placeholders})
                """, convo_ids)

                # Remove conversation files
                cursor.execute(f"""
                    DELETE FROM enterprise_documentation
                    WHERE doc_id IN ({placeholders})
                """, convo_ids)

                conn.commit()

                self.analysis_results["convo_files_removed"] = [
                    {"doc_id": row[0], "title": row[1], "source_path": row[2]}
                    for row in convo_files
                ]

                logger.info(f"✅ Removed {len(convo_files)} conversation files")
        else:
            logger.info("ℹ️ No conversation files found")

    def _consolidate_duplicates(self, conn: sqlite3.Connection):
        """🔄 Identify and consolidate duplicate documents"""
        cursor = conn.cursor()

        # Find duplicates by title
        cursor.execute("""
            SELECT title, COUNT(*) as duplicate_count,
                   GROUP_CONCAT(doc_id) as doc_ids,
                   GROUP_CONCAT(doc_type) as doc_types,
                   GROUP_CONCAT(last_updated) as update_times
            FROM enterprise_documentation
            GROUP BY title
            HAVING COUNT(*) > 1
            ORDER BY duplicate_count DESC
        """)

        title_duplicates = cursor.fetchall()
        duplicates_consolidated = 0

        for row in title_duplicates:
            title = row[0]
            duplicate_count = row[1]
            doc_ids = row[2].split(',')
            doc_types = row[3].split(',')
            update_times = row[4].split(',')

            logger.info(f"🔄 Processing duplicates for '{title}': {duplicate_count} copies")

            # Keep the most recent non-backup version
            best_doc_id = None
            best_timestamp = None

            for i, doc_id in enumerate(doc_ids):
                if doc_types[i] != 'BACKUP_LOG':
                    if best_timestamp is None or update_times[i] > best_timestamp:
                        best_doc_id = doc_id
                        best_timestamp = update_times[i]

            # If no non-backup found, keep the most recent
            if best_doc_id is None:
                best_doc_id = doc_ids[0]
                best_timestamp = update_times[0]
                for i, timestamp in enumerate(update_times):
                    if timestamp > best_timestamp:
                        best_doc_id = doc_ids[i]
                        best_timestamp = timestamp

            # Remove duplicates (keep the best one)
            docs_to_remove = [doc_id for doc_id in doc_ids if doc_id != best_doc_id]

            if docs_to_remove:
                placeholders = ','.join(['?' for _ in docs_to_remove])

                # Remove from analytics first
                cursor.execute(f"""
                    DELETE FROM documentation_analytics
                    WHERE doc_id IN ({placeholders})
                """, docs_to_remove)

                # Remove duplicates
                cursor.execute(f"""
                    DELETE FROM enterprise_documentation
                    WHERE doc_id IN ({placeholders})
                """, docs_to_remove)

                duplicates_consolidated += len(docs_to_remove)

                self.analysis_results["duplicates_found"][title] = {
                    "total_copies": duplicate_count,
                    "removed_copies": len(docs_to_remove),
                    "kept_doc_id": best_doc_id,
                    "removed_doc_ids": docs_to_remove
                }

        conn.commit()
        logger.info(f"✅ Consolidated {duplicates_consolidated} duplicate documents")

    def _analyze_modularization(self, conn: sqlite3.Connection):
        """🧩 Analyze modularization opportunities"""
        cursor = conn.cursor()

        # Group similar documents by patterns
        cursor.execute("""
            SELECT doc_type,
                   COUNT(*) as count,
                   AVG(LENGTH(content)) as avg_length,
                   GROUP_CONCAT(SUBSTR(title, 1, 50)) as sample_titles
            FROM enterprise_documentation
            GROUP BY doc_type
            HAVING count > 5
            ORDER BY count DESC
        """)

        modular_opportunities = cursor.fetchall()

        for row in modular_opportunities:
            doc_type = row[0]
            count = row[1]
            avg_length = row[2]
            sample_titles = row[3]

            # Analyze common patterns in titles
            cursor.execute("""
                SELECT title FROM enterprise_documentation
                WHERE doc_type = ?
                ORDER BY title
            """, (doc_type,))

            titles = [row[0] for row in cursor.fetchall()]

            # Find common prefixes/suffixes
            common_patterns = self._find_common_patterns(titles)

            self.analysis_results["modularization_suggestions"][doc_type] = {
                "document_count": count,
                "average_content_length": avg_length,
                "common_patterns": common_patterns,
                "modularity_potential": "HIGH" if count > 20 else "MEDIUM" if count > 10 else "LOW",
                "recommended_actions": self._generate_modular_recommendations(
                                                                              doc_type,
                                                                              count,
                                                                              common_patterns
                "recommended_actions": self._generate_modular_recommendations(doc_type, count)
            }

        logger.info(f"📊 Analyzed {len(modular_opportunities)} document types for modularization")

    def _find_common_patterns(self, titles: List[str]) -> Dict[str, Any]:
        """🔍 Find common patterns in document titles"""
        if not titles:
            return {}

        # Find common prefixes
        prefixes = Counter()
        suffixes = Counter()
        keywords = Counter()

        for title in titles:
            # Split title into words
            words = re.split(r'[_\-\s]+', title.lower())

            # Count prefixes (first 2 words)
            if len(words) >= 2:
                prefix = '_'.join(words[:2])
                prefixes[prefix] += 1

            # Count suffixes (last 2 words)
            if len(words) >= 2:
                suffix = '_'.join(words[-2:])
                suffixes[suffix] += 1

            # Count all keywords
            for word in words:
                if len(word) > 3:  # Ignore short words
                    keywords[word] += 1

        return {
            "common_prefixes": dict(prefixes.most_common(5)),
            "common_suffixes": dict(suffixes.most_common(5)),
            "frequent_keywords": dict(keywords.most_common(10))
        }

    def _generate_modular_recommendations(
                                          self,
                                          doc_type: str,
                                          count: int,
                                          patterns: Dict) -> List[str]
    def _generate_modular_recommendations(sel)
        """💡 Generate modularization recommendations"""
        recommendations = []

        if count > 50:
            recommendations.append("Consider creating template-based generation system")
            recommendations.append("Implement content inheritance for common sections")

        if count > 20:
            recommendations.append("Create base templates for common document structures")
            recommendations.append("Implement automated content updates")

        if patterns.get("common_prefixes"):
            recommendations.append("Group documents by common prefixes into modules")

        if patterns.get("frequent_keywords"):
            top_keyword = max(
                              patterns["frequent_keywords"],
                              key=patterns["frequent_keywords"].get
            top_keyword = max(patterns["f)
            recommendations.append(f"Create specialized module for '{top_keyword}' related documents")

        return recommendations

    def _generate_final_statistics(self, conn: sqlite3.Connection):
        """📈 Generate final cleanup statistics"""
        cursor = conn.cursor()

        # Get final document count
        cursor.execute("SELECT COUNT(*) FROM enterprise_documentation")
        final_total = cursor.fetchone()[0]

        # Get final document types
        cursor.execute("""
            SELECT doc_type, COUNT(*) as count
            FROM enterprise_documentation
            GROUP BY doc_type
            ORDER BY count DESC
        """)
        final_doc_types = dict(cursor.fetchall())

        initial_total = self.analysis_results["statistics"]["initial"]["total_documents"]
        documents_removed = initial_total - final_total

        self.analysis_results["statistics"]["final"] = {
            "total_documents": final_total,
            "document_types": final_doc_types,
            "documents_removed": documents_removed,
            "removal_percentage": (documents_removed / initial_total) * 100 if initial_total > 0 else 0
        }

        logger.info("📈 Final statistics:")
        logger.info(f"  - Documents removed: {documents_removed}")
        logger.info(f"  - Final document count: {final_total}")
        logger.info(f"  - Reduction: {(documents_removed / initial_total) * 100:.1f}%")

    def _generate_cleanup_report(self):
        """📄 Generate comprehensive cleanup report"""
        report_path = self.workspace_path / f"documentation_cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Add execution metadata
        self.analysis_results["cleanup_summary"] = {
            "execution_time": str(datetime.now() - self.start_time),
            "timestamp": datetime.now().isoformat(),
            "database_path": str(self.db_path),
            "backup_path": str(self.backup_path),
            "report_path": str(report_path)
        }

        # Write report
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(
                      self.analysis_results,
                      f,
                      indent=2,
                      ensure_ascii=False,
                      default=str
            json.dump(self.analys)

        logger.info(f"📄 Cleanup report saved: {report_path}")

        # Generate human-readable summary
        self._print_cleanup_summary()

    def _print_cleanup_summary(self):
        """📋 Print human-readable cleanup summary"""
        print("\n" + "="*80)
        print("🧹 DOCUMENTATION DATABASE CLEANUP SUMMARY")
        print("="*80)

        initial = self.analysis_results["statistics"]["initial"]
        final = self.analysis_results["statistics"]["final"]

        print("📊 STATISTICS:")
        print(f"  Initial documents: {initial['total_documents']}")
        print(f"  Final documents: {final['total_documents']}")
        print(f"  Documents removed: {final['documents_removed']}")
        print(f"  Reduction: {final['removal_percentage']:.1f}%")

        print("\n🗑️ CLEANUP ACTIONS:")
        print(f"  Backup files removed: {len(self.analysis_results['backup_files_removed'])}")
        print(f"  Conversation files removed: {len(self.analysis_results['convo_files_removed'])}")
        print(f"  Duplicate sets consolidated: {len(self.analysis_results['duplicates_found'])}")

        print("\n🧩 MODULARIZATION OPPORTUNITIES:")
        for doc_type, info in self.analysis_results["modularization_suggestions"].items():
            potential = info["modularity_potential"]
            count = info["document_count"]
            print(f"  {doc_type}: {count} docs - {potential} modularity potential")

        print("\n✅ CLEANUP COMPLETED SUCCESSFULLY")
        print(f"   Execution time: {self.analysis_results['cleanup_summary']['execution_time']}")
        print("="*80)


def main():
    """🚀 Main execution function"""
    try:
        cleanup = DocumentationDatabaseCleanup()
        results = cleanup.perform_comprehensive_cleanup()
        return results
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
