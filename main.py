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
from processing import load_csv_to_sqlite

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

def main():
    # Clear the screen at the start
    clear_screen()
    
    # Initialize the project console
    project_console = ProjectConsole()
    
    # Display the project header
    project_console.display_header()
    
    console = Console()
    
    # Execute task with progress tracking
    with Progress(console=console) as progress:
        task = progress.add_task("Loading ISEAR dataset...", total=None)
        
        # Load the CSV file
        result = load_csv_to_sqlite(
            os.path.join(os.path.dirname(__file__), 'data', 'ISEAR.csv')
        )
        
        # Stop the progress display
        progress.stop()
        
        # Show the result
        if result:
            console.print("[green]✓[/green] CSV successfully imported to SQLite database")
        else:
            console.print("[red]✗[/red] Failed to import CSV to SQLite database")

if __name__ == "__main__":
    main()
