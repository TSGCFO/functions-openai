from openai import OpenAI
import os
import argparse
from dotenv import load_dotenv
from response_formatter import format_response
from config import get_config, update_display_mode

# Load environment variables from .env file
load_dotenv()

# Developer instructions and tool configuration from openai_response.py
DEVELOPER_MESSAGE = {
    "role": "developer",
    "content": [
        {
            "type": "input_text",
            "text": (
                "Manage email and password-related tasks for maintaining an Outlook mailbox.\n\n"
                "Focus on managing emails, organizing folders, and handling password updates securely. \n\n"
                "# Steps\n\n"
                "1. **Email Management:**\n"
                "   - Sort incoming emails into relevant folders based on sender or subject.\n"
                "   - Flag important emails for follow-up.\n"
                "   - Delete or archive emails that are no longer needed.\n\n"
                "2. **Folder Organization:**\n"
                "   - Create and name folders for specific projects or clients.\n"
                "   - Move emails into respective folders for easy retrieval.\n\n"
                "3. **Password Management:**\n"
                "   - Ensure that passwords are strong and updated regularly.\n"
                "   - Use a password manager for secure storage or provide guidance on password creation.\n\n"
                "4. **Security Practices:**\n"
                "   - Enable two-factor authentication.\n"
                "   - Watch for and report any suspicious emails.\n\n"
                "# Output Format\n\n"
                "Provide task completion reports in a paragraph format, detailing steps taken and outcomes."
                " When necessary for password instructions, specify guidelines in a bullet point format for clarity.\n\n"
                "# Examples\n\n"
                "**Example 1: Email Organization**\n"
                "- **Task:** An email from [Client Name] regarding [Project Name] required organization.\n"
                "- **Steps Taken:** Moved to `[Project Name]` folder, flagged for review, archived irrelevant messages.\n"
                "- **Outcome:** Email neatly organized; important email flagged for prompt response.\n\n"
                "**Example 2: Password Management**\n"
                "- **Task:** Update password policy.\n"
                "- **Steps Taken:** Updated passwords to include at least 12 characters, with a mix of letters, numbers, and symbols.\n"
                "- **Outcome:** Passwords strengthened and stored securely in a password manager.\n\n"
                "# Notes\n\n"
                "- Ensure frequent backup of important emails.\n"
                "- Regularly check for unauthorized access or phishing attempts.\n"
                "- Document any changes to password policy or email organization for reference.\n\n"
                "Remember, this management role requires a balance between efficiency and security,"
                " ensuring the Outlook mailbox runs smoothly while maintaining strict security measures."
            )
        }
    ]
}

TOOLS = [
    {
        "type": "function",
        "name": "listEmails",
        "description": "List recent emails from a user's Outlook mailbox using Microsoft Graph API.",
        "parameters": {
            "type": "object",
            "properties": {
                "userId": {
                    "type": "string",
                    "description": "The email address of the user whose mailbox will be accessed.",
                    "enum": ["h.sadiq@tsgfulfillment.com"],
                    "default": "h.sadiq@tsgfulfillment.com",
                },
                "top": {
                    "type": "integer",
                    "description": "The number of email messages to retrieve.",
                    "default": 10,
                },
            },
            "required": ["userId"],
        },
        "strict": False,
    }
]


def parse_arguments():
    """Parse command line arguments for display mode configuration."""
    parser = argparse.ArgumentParser(
        description="OpenAI Chat CLI with user-friendly response formatting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Display Modes:
  clean   - Show only assistant response with minimal formatting (default)
  verbose - Include reasoning summary and usage statistics
  debug   - Show all technical details and raw response data

Interactive Mode:
  When enabled, use keyboard shortcuts to switch modes:
  'c' = clean mode    'v' = verbose mode    'd' = debug mode
  'r' = show reasoning    space = expand/collapse sections
        """
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["clean", "verbose", "debug"],
        default=None,
        help="Display mode for responses (overrides config file)"
    )
    
    parser.add_argument(
        "--no-colors",
        action="store_true",
        help="Disable colored output"
    )
    
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Disable interactive keyboard shortcuts"
    )
    
    parser.add_argument(
        "--no-cost-tracking",
        action="store_true",
        help="Disable cost estimation display"
    )
    
    return parser.parse_args()


def apply_cli_overrides(args):
    """Apply command line argument overrides to configuration."""
    config = get_config()
    
    # Apply display mode override
    if args.mode:
        update_display_mode(args.mode)
    
    # Apply other overrides (would need config update methods)
    if args.no_colors:
        config.display.enable_colors = False
    
    if args.no_interactive:
        config.display.enable_interactive = False
        
    if args.no_cost_tracking:
        config.display.enable_cost_tracking = False


def main():
    """Main chat CLI function with enhanced response formatting."""
    # Parse command line arguments
    args = parse_arguments()
    apply_cli_overrides(args)
    
    # Get current configuration
    config = get_config()
    display_mode = args.mode or config.display.default_mode
    
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    messages = [DEVELOPER_MESSAGE]
    
    # Welcome message with mode information
    welcome_text = f"OpenAI Chat CLI - Response Mode: {display_mode.upper()}"
    if config.display.enable_interactive:
        welcome_text += " (Interactive shortcuts enabled)"
    
    print(welcome_text)
    print("Type 'quit' or 'exit' to end the session.")
    if config.display.enable_interactive:
        print("Press 'c/v/d' to switch display modes during conversation.")
    print("-" * 60)
    print()
    
    # Main chat loop
    while True:
        try:
            user_input = input("You: ")
            
            if user_input.strip().lower() in {"quit", "exit"}:
                print("Goodbye!")
                break
            
            if not user_input.strip():
                continue
                
            # Add user message to conversation
            messages.append({"role": "user", "content": user_input})
            
            # Get response from OpenAI
            response = client.responses.create(
                model="o3",
                input=messages,
                text={"format": {"type": "text"}},
                reasoning={"effort": "medium", "summary": "auto"},
                tools=TOOLS,
                store=True,
            )
            
            # Format and display the response using the new formatter
            format_response(response, mode=display_mode)
            
            # Add assistant response to conversation history
            # Extract the actual response text for conversation context using the same extractor
            from response_formatter import ContentExtractor
            try:
                extractor = ContentExtractor()
                extracted = extractor.extract(response)
                
                # Use the extracted text if available, otherwise fall back to string representation
                if extracted.text:
                    response_text = extracted.text
                else:
                    response_text = str(response)
                
                messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                # Fallback to string representation if extraction fails
                messages.append({"role": "assistant", "content": str(response)})
            
            print()  # Add spacing between responses
            
        except KeyboardInterrupt:
            print("\n\nSession interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError occurred: {e}")
            print("Please try again or type 'quit' to exit.\n")


if __name__ == "__main__":
    main()
