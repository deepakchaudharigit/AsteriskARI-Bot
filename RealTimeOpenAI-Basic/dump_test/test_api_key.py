#!/usr/bin/env python3
"""
Test OpenAI API key from .env file
"""

import os
import sys
from dotenv import load_dotenv
import openai

def test_api_key():
    # Clear any existing environment variable
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']
    
    # Load from .env file
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"API Key from .env: {api_key[:20]}...{api_key[-10:]}")
    print(f"API Key length: {len(api_key)}")
    
    # Test the API key
    try:
        client = openai.OpenAI(api_key=api_key)
        
        # Simple test request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        print("✅ API key is working!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        return False

if __name__ == "__main__":
    test_api_key()