# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based CLI chat application that integrates OpenAI's o3 model with Microsoft Graph API for email management. The application provides an interactive chat interface where users can manage Outlook emails through natural language commands.

## OpenAI API Integration

**IMPORTANT**: This project exclusively uses OpenAI's **Responses API** (not the legacy Chat Completions API). All conversations and tasks must use:

- **API Endpoint**: `/chat/responses` (Responses API)
- **Model**: `o3` (OpenAI's o3 model)
- **Legacy Chat Completions API**: NOT USED - this project has migrated away from `/chat/completions`

All code implementations should follow the Responses API patterns and use the o3 model for optimal performance and feature compatibility.

## Architecture

The codebase consists of three main Python files:

1. **chat_cli.py** - Main CLI application with interactive chat loop
   - Uses OpenAI's Responses API with o3 model exclusively
   - Implements function calling for email operations
   - Contains developer instructions for email/password management tasks

2. **ms_graph_functions.py** - Microsoft Graph API integration
   - Handles OAuth authentication with Microsoft
   - Implements various email operations (list, send, draft management)
   - Includes calendar event management functions
   - Contains mailbox settings and forwarding rule management

3. **openai_response.py** - OpenAI Responses API example
   - Demonstrates proper usage of OpenAI's Responses API (not Chat Completions)
   - Uses o3 model exclusively
   - Contains the same developer instructions as the CLI

## Key Integration Points

- **OpenAI Responses API**: All OpenAI interactions use the Responses API endpoint with o3 model
- **Function Calling**: The CLI uses OpenAI's function calling feature (via Responses API) with a `listEmails` function that connects to Microsoft Graph API
- **Authentication**: Microsoft Graph authentication uses client credentials flow with hardcoded tenant/client IDs
- **Email Management**: The system is designed to handle email organization, password management, and security practices through conversational AI powered by o3

## Development Commands

### Running the Application

```bash
python chat_cli.py
```

### Dependencies

The project requires:

- `openai` - OpenAI Python SDK (configured for Responses API with o3 model)
- `requests` - HTTP requests for Microsoft Graph API

### Authentication Setup

The application uses Microsoft Graph OAuth with client credentials. The credentials are currently hardcoded in `ms_graph_functions.py` and need to be updated for different environments.

## Security Considerations

- API keys and credentials are currently hardcoded and should be moved to environment variables
- The application handles sensitive email data and requires proper authentication
- Two-factor authentication and security practices are part of the core functionality

## Function Implementations

The `ms_graph_functions.py` contains implementations for:

- Email listing and sending
- Draft management
- Calendar event operations
- Mailbox settings configuration
- Forwarding rule creation

Each function follows the Microsoft Graph API patterns and returns JSON responses.

## General Response Guidelines

Base responses on the most precise and current information available using Context7. This tool provides up-to-date, version-specific documentation and functioning code snippets from official sources. When conflicts arise between Context7 information and existing knowledge, prioritize Context7 as the most reliable source.

### Workflow

1. Access Context7 and retrieve current documentation for the topic
2. Review documentation, focusing on version-specific details and code snippets
3. Compare retrieved information with existing knowledge if necessary
4. Integrate Context7 information when discrepancies arise

### Output Requirements

Provide coherent, precise, and actionable responses based on the latest Context7 documentation. Include:

- Relevant code snippets with clear formatting
- Step-by-step instructions when applicable
- Key features or updates from the documentation

### Example

**Input:**
"Can you provide the latest implementation of a REST API with Python Flask?"

**Output Process:**

1. Retrieve most recent official Flask documentation via Context7
2. Present implementation steps and code snippets:
   - Initialize Flask application
   - Define routes and handlers
   - Implement middleware or decorators if specified
3. Summarize key features or updates from documentation
