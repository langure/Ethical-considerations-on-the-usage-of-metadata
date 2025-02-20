import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress
from typing import Optional, List, Callable

# Load environment variables
load_dotenv()

class ProjectConsole:
    """
    A utility class for managing console output with Rich formatting.
    Follows the guidelines in context.txt for consistent output.
    """
    
    def __init__(self):
        """
        Initialize the console with project metadata.
        """
        self.console = Console()
        self.project_metadata = {
            'title': os.getenv('TITLE', 'Untitled Project'),
            'author': os.getenv('AUTHOR', 'Unknown Author'),
            'year': os.getenv('YEAR', 'N/A'),
            'topic': os.getenv('TOPIC', 'Not Specified')
        }
    
    def create_header(self) -> Panel:
        """
        Create a formatted header panel with project information.
        
        Returns:
            Panel: A Rich panel containing project metadata
        """
        header_text = Text("Research Project", style="bold magenta")
        header_text.append(f"\n{self.project_metadata['title']}", style="bold white")
        
        return Panel(
            header_text,
            title=f"By {self.project_metadata['author']} | {self.project_metadata['year']}",
            border_style="bold blue",
            expand=False
        )
    
    def display_header(self):
        """
        Print the project header to the console.
        """
        self.console.print(self.create_header())
    
    def print_info(self, message: str, style: str = "yellow"):
        """
        Print an informational message with consistent styling.
        
        Args:
            message (str): The message to print
            style (str, optional): Rich styling for the message
        """
        self.console.print(f"[{style}]{message}[/{style}]")
    
    def print_success(self, message: str):
        """
        Print a success message in green.
        
        Args:
            message (str): The success message
        """
        self.console.print(f"[green]✓ {message}[/green]")
    
    def progress_tasks(self, tasks: List[dict]):
        """
        Execute a list of tasks with progress tracking.
        
        Args:
            tasks (List[dict]): A list of task dictionaries with 'name' and 'function' keys
        """
        with Progress(console=self.console, transient=True) as progress:
            for task_info in tasks:
                task = progress.add_task(task_info['name'], total=100)
                
                # Execute the task function if provided
                if 'function' in task_info and callable(task_info['function']):
                    task_info['function']()
                
                # Simulate progress
                for _ in range(100):
                    progress.update(task, advance=1)
                    # You can add a small sleep here if needed
    
    def error(self, message: str, exception: Optional[Exception] = None):
        """
        Print an error message with optional exception details.
        
        Args:
            message (str): The error message
            exception (Exception, optional): Optional exception to print details
        """
        self.console.print(f"[bold red]ERROR:[/bold red] {message}")
        if exception:
            self.console.print_exception(show_locals=True)

# Utility functions can be added here as needed
def load_project_configuration():
    """
    Load project configuration from environment variables.
    
    Returns:
        dict: Project configuration details
    """
    return {
        'title': os.getenv('TITLE'),
        'author': os.getenv('AUTHOR'),
        'year': os.getenv('YEAR'),
        'topic': os.getenv('TOPIC')
    }