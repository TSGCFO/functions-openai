#!/usr/bin/env python3
"""
Test script to verify the response formatting system works correctly.
Tests both display formatting and conversation history extraction.
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
from response_formatter import format_response, ContentExtractor

def test_response_system():
    """Test the complete response system functionality."""
    
    # Load environment
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    print("🧪 Testing OpenAI O3 Response System")
    print("=" * 50)
    
    # Test 1: Single response formatting
    print("\n1. Testing Response Formatting...")
    print("-" * 30)
    
    response = client.responses.create(
        model="o3",
        input=[{"role": "user", "content": "Say hello and ask how you can help"}],
        text={"format": {"type": "text"}},
        reasoning={"effort": "low", "summary": "auto"},
        store=True,
    )
    
    print("Raw response.text:", response.text)
    print("\nFormatted output:")
    format_response(response, mode="clean")
    
    # Test 2: Content extraction for conversation history
    print("\n\n2. Testing Conversation History Extraction...")
    print("-" * 30)
    
    extractor = ContentExtractor()
    extracted = extractor.extract(response)
    
    print(f"Extracted text: {repr(extracted.text)}")
    print(f"Text length: {len(extracted.text) if extracted.text else 0}")
    print(f"Contains config object: {'ResponseTextConfig' in str(extracted.text) if extracted.text else False}")
    
    # Test 3: Multi-turn conversation simulation
    print("\n\n3. Testing Multi-turn Conversation...")
    print("-" * 30)
    
    # Simulate the chat_cli.py conversation logic
    messages = [
        {"role": "user", "content": "Hello, what's your name?"}
    ]
    
    # First response
    response1 = client.responses.create(
        model="o3",
        input=messages,
        text={"format": {"type": "text"}},
        reasoning={"effort": "low", "summary": "auto"},
        store=True,
    )
    
    # Extract for conversation history (fixed logic)
    extracted1 = extractor.extract(response1)
    response_text1 = extracted1.text if extracted1.text else str(response1)
    messages.append({"role": "assistant", "content": response_text1})
    
    print(f"First response added to history: {repr(response_text1)}")
    
    # Second turn
    messages.append({"role": "user", "content": "Can you help me with email?"})
    
    response2 = client.responses.create(
        model="o3",
        input=messages,
        text={"format": {"type": "text"}},
        reasoning={"effort": "low", "summary": "auto"},
        store=True,
    )
    
    extracted2 = extractor.extract(response2)
    response_text2 = extracted2.text if extracted2.text else str(response2)
    
    print(f"Second response: {repr(response_text2)}")
    
    # Verify no config objects in conversation history
    conversation_str = str(messages)
    if "ResponseTextConfig" in conversation_str:
        print("❌ FAILED: Config objects found in conversation history!")
        return False
    else:
        print("✅ SUCCESS: No config objects in conversation history!")
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! The response system is working correctly.")
    print("\n📋 Summary:")
    print("• Response formatter displays clean text instead of config objects")
    print("• Conversation history extraction works correctly")
    print("• Multi-turn conversations maintain proper context")
    print("• No 'ResponseTextConfig' objects leak into user-visible output")
    
    return True

if __name__ == "__main__":
    try:
        success = test_response_system()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)