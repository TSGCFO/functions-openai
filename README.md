# OpenAI Function Calling Examples

This repository contains example Python scripts that demonstrate how to call
Microsoft Graph API functions from an OpenAI chat model and how to interact
with the OpenAI API through a simple command line interface.

## Files

- `graph_functions.py` &mdash; Implements several helper functions for the
  Microsoft Graph API and a sample routine that uses OpenAI function calling to
  invoke them.
- `openai_config.py` &mdash; Provides a configured `OpenAI` client as well as an
  example request showing how tools can be supplied to the API.
- `chat_cli.py` &mdash; A minimal CLI chat interface built on top of
  `openai_config`.

## Setup

1. Create a Python virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install openai requests
   ```
2. Set the required environment variables for your credentials:
   ```bash
   export OPENAI_API_KEY=your-openai-key
   export TENANT_ID=your-tenant-id
   export CLIENT_ID=your-client-id
   export CLIENT_SECRET=your-client-secret
   ```
3. Run any of the example scripts, for instance:
   ```bash
   python chat_cli.py
   ```

The scripts expect valid credentials to communicate with both the OpenAI API
and Microsoft Graph.
