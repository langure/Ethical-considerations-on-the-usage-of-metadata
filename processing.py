import os
import csv
import sqlite3
from rich.console import Console

console = Console()

def sanitize_column_name(name: str) -> str:
    """
    Sanitize column names to be SQLite-compatible.
    
    Args:
        name (str): Original column name
    
    Returns:
        str: Sanitized column name
    """
    # Remove special characters and replace spaces
    sanitized = ''.join(c if c.isalnum() or c == '_' else '_' for c in name)
    
    # Ensure it doesn't start with a number
    if sanitized[0].isdigit():
        sanitized = f'col_{sanitized}'
    
    # Ensure it's not a SQLite reserved keyword
    sqlite_keywords = {'when', 'where', 'select', 'from', 'order', 'group', 'by', 'and', 'or'}
    if sanitized.lower() in sqlite_keywords:
        sanitized = f'col_{sanitized}'
    
    return sanitized.lower()

def load_csv_to_sqlite(csv_path: str, sqlite_filename: str = 'isear.db'):
    """
    Load CSV data into an SQLite database table.
    
    Args:
        csv_path (str): Path to the source CSV file
        sqlite_filename (str, optional): Name of the SQLite database file. Defaults to 'isear.db'.
    """
    # Validate CSV file exists
    if not os.path.exists(csv_path):
        console.print("[bold red]Error: CSV file not found at {csv_path}[/bold red]")
        return False
    
    # Ensure data directory exists
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Full path for SQLite database
    sqlite_path = os.path.join(data_dir, sqlite_filename)
    
    try:
        # Connect to database
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        # Read CSV and get headers
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            headers = next(csv_reader)
            
            # Sanitize column names
            sanitized_headers = [sanitize_column_name(header) for header in headers]
            
            # Create table (drop if exists)
            cursor.execute("DROP TABLE IF EXISTS isear_original")
            create_table_sql = f"CREATE TABLE isear_original ({', '.join([f'{header} TEXT' for header in sanitized_headers])})"
            cursor.execute(create_table_sql)
            
            # Insert data
            insert_sql = f"INSERT INTO isear_original VALUES ({','.join(['?' for _ in headers])})"
            cursor.executemany(insert_sql, csv_reader)
            conn.commit()
        
        return True
    
    except Exception as e:
        console.print(f"\n[bold red]Error during import: {str(e)}[/bold red]")
        return False
    finally:
        if 'conn' in locals():
            conn.close()