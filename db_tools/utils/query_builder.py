"""
Database query builder utilities.
"""

from typing import List, Dict, Any


class QueryBuilder:
    """SQL query builder for common database operations"""

    @staticmethod
    def select(table: str, columns: List[str] = None, where: Dict[str, Any] = None,
               order_by: str = None, limit: int = None) -> tuple:
        """Build SELECT query with parameters"""

        # Handle columns
        if columns is None:
            columns_str = "*"
        else:
            columns_str = ", ".join(columns)

        query = f"SELECT {columns_str} FROM {table}"
        params = []

        # Handle WHERE clause
        if where:
            where_clauses = []
            for column, value in where.items():
                where_clauses.append(f"{column} = ?")
                params.append(value)
            query += " WHERE " + " AND ".join(where_clauses)

        # Handle ORDER BY
        if order_by:
            query += f" ORDER BY {order_by}"

        # Handle LIMIT
        if limit:
            query += f" LIMIT {limit}"

        return query, tuple(params)

    @staticmethod
    def insert(table: str, data: Dict[str, Any]) -> tuple:
        """Build INSERT query with parameters"""
        columns = list(data.keys())
        placeholders = ", ".join(["?"] * len(columns))

        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        params = tuple(data.values())

        return query, params

    @staticmethod
    def update(table: str, data: Dict[str, Any], where: Dict[str, Any]) -> tuple:
        """Build UPDATE query with parameters"""
        set_clauses = []
        params = []

        # Handle SET clause
        for column, value in data.items():
            set_clauses.append(f"{column} = ?")
            params.append(value)

        query = f"UPDATE {table} SET {', '.join(set_clauses)}"

        # Handle WHERE clause
        if where:
            where_clauses = []
            for column, value in where.items():
                where_clauses.append(f"{column} = ?")
                params.append(value)
            query += " WHERE " + " AND ".join(where_clauses)

        return query, tuple(params)

    @staticmethod
    def delete(table: str, where: Dict[str, Any]) -> tuple:
        """Build DELETE query with parameters"""
        params = []
        where_clauses = []

        for column, value in where.items():
            where_clauses.append(f"{column} = ?")
            params.append(value)

        query = f"DELETE FROM {table} WHERE {' AND '.join(where_clauses)}"

        return query, tuple(params)
