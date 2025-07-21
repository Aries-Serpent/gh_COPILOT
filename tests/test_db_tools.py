"""
Tests for the db_tools package.
"""

import tempfile
import sqlite3
from pathlib import Path

from db_tools.core.connection import DatabaseConnection
from db_tools.core.models import DatabaseConfig
from db_tools.operations.access import DatabaseAccessLayer
from db_tools.operations.cleanup import DatabaseCleanupProcessor
from db_tools.operations.compliance import DatabaseComplianceChecker
from db_tools.utils.query_builder import QueryBuilder
from db_tools.utils.validators import DataValidator


class TestDatabaseConnection:
    """Test database connection functionality"""
    
    def test_connection_with_string_path(self):
        """Test connection creation with string path"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        conn = DatabaseConnection(db_path)
        assert conn.config.database_path == Path(db_path)
    
    def test_connection_with_config(self):
        """Test connection creation with config object"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        config = DatabaseConfig(database_path=Path(db_path))
        conn = DatabaseConnection(config)
        assert conn.config.database_path == Path(db_path)
    
    def test_execute_query_select(self):
        """Test executing SELECT query"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        # Create test table
        with sqlite3.connect(db_path) as conn:
            conn.execute("CREATE TABLE test (id INTEGER, name TEXT)")
            conn.execute("INSERT INTO test VALUES (1, 'test')")
            conn.commit()
        
        db_conn = DatabaseConnection(db_path)
        result = db_conn.execute_query("SELECT * FROM test")
        assert len(result) == 1
        assert result[0]['name'] == 'test'
    
    def test_execute_query_insert(self):
        """Test executing INSERT query"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        # Create test table
        with sqlite3.connect(db_path) as conn:
            conn.execute("CREATE TABLE test (id INTEGER, name TEXT)")
            conn.commit()
        
        db_conn = DatabaseConnection(db_path)
        row_count = db_conn.execute_query("INSERT INTO test VALUES (?, ?)", (1, 'test'))
        assert row_count == 1
    
    def test_table_exists(self):
        """Test table existence checking"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        # Create test table
        with sqlite3.connect(db_path) as conn:
            conn.execute("CREATE TABLE test (id INTEGER)")
            conn.commit()
        
        db_conn = DatabaseConnection(db_path)
        assert db_conn.table_exists('test') is True
        assert db_conn.table_exists('nonexistent') is False


class TestDatabaseAccessLayer:
    """Test database access layer functionality"""
    
    def test_initialization(self):
        """Test access layer initialization"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        access_layer = DatabaseAccessLayer(db_path)
        assert access_layer.database_path == Path(db_path)
    
    def test_execute_processing(self):
        """Test processing execution"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        access_layer = DatabaseAccessLayer(db_path)
        result = access_layer.execute_processing()
        assert result is True
    
    def test_get_tables_info(self):
        """Test getting tables information"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        # Create test table
        with sqlite3.connect(db_path) as conn:
            conn.execute("CREATE TABLE test (id INTEGER)")
            conn.commit()
        
        access_layer = DatabaseAccessLayer(db_path)
        tables = access_layer.get_tables_info()
        assert 'test' in tables
    
    def test_get_table_row_count(self):
        """Test getting table row count"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        # Create test table with data
        with sqlite3.connect(db_path) as conn:
            conn.execute("CREATE TABLE test (id INTEGER)")
            conn.execute("INSERT INTO test VALUES (1)")
            conn.execute("INSERT INTO test VALUES (2)")
            conn.commit()
        
        access_layer = DatabaseAccessLayer(db_path)
        count = access_layer.get_table_row_count('test')
        assert count == 2
        
        # Test nonexistent table
        count = access_layer.get_table_row_count('nonexistent')
        assert count == 0

    def test_process_operations_stats(self):
        """Table statistics collected correctly"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        with sqlite3.connect(db_path) as conn:
            conn.execute("CREATE TABLE a (id INTEGER)")
            conn.execute("INSERT INTO a VALUES (1)")
            conn.execute("CREATE TABLE b (name TEXT)")
            conn.execute("INSERT INTO b VALUES ('x')")
            conn.commit()

        access_layer = DatabaseAccessLayer(db_path)
        assert access_layer.process_operations() is True
        assert access_layer.table_stats["a"] == 1
        assert access_layer.table_stats["b"] == 1


class TestQueryBuilder:
    """Test query builder functionality"""
    
    def test_select_simple(self):
        """Test simple SELECT query building"""
        query, params = QueryBuilder.select('users')
        assert query == "SELECT * FROM users"
        assert params == ()
    
    def test_select_with_columns(self):
        """Test SELECT with specific columns"""
        query, params = QueryBuilder.select('users', ['id', 'name'])
        assert query == "SELECT id, name FROM users"
        assert params == ()
    
    def test_select_with_where(self):
        """Test SELECT with WHERE clause"""
        query, params = QueryBuilder.select('users', where={'id': 1, 'active': True})
        assert "WHERE" in query
        assert "id = ?" in query
        assert "active = ?" in query
        assert len(params) == 2
    
    def test_insert(self):
        """Test INSERT query building"""
        data = {'name': 'John', 'age': 30}
        query, params = QueryBuilder.insert('users', data)
        assert query == "INSERT INTO users (name, age) VALUES (?, ?)"
        assert params == ('John', 30)
    
    def test_update(self):
        """Test UPDATE query building"""
        data = {'name': 'Jane'}
        where = {'id': 1}
        query, params = QueryBuilder.update('users', data, where)
        assert query == "UPDATE users SET name = ? WHERE id = ?"
        assert params == ('Jane', 1)
    
    def test_delete(self):
        """Test DELETE query building"""
        where = {'id': 1}
        query, params = QueryBuilder.delete('users', where)
        assert query == "DELETE FROM users WHERE id = ?"
        assert params == (1,)


class TestDataValidator:
    """Test data validation functionality"""
    
    def test_validate_file_path(self):
        """Test file path validation"""
        assert DataValidator.validate_file_path('test.py') is True
        assert DataValidator.validate_file_path('folder/test.py') is True
        assert DataValidator.validate_file_path('../test.py') is False
        assert DataValidator.validate_file_path('/etc/passwd') is False
    
    def test_validate_sql_table_name(self):
        """Test SQL table name validation"""
        assert DataValidator.validate_sql_table_name('users') is True
        assert DataValidator.validate_sql_table_name('user_data') is True
        assert DataValidator.validate_sql_table_name('_internal') is True
        assert DataValidator.validate_sql_table_name('123invalid') is False
        assert DataValidator.validate_sql_table_name('user-data') is False
        assert DataValidator.validate_sql_table_name('user data') is False
    
    def test_validate_sql_column_name(self):
        """Test SQL column name validation"""
        assert DataValidator.validate_sql_column_name('id') is True
        assert DataValidator.validate_sql_column_name('user_id') is True
        assert DataValidator.validate_sql_column_name('_private') is True
        assert DataValidator.validate_sql_column_name('123invalid') is False
        assert DataValidator.validate_sql_column_name('user-id') is False
    
    def test_sanitize_string(self):
        """Test string sanitization"""
        result = DataValidator.sanitize_string('test string')
        assert result == 'test string'
        
        # Test null character removal
        result = DataValidator.sanitize_string('test\x00string')
        assert result == 'teststring'
        
        # Test length limiting
        long_string = 'a' * 2000
        result = DataValidator.sanitize_string(long_string, max_length=100)
        assert len(result) == 100
    
    def test_validate_violation_data(self):
        """Test violation data validation"""
        valid_data = {
            'file_path': 'test.py',
            'line_number': 10,
            'error_code': 'E101'
        }
        errors = DataValidator.validate_violation_data(valid_data)
        assert len(errors) == 0
        
        # Test missing fields
        invalid_data = {'file_path': 'test.py'}
        errors = DataValidator.validate_violation_data(invalid_data)
        assert len(errors) > 0
        assert any('line_number' in error for error in errors)
        
        # Test invalid line number
        invalid_data = {
            'file_path': 'test.py',
            'line_number': -1,
            'error_code': 'E101'
        }
        errors = DataValidator.validate_violation_data(invalid_data)
        assert any('positive' in error for error in errors)


class TestDatabaseCleanupProcessor:
    """Test database cleanup processor"""
    
    def test_initialization(self):
        """Test cleanup processor initialization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            processor = DatabaseCleanupProcessor(temp_dir)
            assert processor.workspace_path == Path(temp_dir)


class TestDatabaseComplianceChecker:
    """Test database compliance checker"""
    
    def test_initialization(self):
        """Test compliance checker initialization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            checker = DatabaseComplianceChecker(temp_dir)
            assert checker.workspace_path == Path(temp_dir)
    
    def test_should_process_file(self):
        """Test file processing logic"""
        checker = DatabaseComplianceChecker()
        
        # Should process normal Python files
        assert checker.should_process_file(Path('test.py')) is True
        assert checker.should_process_file(Path('src/module.py')) is True
        
        # Should skip hidden files and directories
        assert checker.should_process_file(Path('.hidden/test.py')) is False
        assert checker.should_process_file(Path('src/.test.py')) is False
        
        # Should skip build directories
        assert checker.should_process_file(Path('__pycache__/test.py')) is False
        assert checker.should_process_file(Path('build/test.py')) is False