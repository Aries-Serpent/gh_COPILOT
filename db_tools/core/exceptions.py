"""
Custom database exceptions for the db_tools package.
"""


class DatabaseError(Exception):
    """Base database error"""
    pass


class DatabaseConnectionError(DatabaseError):
    """Database connection error"""
    pass


class DatabaseQueryError(DatabaseError):
    """Database query execution error"""
    pass


class DatabaseValidationError(DatabaseError):
    """Database validation error"""
    pass