from openai import OpenAI

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


def main():
    client = OpenAI()
    messages = [DEVELOPER_MESSAGE]
    print("Type 'quit' to exit.\n")
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in {"quit", "exit"}:
            break
        messages.append({"role": "user", "content": user_input})
        response = client.responses.create(
            model="o3",
            input=messages,
            text={"format": {"type": "text"}},
            reasoning={"effort": "medium", "summary": "auto"},
            tools=TOOLS,
            store=True,
        )
        print("Assistant:", response)
        messages.append({"role": "assistant", "content": str(response)})


if __name__ == "__main__":
    main()
