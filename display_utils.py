"""
Display utilities for the response formatter system.
Handles terminal formatting, colors, and interactive elements using Rich.
"""

import sys
import threading
import time
from typing import Dict, Any, Optional, List, Callable
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.columns import Columns
from rich.table import Table
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from config import get_config, Config


class InteractiveDisplay:
    """Handles interactive terminal display with keyboard shortcuts."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.config = get_config()
        self.current_mode = self.config.display.default_mode
        self.expanded_sections: Dict[str, bool] = {}
        self.keyboard_enabled = self.config.display.enable_interactive
        self._stop_keyboard_listener = False
        
    def setup_keyboard_listener(self):
        """Set up keyboard listener for interactive mode."""
        if not self.keyboard_enabled:
            return
            
        try:
            import keyboard
            
            def on_key_event(event):
                if event.event_type == keyboard.KEY_DOWN:
                    self._handle_key_press(event.name)
            
            keyboard.hook(on_key_event)
        except ImportError:
            self.console.print("[yellow]Warning: keyboard module not available. Interactive mode disabled.[/yellow]")
            self.keyboard_enabled = False
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not set up keyboard listener: {e}[/yellow]")
            self.keyboard_enabled = False
    
    def _handle_key_press(self, key: str):
        """Handle keyboard input."""
        config = self.config.keyboard
        
        if key == config.clean_mode:
            self.current_mode = "clean"
            self.console.print("[dim]Switched to clean mode[/dim]")
        elif key == config.verbose_mode:
            self.current_mode = "verbose"
            self.console.print("[dim]Switched to verbose mode[/dim]")
        elif key == config.debug_mode:
            self.current_mode = "debug"
            self.console.print("[dim]Switched to debug mode[/dim]")
        elif key == config.reasoning and "reasoning" in self.expanded_sections:
            self.expanded_sections["reasoning"] = not self.expanded_sections["reasoning"]
            self.console.print("[dim]Toggled reasoning section[/dim]")
        elif key == config.expand_collapse:
            # Toggle the most recent expandable section
            if self.expanded_sections:
                last_section = list(self.expanded_sections.keys())[-1]
                self.expanded_sections[last_section] = not self.expanded_sections[last_section]
                self.console.print(f"[dim]Toggled {last_section} section[/dim]")
        elif key == config.exit_interactive:
            self._stop_keyboard_listener = True
    
    def create_mode_indicator(self) -> Text:
        """Create a visual indicator of the current display mode."""
        mode_colors = {
            "clean": "green",
            "verbose": "yellow", 
            "debug": "red"
        }
        
        color = mode_colors.get(self.current_mode, "white")
        return Text(f"[{self.current_mode.upper()}]", style=color)
    
    def create_interaction_hints(self) -> Text:
        """Create hints for keyboard shortcuts."""
        if not self.keyboard_enabled:
            return Text("")
        
        config = self.config.keyboard
        hints = []
        
        if self.current_mode != "clean":
            hints.append(f"'{config.clean_mode}'=clean")
        if self.current_mode != "verbose":
            hints.append(f"'{config.verbose_mode}'=verbose")
        if self.current_mode != "debug":
            hints.append(f"'{config.debug_mode}'=debug")
        if "reasoning" in self.expanded_sections:
            hints.append(f"'{config.reasoning}'=reasoning")
        
        if hints:
            hint_text = f"[Press {' | '.join(hints)}]"
            return Text(hint_text, style="dim")
        
        return Text("")
    
    def create_expandable_section(self, title: str, content: str, 
                                  expanded: bool = False,
                                  style: str = "white") -> Panel:
        """Create an expandable section with toggle indicator."""
        self.expanded_sections[title] = expanded
        
        indicator = "▼" if expanded else "▶"
        panel_title = f"{indicator} {title}"
        
        if expanded:
            panel_content = content
        else:
            # Show truncated preview
            preview = content[:100] + "..." if len(content) > 100 else content
            panel_content = f"[dim]{preview}[/dim]\n\n[dim italic]Press space to expand[/dim italic]"
        
        return Panel(
            panel_content,
            title=panel_title,
            border_style=style,
            box=box.ROUNDED
        )


class ColorFormatter:
    """Handles color formatting based on configuration."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or get_config()
        self.console = Console()
        
    def format_header(self, text: str) -> Text:
        """Format header text."""
        color = self.config.colors.header if self.config.display.enable_colors else "white"
        return Text(text, style=f"bold {color}")
    
    def format_content(self, text: str) -> Text:
        """Format main content text."""
        color = self.config.colors.content if self.config.display.enable_colors else "white"
        return Text(text, style=color)
    
    def format_error(self, text: str) -> Text:
        """Format error text."""
        color = self.config.colors.error if self.config.display.enable_colors else "white"
        return Text(text, style=f"bold {color}")
    
    def format_warning(self, text: str) -> Text:
        """Format warning text."""
        color = self.config.colors.warning if self.config.display.enable_colors else "white"
        return Text(text, style=color)
    
    def format_technical(self, text: str) -> Text:
        """Format technical details text."""
        color = self.config.colors.technical if self.config.display.enable_colors else "white"
        return Text(text, style=color)
    
    def format_reasoning(self, text: str) -> Text:
        """Format reasoning text."""
        color = self.config.colors.reasoning if self.config.display.enable_colors else "white"
        return Text(text, style=color)
    
    def format_usage(self, text: str) -> Text:
        """Format usage statistics text."""
        color = self.config.colors.usage if self.config.display.enable_colors else "white"
        return Text(text, style=color)


class ProgressDisplay:
    """Handles progress indication during processing."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.progress: Optional[Progress] = None
        
    def show_processing(self, message: str = "Processing response..."):
        """Show a processing spinner."""
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        )
        
        self.progress.start()
        task = self.progress.add_task(message, total=None)
        return task
    
    def hide_processing(self):
        """Hide the processing spinner."""
        if self.progress:
            self.progress.stop()
            self.progress = None


class TableFormatter:
    """Formats data in table format for better readability."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        
    def create_usage_table(self, usage_data: Dict[str, Any]) -> Table:
        """Create a table for usage statistics."""
        table = Table(title="Usage Statistics", box=box.ROUNDED)
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")
        
        for key, value in usage_data.items():
            # Format the key to be more readable
            formatted_key = key.replace('_', ' ').title()
            table.add_row(formatted_key, str(value))
        
        return table
    
    def create_metadata_table(self, metadata: Dict[str, Any]) -> Table:
        """Create a table for response metadata."""
        table = Table(title="Response Metadata", box=box.ROUNDED)
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        for key, value in metadata.items():
            if value is not None:
                formatted_key = key.replace('_', ' ').title()
                # Truncate long values
                str_value = str(value)
                if len(str_value) > 50:
                    str_value = str_value[:47] + "..."
                table.add_row(formatted_key, str_value)
        
        return table


class ContentTruncator:
    """Handles content truncation and preview generation."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or get_config()
    
    def truncate_content(self, content: str, max_length: Optional[int] = None) -> str:
        """Truncate content if it exceeds maximum length."""
        if not self.config.display.truncate_long_content:
            return content
            
        max_len = max_length or self.config.display.max_content_length
        
        if len(content) <= max_len:
            return content
        
        # Try to truncate at word boundary
        truncated = content[:max_len]
        last_space = truncated.rfind(' ')
        
        if last_space > max_len * 0.8:  # If we can find a good word boundary
            truncated = truncated[:last_space]
        
        return truncated + "..."
    
    def create_preview(self, content: str, preview_length: int = 100) -> str:
        """Create a short preview of content."""
        if len(content) <= preview_length:
            return content
        
        preview = content[:preview_length]
        last_space = preview.rfind(' ')
        
        if last_space > preview_length * 0.7:
            preview = preview[:last_space]
        
        return preview + "..."


def create_separator(width: int = 80, char: str = "─") -> Text:
    """Create a visual separator line."""
    return Text(char * width, style="dim")


def format_timestamp(timestamp: float) -> str:
    """Format a timestamp for display."""
    import datetime
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def calculate_cost(usage_data: Dict[str, Any], model: str = "o3") -> Optional[float]:
    """Calculate estimated cost based on usage statistics."""
    # OpenAI pricing (approximate, as of 2024)
    pricing = {
        "o3": {"input": 0.03, "output": 0.06},  # per 1K tokens
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
    }
    
    if model not in pricing:
        return None
    
    input_tokens = usage_data.get("prompt_tokens", 0)
    output_tokens = usage_data.get("completion_tokens", 0)
    
    if not input_tokens and not output_tokens:
        return None
    
    model_pricing = pricing[model]
    input_cost = (input_tokens / 1000) * model_pricing["input"]
    output_cost = (output_tokens / 1000) * model_pricing["output"]
    
    return input_cost + output_cost