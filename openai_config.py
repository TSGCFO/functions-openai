from openai import OpenAI

# Instantiate the OpenAI client. The API key should be provided via the
# OPENAI_API_KEY environment variable for security reasons.
client = OpenAI()

# Example request demonstrating how tools could be passed to the API. This is
# based on the second snippet provided in the instructions.
EXAMPLE_PROMPT = {
    "role": "developer",
    "content": [
        {
            "type": "input_text",
            "text": (
                "Manage email and password-related tasks for maintaining an Outlook "
                "mailbox.\n\nFocus on managing emails, organizing folders, and handling "
                "password updates securely."
            ),
        }
    ],
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


def example_response():
    """Run an example API call to illustrate configuration."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[EXAMPLE_PROMPT],
        tools=TOOLS,
    )
    return response


if __name__ == "__main__":
    print(example_response())
