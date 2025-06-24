from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.responses.create(
  model="o3",
  input=[
    {
      "role": "developer",
      "content": [
        {
          "type": "input_text",
          "text": "Manage email and password-related tasks for maintaining an Outlook mailbox.\n\nFocus on managing emails, organizing folders, and handling password updates securely. \n\n# Steps\n\n1. **Email Management:**\n   - Sort incoming emails into relevant folders based on sender or subject.\n   - Flag important emails for follow-up.\n   - Delete or archive emails that are no longer needed.\n   \n2. **Folder Organization:**\n   - Create and name folders for specific projects or clients.\n   - Move emails into respective folders for easy retrieval.\n   \n3. **Password Management:**\n   - Ensure that passwords are strong and updated regularly.\n   - Use a password manager for secure storage or provide guidance on password creation.\n   \n4. **Security Practices:**\n   - Enable two-factor authentication.\n   - Watch for and report any suspicious emails.\n"
        }
      ]
    }
  ],
  text={
    "format": {
      "type": "text"
    }
  },
  reasoning={
    "effort": "medium",
    "summary": "auto"
  },
  tools=[
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
            "enum": [
              "h.sadiq@tsgfulfillment.com"
            ],
            "default": "h.sadiq@tsgfulfillment.com"
          },
          "top": {
            "type": "integer",
            "description": "The number of email messages to retrieve.",
            "default": 10
          }
        },
        "required": [
          "userId"
        ]
      },
      "strict": False
    }
  ],
  store=True
)

