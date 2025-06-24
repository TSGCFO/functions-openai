import openai
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# 🔒 Your Microsoft Graph OAuth credentials
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
GRAPH_SCOPE = os.getenv("GRAPH_SCOPE")
GRAPH_API_BASE = os.getenv("GRAPH_API_BASE")

# 🔐 OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# 🔑 Get Microsoft Graph Access Token
def get_graph_token():
    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": GRAPH_SCOPE
    }
    
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Error getting token: {response.status_code}")
        print(response.text)
        return None

# 📧 Function to list emails from Outlook
def listEmails():
    access_token = get_graph_token()
    if not access_token:
        return {"error": "Failed to get access token"}
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Get emails from the user's mailbox
    url = f"{GRAPH_API_BASE}/me/messages"
    params = {
        "$top": 10,  # Limit to 10 emails
        "$select": "subject,from,receivedDateTime,bodyPreview",
        "$orderby": "receivedDateTime desc"
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        emails = response.json().get("value", [])
        formatted_emails = []
        
        for email in emails:
            formatted_email = {
                "subject": email.get("subject", "No Subject"),
                "from": email.get("from", {}).get("emailAddress", {}).get("address", "Unknown"),
                "receivedDateTime": email.get("receivedDateTime", "Unknown"),
                "bodyPreview": email.get("bodyPreview", "No preview available")[:100] + "..." if len(email.get("bodyPreview", "")) > 100 else email.get("bodyPreview", "")
            }
            formatted_emails.append(formatted_email)
        
        return {"emails": formatted_emails}
    else:
        return {"error": f"Failed to get emails: {response.status_code} - {response.text}"}

# 📤 Function to send email
def sendEmail(to, subject, body):
    access_token = get_graph_token()
    if not access_token:
        return {"error": "Failed to get access token"}
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    email_data = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": to
                    }
                }
            ]
        },
        "saveToSentItems": "true"
    }
    
    url = f"{GRAPH_API_BASE}/me/sendMail"
    response = requests.post(url, headers=headers, json=email_data)
    
    if response.status_code == 202:
        return {"success": "Email sent successfully"}
    else:
        return {"error": f"Failed to send email: {response.status_code} - {response.text}"}

# 📝 Function to create email draft
def createDraft(to, subject, body):
    access_token = get_graph_token()
    if not access_token:
        return {"error": "Failed to get access token"}
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    draft_data = {
        "subject": subject,
        "body": {
            "contentType": "Text",
            "content": body
        },
        "toRecipients": [
            {
                "emailAddress": {
                    "address": to
                }
            }
        ]
    }
    
    url = f"{GRAPH_API_BASE}/me/messages"
    response = requests.post(url, headers=headers, json=draft_data)
    
    if response.status_code == 201:
        draft = response.json()
        return {"success": "Draft created successfully", "draftId": draft.get("id")}
    else:
        return {"error": f"Failed to create draft: {response.status_code} - {response.text}"}

# 📅 Function to list calendar events
def listCalendarEvents():
    access_token = get_graph_token()
    if not access_token:
        return {"error": "Failed to get access token"}
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    url = f"{GRAPH_API_BASE}/me/events"
    params = {
        "$top": 10,
        "$select": "subject,start,end,location",
        "$orderby": "start/dateTime asc"
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        events = response.json().get("value", [])
        return {"events": events}
    else:
        return {"error": f"Failed to get calendar events: {response.status_code} - {response.text}"}

# ⚙️ Function to get mailbox settings
def getMailboxSettings():
    access_token = get_graph_token()
    if not access_token:
        return {"error": "Failed to get access token"}
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    url = f"{GRAPH_API_BASE}/me/mailboxSettings"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        settings = response.json()
        return {"settings": settings}
    else:
        return {"error": f"Failed to get mailbox settings: {response.status_code} - {response.text}"}

# 🔄 Function to create email forwarding rule
def createForwardingRule(forwardTo, conditions=None):
    access_token = get_graph_token()
    if not access_token:
        return {"error": "Failed to get access token"}
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    rule_data = {
        "displayName": "Auto Forward Rule",
        "isEnabled": True,
        "actions": {
            "forwardTo": [
                {
                    "emailAddress": {
                        "address": forwardTo
                    }
                }
            ]
        }
    }
    
    # Add conditions if provided
    if conditions:
        rule_data["conditions"] = conditions
    
    url = f"{GRAPH_API_BASE}/me/mailFolders/inbox/messageRules"
    response = requests.post(url, headers=headers, json=rule_data)
    
    if response.status_code == 201:
        rule = response.json()
        return {"success": "Forwarding rule created successfully", "ruleId": rule.get("id")}
    else:
        return {"error": f"Failed to create forwarding rule: {response.status_code} - {response.text}"}