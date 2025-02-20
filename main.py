import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress
from rich.live import Live
import time
from utils import ProjectConsole, load_project_configuration

# Load environment variables
load_dotenv()

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

def example_task1():
    """Example task to demonstrate progress tracking."""
    time.sleep(0.5)

def example_task2():
    """Another example task."""
    time.sleep(0.5)

def main():
    # Initialize the project console
    project_console = ProjectConsole()
    
    # Display the project header
    project_console.display_header()
    
    # Print project topic
    project_console.print_info(f"Project Topic: {project_console.project_metadata['topic']}")
    
    # Define and execute tasks
    tasks = [
        {
            'name': '[blue]Performing initial setup...[/blue]',
            'function': example_task1
        },
        {
            'name': '[cyan]Loading data...[/cyan]',
            'function': example_task2
        },
        {
            'name': '[magenta]Preparing analysis...[/magenta]',
            'function': None  # No function for this task
        }
    ]
    
    # Run tasks with progress tracking
    project_console.progress_tasks(tasks)
    
    # Print success message
    project_console.print_success("Setup complete!")

if __name__ == "__main__":
    main()
