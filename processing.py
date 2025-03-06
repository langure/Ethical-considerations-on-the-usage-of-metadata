import os
import csv
import sqlite3
from rich.console import Console
import pandas as pd

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
    
    Returns:
        tuple: (success_bool, record_count)
    """
    # Validate CSV file exists
    if not os.path.exists(csv_path):
        console.print("[bold red]Error: CSV file not found at {csv_path}[/bold red]")
        return False, 0
    
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
            csv_reader = list(csv.reader(csvfile))
            headers = csv_reader[0]
            data_rows = csv_reader[1:]  # Exclude header
            
            # Sanitize column names
            sanitized_headers = [sanitize_column_name(header) for header in headers]
            
            # Create table (drop if exists)
            cursor.execute("DROP TABLE IF EXISTS isear_original")
            create_table_sql = f"CREATE TABLE isear_original ({', '.join([f'{header} TEXT' for header in sanitized_headers])})"
            cursor.execute(create_table_sql)
            
            # Insert data
            insert_sql = f"INSERT INTO isear_original VALUES ({','.join(['?' for _ in headers])})"
            cursor.executemany(insert_sql, data_rows)
            conn.commit()
        
        return True, len(data_rows)
    
    except Exception as e:
        console.print(f"\n[bold red]Error during import: {str(e)}[/bold red]")
        return False, 0
    finally:
        if 'conn' in locals():
            conn.close()

def initialize_anonymous_table(sqlite_filename: str = 'isear.db'):
    """
    Create an anonymous version of the original ISEAR dataset.
    
    Args:
        sqlite_filename (str, optional): Name of the SQLite database file. Defaults to 'isear.db'.
    
    Returns:
        tuple: (success_bool, record_count)
    """
    # Ensure data directory exists
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Full path for SQLite database
    sqlite_path = os.path.join(data_dir, sqlite_filename)
    
    try:
        # Connect to database
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        # Check if original table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='isear_original'")
        if not cursor.fetchone():
            console.print("[bold red]Error: Original table 'isear_original' does not exist[/bold red]")
            return False, 0
        
        # Get column names from original table
        cursor.execute("PRAGMA table_info(isear_original)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Drop anonymous table if it exists
        cursor.execute("DROP TABLE IF EXISTS isear_anonymous")
        
        # Create anonymous table with same structure
        create_table_sql = f"CREATE TABLE isear_anonymous AS SELECT * FROM isear_original"
        cursor.execute(create_table_sql)
        
        # Get record count
        cursor.execute("SELECT COUNT(*) FROM isear_anonymous")
        record_count = cursor.fetchone()[0]
        
        # Commit changes
        conn.commit()
        
        return True, record_count
    
    except Exception as e:
        console.print(f"\n[bold red]Error creating anonymous table: {str(e)}[/bold red]")
        return False, 0
    finally:
        if 'conn' in locals():
            conn.close()

def calculate_anonymity_index(sqlite_filename: str, table_name: str, identifying_columns: list) -> float:
    """
    Calculate the anonymity index for a given table.
    
    Args:
        sqlite_filename (str): Name of the SQLite database file
        table_name (str): Name of the table to analyze
        identifying_columns (list): List of column names to consider for anonymity
    
    Returns:
        float: Anonymity index (0-1 scale)
    """
    console.print(f"[blue]Starting anonymity index calculation for {table_name}...[/blue]")
    
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'data', sqlite_filename))
        
        # Read the table into a pandas DataFrame
        query = f"SELECT {', '.join(identifying_columns)} FROM {table_name}"
        df = pd.read_sql_query(query, conn)
        
        # Close the connection
        conn.close()
        
        # Total number of rows
        total_rows = len(df)
        
        # Count unique combinations of identifying columns
        unique_combinations = len(df.drop_duplicates(subset=identifying_columns))
        
        # Calculate anonymity index
        anonymity_index = 1 - (unique_combinations / total_rows)
        
        # Categorize anonymity level
        def categorize_anonymity(index):
            if index < 0.2:
                return "Very Low"
            elif index < 0.4:
                return "Low"
            elif index < 0.6:
                return "Moderate"
            elif index < 0.8:
                return "High"
            else:
                return "Very High"
        
        # Print detailed results
        console.print(f"[cyan]→[/cyan] Total Rows: {total_rows}")
        console.print(f"[cyan]→[/cyan] Unique Combinations: {unique_combinations}")
        console.print(f"[green]✓[/green] Anonymity Index: {anonymity_index:.4f}")
        console.print(f"[magenta]→[/magenta] Anonymity Level: {categorize_anonymity(anonymity_index)}")
        
        console.print(f"[blue]Anonymity index calculation for {table_name} ... done.[/blue]")
        
        return anonymity_index
    
    except Exception as e:
        console.print(f"[bold red]Error calculating anonymity index: {e}[/bold red]")
        return 0.0  # Return lowest possible anonymity in case of error