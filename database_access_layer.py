
class DatabaseAccessLayer:
    """🌉 Cross-Database Access Layer for Documentation and Logs"""

    def __init__(self, docs_db_path: str, logs_db_path: str):
        self.docs_db = docs_db_path
        self.logs_db = logs_db_path

    def get_unified_search(self, search_term: str, include_logs: bool = True):
        """🔍 Search across both databases"""
        results = {"documentation": [], "logs": []}

        # Search documentation
        with sqlite3.connect(self.docs_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT title, doc_type, category, last_updated
                FROM enterprise_documentation
                WHERE title LIKE ? OR content LIKE ?
                ORDER BY last_updated DESC
            """, (f"%{search_term}%", f"%{search_term}%"))
            results["documentation"] = cursor.fetchall()

        # Search logs if requested
        if include_logs:
            with sqlite3.connect(self.logs_db) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT title, log_level, component, last_updated
                    FROM enterprise_logs
                    WHERE title LIKE ? OR content LIKE ?
                    ORDER BY last_updated DESC
                """, (f"%{search_term}%", f"%{search_term}%"))
                results["logs"] = cursor.fetchall()

        return results

    def get_comprehensive_metrics(self):
        """📊 Get metrics from both databases"""
        metrics = {}

        # Documentation metrics
        with sqlite3.connect(self.docs_db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                           "SELECT doc_type,
                           COUNT(*) FROM enterprise_documentation GROUP BY doc_type"
            cursor.execute("SELECT doc)
            metrics["documentation"] = dict(cursor.fetchall())

        # Logs metrics
        with sqlite3.connect(self.logs_db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                           "SELECT category,
                           COUNT(*) FROM enterprise_logs GROUP BY category"
            cursor.execute("SELECT cat)
            metrics["logs"] = dict(cursor.fetchall())

        return metrics
