import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress
from rich.live import Live
import time
from utils import ProjectConsole, load_project_configuration
from processing import load_csv_to_sqlite, initialize_anonymous_table

# Load environment variables
load_dotenv()

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def create_header():
    """Create a sticky header with project information."""
    # Create the header panel
    header_text = Text(f"Research Project", style="bold magenta")
    header_text.append("\n" + os.getenv('TITLE', 'Untitled Project'), style="bold white")
    
    header_panel = Panel(
        header_text,
        title=f"By {os.getenv('AUTHOR', 'Unknown Author')} | {os.getenv('YEAR', 'N/A')}",
        border_style="bold blue",
        expand=False
    )

    return header_panel

def report_task_result(console, task_name, success, record_count=None):
    """
    Standardized method to report task results.
    
    Args:
        console (Console): Rich console for output
        task_name (str): Name of the task
        success (bool): Whether the task was successful
        record_count (int, optional): Number of records processed
    """
    if success:
        console.print(f"[green]✓[/green] {task_name} successful")
        if record_count is not None:
            console.print(f"[cyan]→[/cyan] Total records: {record_count}")
    else:
        console.print(f"[red]✗[/red] Failed to {task_name}")

def main():
    # Clear the screen at the start
    clear_screen()
    
    # Initialize the project console
    project_console = ProjectConsole()
    
    # Display the project header
    project_console.display_header()
    
    console = Console()
    
    # Execute tasks with progress tracking
    with Progress(console=console) as progress:
        # Task 1: Load CSV to SQLite
        task1 = progress.add_task("Loading ISEAR dataset...", total=None)
        success1, record_count1 = load_csv_to_sqlite(
            os.path.join(os.path.dirname(__file__), 'data', 'ISEAR.csv')
        )
        progress.update(task1, completed=True)
        
        # Task 2: Initialize Anonymous Table
        task2 = progress.add_task("Creating anonymous table...", total=None)
        success2, record_count2 = initialize_anonymous_table()
        progress.update(task2, completed=True)
        
        # Stop the progress display
        progress.stop()
        
        # Report results
        report_task_result(console, "CSV import to SQLite", success1, record_count1)
        report_task_result(console, "Anonymous table creation", success2, record_count2)

if __name__ == "__main__":
    main()
