"""
Database utility functions for SQLite operations.
"""
import sqlite3
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager with utility methods."""
    
    def __init__(self, db_path: str):
        """Initialize database connection."""
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        
    def connect(self):
        """Establish database connection."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Access columns by name
        logger.info(f"Connected to database: {self.db_path}")
        return self.connection
    
    def create_schema(self, schema_path: str):
        """Execute schema SQL file to create tables."""
        if not self.connection:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        cursor = self.connection.cursor()
        cursor.executescript(schema_sql)
        self.connection.commit()
        logger.info(f"Schema created from {schema_path}")
        
    def insert_one(self, table: str, data: dict):
        """Insert a single row into a table."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        cursor = self.connection.cursor()
        cursor.execute(sql, list(data.values()))
        return cursor.lastrowid
    
    def insert_many(self, table: str, data_list: list[dict]):
        """Insert multiple rows into a table efficiently."""
        if not data_list:
            return
        
        # All dicts should have same keys
        columns = ', '.join(data_list[0].keys())
        placeholders = ', '.join(['?' ] * len(data_list[0]))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        cursor = self.connection.cursor()
        values_list = [list(d.values()) for d in data_list]
        cursor.executemany(sql, values_list)
        logger.debug(f"Inserted {len(data_list)} rows into {table}")
        
    def commit(self):
        """Commit transaction."""
        if self.connection:
            self.connection.commit()
            
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
            
    def get_random_records(self, table: str, column: str, limit: int = 1) -> list:
        """Get random records from a table (useful for FK assignments)."""
        cursor = self.connection.cursor()
        sql = f"SELECT {column} FROM {table} ORDER BY RANDOM() LIMIT ?"
        result = cursor.execute(sql, (limit,)).fetchall()
        return [row[0] for row in result]
    
    def get_records_by_condition(self, table: str, column: str, 
                                  condition: str, params: tuple = ()) -> list:
        """Get records matching a condition."""
        cursor = self.connection.cursor()
        sql = f"SELECT {column} FROM {table} WHERE {condition}"
        result = cursor.execute(sql, params).fetchall()
        return [row[0] for row in result]
    
    def count_records(self, table: str) -> int:
        """Count total records in a table."""
        cursor = self.connection.cursor()
        result = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
        return result[0]


def create_database(db_path: str, schema_path: str) -> Database:
    """
    Create and initialize database with schema.
    
    Args:
        db_path: Path to SQLite database file
        schema_path: Path to SQL schema file
        
    Returns:
        Database instance
    """
    db = Database(db_path)
    db.connect()
    db.create_schema(schema_path)
    return db