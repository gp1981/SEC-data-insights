import sqlite3
import pandas as pd
from tabulate import tabulate

class DBExplorer:
    def __init__(self, db_path='sec_filings.db'):
        """Initialize database connection"""
        self.conn = sqlite3.connect(db_path)
    
    def list_tables(self):
        """List all tables in the database"""
        query = """
        SELECT name FROM sqlite_master 
        WHERE type='table'
        ORDER BY name;
        """
        tables = pd.read_sql_query(query, self.conn)
        print("\nAvailable tables:")
        print(tabulate(tables, headers='keys', tablefmt='psql'))
    
    def table_info(self, table_name):
        """Show table schema"""
        query = f"PRAGMA table_info({table_name});"
        schema = pd.read_sql_query(query, self.conn)
        print(f"\nSchema for table '{table_name}':")
        print(tabulate(schema, headers='keys', tablefmt='psql'))
    
    def preview_table(self, table_name, limit=5):
        """Show first few rows of a table"""
        query = f"SELECT * FROM {table_name} LIMIT {limit};"
        data = pd.read_sql_query(query, self.conn)
        print(f"\nPreview of table '{table_name}' (first {limit} rows):")
        print(tabulate(data, headers='keys', tablefmt='psql'))
    
    def custom_query(self, query):
        """Execute custom SQL query"""
        result = pd.read_sql_query(query, self.conn)
        print("\nQuery results:")
        print(tabulate(result, headers='keys', tablefmt='psql'))
    
    def close(self):
        """Close database connection"""
        self.conn.close()