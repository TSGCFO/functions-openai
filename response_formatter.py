"""
Main response formatter system for transforming OpenAI response objects
into user-friendly, interactive displays.
"""

import json
import time
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich import box

from config import get_config, Config
from display_utils import (
    InteractiveDisplay, ColorFormatter, ProgressDisplay, 
    TableFormatter, ContentTruncator, create_separator,
    format_timestamp, calculate_cost
)


@dataclass
class ExtractedContent:
    """Container for extracted response content."""
    text: Optional[str] = None
    reasoning: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    model: Optional[str] = None
    timestamp: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    raw_response: Optional[Any] = None


class ContentExtractor:
    """Extracts meaningful content from OpenAI response objects."""
    
    def __init__(self):
        self.config = get_config()
    
    def extract(self, response: Any) -> ExtractedContent:
        """Extract content from an OpenAI response object."""
        try:
            extracted = ExtractedContent()
            extracted.raw_response = response
            extracted.timestamp = time.time()
            
            # Handle different response types
            if hasattr(response, 'text'):
                # Direct text response
                extracted.text = str(response.text)
            elif hasattr(response, 'choices') and response.choices:
                # Chat completion response
                choice = response.choices[0]
                if hasattr(choice, 'message'):
                    extracted.text = choice.message.content
                elif hasattr(choice, 'text'):
                    extracted.text = choice.text
            elif hasattr(response, 'content'):
                # Some response formats have direct content
                extracted.text = str(response.content)
            elif isinstance(response, str):
                # String response
                extracted.text = response
            else:
                # Try to extract from response object attributes
                extracted.text = self._extract_text_from_object(response)
            
            # Extract reasoning if available
            extracted.reasoning = self._extract_reasoning(response)
            
            # Extract usage statistics
            extracted.usage = self._extract_usage(response)
            
            # Extract model information
            extracted.model = self._extract_model(response)
            
            # Extract additional metadata
            extracted.metadata = self._extract_metadata(response)
            
            return extracted
            
        except Exception as e:
            # Return error information
            return ExtractedContent(
                error=f"Failed to extract content: {str(e)}",
                raw_response=response,
                timestamp=time.time()
            )
    
    def _extract_text_from_object(self, response: Any) -> Optional[str]:
        """Try to extract text from various response object formats."""
        # Common attributes that might contain the response text
        text_attributes = [
            'text', 'content', 'message', 'response', 'output',
            'result', 'answer', 'completion'
        ]
        
        for attr in text_attributes:
            if hasattr(response, attr):
                value = getattr(response, attr)
                if isinstance(value, str):
                    return value
                elif hasattr(value, 'content'):
                    return str(value.content)
                elif hasattr(value, 'text'):
                    return str(value.text)
        
        # If no text found, convert the whole response to string
        return str(response)
    
    def _extract_reasoning(self, response: Any) -> Optional[str]:
        """Extract reasoning information from response."""
        reasoning_attributes = ['reasoning', 'explanation', 'rationale', 'logic']
        
        for attr in reasoning_attributes:
            if hasattr(response, attr):
                value = getattr(response, attr)
                if value:
                    return str(value)
        
        return None
    
    def _extract_usage(self, response: Any) -> Optional[Dict[str, Any]]:
        """Extract token usage and other statistics."""
        if hasattr(response, 'usage'):
            usage = response.usage
            if hasattr(usage, '__dict__'):
                return usage.__dict__
            elif isinstance(usage, dict):
                return usage
        
        # Try to extract usage from other common locations
        usage_data = {}
        
        # Common usage attributes
        usage_attrs = [
            ('prompt_tokens', ['prompt_tokens', 'input_tokens']),
            ('completion_tokens', ['completion_tokens', 'output_tokens']),
            ('total_tokens', ['total_tokens']),
        ]
        
        for key, attrs in usage_attrs:
            for attr in attrs:
                if hasattr(response, attr):
                    usage_data[key] = getattr(response, attr)
                    break
        
        return usage_data if usage_data else None
    
    def _extract_model(self, response: Any) -> Optional[str]:
        """Extract model information from response."""
        model_attributes = ['model', 'model_name', 'engine']
        
        for attr in model_attributes:
            if hasattr(response, attr):
                return str(getattr(response, attr))
        
        return None
    
    def _extract_metadata(self, response: Any) -> Optional[Dict[str, Any]]:
        """Extract additional metadata from response."""
        metadata = {}
        
        # Common metadata attributes
        metadata_attrs = [
            'id', 'created', 'object', 'system_fingerprint',
            'finish_reason', 'logprobs', 'index'
        ]
        
        for attr in metadata_attrs:
            if hasattr(response, attr):
                value = getattr(response, attr)
                if value is not None:
                    metadata[attr] = value
        
        return metadata if metadata else None


class ErrorHandler:
    """Handles error processing and user-friendly error presentation."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.color_formatter = ColorFormatter()
    
    def handle_extraction_error(self, error: str, raw_response: Any) -> None:
        """Handle errors during content extraction."""
        error_panel = Panel(
            self.color_formatter.format_error(f"Content Extraction Error\n\n{error}"),
            title="⚠️ Error",
            border_style="red",
            box=box.ROUNDED
        )
        
        self.console.print(error_panel)
        
        # Offer to show raw response in debug mode
        if get_config().display.default_mode == "debug":
            self._show_raw_response_on_error(raw_response)
    
    def handle_formatting_error(self, error: str, content: ExtractedContent) -> None:
        """Handle errors during response formatting."""
        error_text = f"Formatting Error: {error}"
        
        # Try to show at least the extracted text if available
        if content.text:
            self.console.print(self.color_formatter.format_header("Assistant:"))
            self.console.print(self.color_formatter.format_content(content.text))
            self.console.print()
            self.console.print(self.color_formatter.format_error(error_text))
        else:
            error_panel = Panel(
                self.color_formatter.format_error(error_text),
                title="⚠️ Formatting Error",
                border_style="red",
                box=box.ROUNDED
            )
            self.console.print(error_panel)
    
    def _show_raw_response_on_error(self, raw_response: Any) -> None:
        """Show the raw response when there's an error."""
        try:
            raw_text = json.dumps(raw_response.__dict__, indent=2) if hasattr(raw_response, '__dict__') else str(raw_response)
        except:
            raw_text = str(raw_response)
        
        raw_panel = Panel(
            self.color_formatter.format_technical(raw_text[:1000] + "..." if len(raw_text) > 1000 else raw_text),
            title="Raw Response (Debug)",
            border_style="dim",
            box=box.ROUNDED
        )
        
        self.console.print(raw_panel)


class ResponseFormatter:
    """Main formatting engine that orchestrates response presentation."""
    
    def __init__(self, console: Optional[Console] = None, mode: Optional[str] = None):
        self.console = console or Console()
        self.config = get_config()
        self.mode = mode or self.config.display.default_mode
        
        # Initialize helper components
        self.extractor = ContentExtractor()
        self.error_handler = ErrorHandler(self.console)
        self.interactive_display = InteractiveDisplay(self.console)
        self.color_formatter = ColorFormatter()
        self.progress_display = ProgressDisplay(self.console)
        self.table_formatter = TableFormatter(self.console)
        self.content_truncator = ContentTruncator()
        
        # Set interactive display mode
        if mode:
            self.interactive_display.current_mode = mode
    
    def format_response(self, response: Any, mode: Optional[str] = None) -> None:
        """Format and display an OpenAI response."""
        display_mode = mode or self.mode
        
        # Show processing indicator
        task = self.progress_display.show_processing("Processing response...")
        
        try:
            # Extract content from response
            content = self.extractor.extract(response)
            
            # Hide processing indicator
            self.progress_display.hide_processing()
            
            # Handle extraction errors
            if content.error:
                self.error_handler.handle_extraction_error(content.error, content.raw_response)
                return
            
            # Format based on display mode
            if display_mode == "clean":
                self._format_clean(content)
            elif display_mode == "verbose":
                self._format_verbose(content)
            elif display_mode == "debug":
                self._format_debug(content)
            else:
                # Default to clean mode
                self._format_clean(content)
                
        except Exception as e:
            self.progress_display.hide_processing()
            self.error_handler.handle_formatting_error(str(e), ExtractedContent())
    
    def _format_clean(self, content: ExtractedContent) -> None:
        """Format response in clean mode - minimal, user-friendly display."""
        if not content.text:
            self.console.print(self.color_formatter.format_warning("No response content available."))
            return
        
        # Show main response
        self.console.print(self.color_formatter.format_header("Assistant: "), end="")
        
        # Truncate content if needed
        display_text = self.content_truncator.truncate_content(content.text)
        self.console.print(self.color_formatter.format_content(display_text))
        
        # Show interaction hints
        hints = self.interactive_display.create_interaction_hints()
        if hints.plain:
            self.console.print()
            self.console.print(hints)
    
    def _format_verbose(self, content: ExtractedContent) -> None:
        """Format response in verbose mode - includes reasoning and usage stats."""
        # Show mode indicator
        mode_indicator = self.interactive_display.create_mode_indicator()
        self.console.print(f"Response {mode_indicator}")
        self.console.print(create_separator())
        
        # Main content
        if content.text:
            content_panel = Panel(
                self.color_formatter.format_content(content.text),
                title="Assistant Response",
                border_style="cyan",
                box=box.ROUNDED
            )
            self.console.print(content_panel)
        
        # Additional sections
        sections = []
        
        # Reasoning section
        if content.reasoning:
            reasoning_section = self.interactive_display.create_expandable_section(
                "Reasoning", content.reasoning, expanded=False, style="blue"
            )
            sections.append(reasoning_section)
        
        # Usage statistics
        if content.usage:
            usage_table = self.table_formatter.create_usage_table(content.usage)
            usage_section = Panel(
                usage_table,
                title="📊 Usage Statistics",
                border_style="magenta",
                box=box.ROUNDED
            )
            sections.append(usage_section)
        
        # Show sections
        if sections:
            self.console.print()
            for section in sections:
                self.console.print(section)
        
        # Cost calculation
        if content.usage and content.model and self.config.display.enable_cost_tracking:
            cost = calculate_cost(content.usage, content.model)
            if cost:
                self.console.print()
                cost_text = f"💰 Estimated cost: ${cost:.4f}"
                self.console.print(self.color_formatter.format_usage(cost_text))
        
        # Interaction hints
        self.console.print()
        hints = self.interactive_display.create_interaction_hints()
        if hints.plain:
            self.console.print(hints)
    
    def _format_debug(self, content: ExtractedContent) -> None:
        """Format response in debug mode - includes all technical details."""
        # Show mode indicator
        mode_indicator = self.interactive_display.create_mode_indicator()
        self.console.print(f"Response {mode_indicator}")
        self.console.print(create_separator())
        
        # Main content with metadata
        if content.text:
            content_panel = Panel(
                self.color_formatter.format_content(content.text),
                title="Assistant Response",
                border_style="cyan",
                box=box.ROUNDED
            )
            self.console.print(content_panel)
        
        # Technical details in columns
        debug_sections = []
        
        # Model and timestamp info
        if content.model or content.timestamp:
            info_lines = []
            if content.model:
                info_lines.append(f"Model: {content.model}")
            if content.timestamp:
                info_lines.append(f"Timestamp: {format_timestamp(content.timestamp)}")
            
            info_panel = Panel(
                "\n".join(info_lines),
                title="🔧 Model Info",
                border_style="dim",
                box=box.ROUNDED
            )
            debug_sections.append(info_panel)
        
        # Usage statistics
        if content.usage:
            usage_table = self.table_formatter.create_usage_table(content.usage)
            usage_panel = Panel(
                usage_table,
                title="📊 Usage Statistics",
                border_style="magenta",
                box=box.ROUNDED
            )
            debug_sections.append(usage_panel)
        
        # Metadata
        if content.metadata:
            metadata_table = self.table_formatter.create_metadata_table(content.metadata)
            metadata_panel = Panel(
                metadata_table,
                title="📋 Metadata",
                border_style="blue",
                box=box.ROUNDED
            )
            debug_sections.append(metadata_panel)
        
        # Show debug sections in columns if multiple
        if debug_sections:
            self.console.print()
            if len(debug_sections) > 1:
                columns = Columns(debug_sections, equal=True, expand=True)
                self.console.print(columns)
            else:
                self.console.print(debug_sections[0])
        
        # Reasoning section
        if content.reasoning:
            self.console.print()
            reasoning_panel = Panel(
                self.color_formatter.format_reasoning(content.reasoning),
                title="🧠 Reasoning",
                border_style="blue",
                box=box.ROUNDED
            )
            self.console.print(reasoning_panel)
        
        # Raw response (truncated)
        if content.raw_response:
            self.console.print()
            try:
                if hasattr(content.raw_response, '__dict__'):
                    raw_dict = content.raw_response.__dict__
                    raw_text = json.dumps(raw_dict, indent=2, default=str)
                else:
                    raw_text = str(content.raw_response)
                
                # Truncate very long raw responses
                if len(raw_text) > 2000:
                    raw_text = raw_text[:2000] + "\n... (truncated)"
                
                raw_panel = Panel(
                    self.color_formatter.format_technical(raw_text),
                    title="🔍 Raw Response",
                    border_style="dim",
                    box=box.ROUNDED
                )
                self.console.print(raw_panel)
            except Exception as e:
                error_text = f"Could not serialize raw response: {e}"
                self.console.print(self.color_formatter.format_error(error_text))
        
        # Cost calculation
        if content.usage and content.model and self.config.display.enable_cost_tracking:
            cost = calculate_cost(content.usage, content.model)
            if cost:
                self.console.print()
                cost_text = f"💰 Estimated cost: ${cost:.4f}"
                self.console.print(self.color_formatter.format_usage(cost_text))
        
        # Interaction hints
        self.console.print()
        hints = self.interactive_display.create_interaction_hints()
        if hints.plain:
            self.console.print(hints)


# Convenience functions for easy integration
def format_response(response: Any, mode: str = "clean", console: Optional[Console] = None):
    """Format an OpenAI response with the specified mode."""
    formatter = ResponseFormatter(console=console, mode=mode)
    formatter.format_response(response)


def create_formatter(mode: str = "clean", console: Optional[Console] = None) -> ResponseFormatter:
    """Create a response formatter instance."""
    return ResponseFormatter(console=console, mode=mode)