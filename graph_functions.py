import json
import os
import requests
import openai

# Microsoft Graph OAuth credentials from environment variables
TENANT_ID = os.getenv("TENANT_ID", "your-tenant-id")
CLIENT_ID = os.getenv("CLIENT_ID", "your-client-id")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "your-client-secret")
GRAPH_SCOPE = "https://graph.microsoft.com/.default"
GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"

# OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY", "sk-your-openai-key")


def get_graph_token():
    """Retrieve a Microsoft Graph access token."""
    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": GRAPH_SCOPE,
    }
    response = requests.post(token_url, data=data, timeout=30)
    response.raise_for_status()
    return response.json().get("access_token")


def handle_function_call(function_name: str, arguments: dict):
    """Call Microsoft Graph API based on the provided function name."""
    token = get_graph_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    user_id = arguments.get("userId", "h.sadiq@tsgfulfillment.com")

    if function_name == "listEmails":
        top = arguments.get("top", 10)
        url = f"{GRAPH_API_BASE}/users/{user_id}/messages?$top={top}"
        r = requests.get(url, headers=headers, timeout=30)
        return r.json()

    elif function_name == "sendEmail":
        to = arguments["to"]
        recipients = [{"emailAddress": {"address": email}} for email in to]
        payload = {
            "message": {
                "subject": arguments["subject"],
                "body": {
                    "contentType": arguments.get("bodyType", "Text"),
                    "content": arguments["body"],
                },
                "toRecipients": recipients,
            },
            "saveToSentItems": arguments.get("saveToSentItems", True),
        }
        url = f"{GRAPH_API_BASE}/users/{user_id}/sendMail"
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        return {"status": "sent" if r.status_code == 202 else r.text}

    elif function_name == "createDraft":
        to = arguments["to"]
        recipients = [{"emailAddress": {"address": email}} for email in to]
        payload = {
            "subject": arguments["subject"],
            "body": {
                "contentType": arguments.get("bodyType", "Text"),
                "content": arguments["body"],
            },
            "toRecipients": recipients,
        }
        url = f"{GRAPH_API_BASE}/users/{user_id}/messages"
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        return r.json()

    elif function_name == "sendDraft":
        message_id = arguments["messageId"]
        url = f"{GRAPH_API_BASE}/users/{user_id}/messages/{message_id}/send"
        r = requests.post(url, headers=headers, timeout=30)
        return {"status": "sent" if r.status_code == 202 else r.text}

    elif function_name == "listDrafts":
        url = f"{GRAPH_API_BASE}/users/{user_id}/mailFolders/drafts/messages"
        r = requests.get(url, headers=headers, timeout=30)
        return r.json()

    elif function_name == "listCalendarEvents":
        top = arguments.get("top", 10)
        url = f"{GRAPH_API_BASE}/users/{user_id}/events?$top={top}"
        r = requests.get(url, headers=headers, timeout=30)
        return r.json()

    elif function_name == "createCalendarEvent":
        attendees = [
            {"emailAddress": {"address": email}, "type": "required"}
            for email in arguments.get("attendees", [])
        ]
        payload = {
            "subject": arguments["subject"],
            "start": {
                "dateTime": arguments["startDateTime"],
                "timeZone": arguments.get("timeZone", "Eastern Standard Time"),
            },
            "end": {
                "dateTime": arguments["endDateTime"],
                "timeZone": arguments.get("timeZone", "Eastern Standard Time"),
            },
            "body": {"contentType": "Text", "content": arguments.get("body", "")},
            "attendees": attendees,
        }
        url = f"{GRAPH_API_BASE}/users/{user_id}/events"
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        return r.json()

    elif function_name == "updateMailboxSettings":
        payload = {
            "timeZone": arguments.get("timeZone", "Eastern Standard Time"),
            "automaticRepliesSetting": {
                "status": arguments.get("autoReplyStatus", "disabled"),
                "externalReplyMessage": arguments.get("autoReplyMessage", ""),
            },
        }
        url = f"{GRAPH_API_BASE}/users/{user_id}/mailboxSettings"
        r = requests.patch(url, headers=headers, json=payload, timeout=30)
        return r.json()

    elif function_name == "createForwardingRule":
        forward_to = [
            {"emailAddress": {"address": addr}} for addr in arguments["forwardTo"]
        ]
        payload = {
            "displayName": "GPT Forwarding Rule",
            "sequence": 1,
            "isEnabled": True,
            "conditions": {"senderContains": arguments.get("senderContains", [])},
            "actions": {"forwardTo": forward_to},
        }
        url = f"{GRAPH_API_BASE}/users/{user_id}/mailFolders/inbox/messageRules"
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        return r.json()

    else:
        return {"error": f"Function '{function_name}' is not implemented."}


def run_openai_chat():
    """Simple example that lets OpenAI choose a Microsoft Graph function."""
    functions = json.load(open("functions.json")) if os.path.exists("functions.json") else []
    messages = [{"role": "user", "content": "Show my last 5 emails"}]

    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=messages,
        functions=functions,
        function_call="auto",
    )

    tool_call = response.choices[0].message.get("function_call")
    if tool_call:
        name = tool_call["name"]
        args = json.loads(tool_call["arguments"])
        result = handle_function_call(name, args)
        print(f"Function result for '{name}':\n", json.dumps(result, indent=2))
    else:
        print("No function call suggested by model.")


if __name__ == "__main__":
    run_openai_chat()
