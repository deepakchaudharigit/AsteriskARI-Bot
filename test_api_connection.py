#!/usr/bin/env python3
"""
Test OpenAI API connectivity
"""
import os
import sys

def test_api_connection():
    """Test OpenAI API connection"""
    
    # Check if API key is set
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("Set it with: export OPENAI_API_KEY='sk-your-key-here'")
        return False
    
    # Check API key format
    if not api_key.startswith('sk-'):
        print(f"❌ Invalid API key format: {api_key[:10]}...")
        print("OpenAI API keys should start with 'sk-'")
        return False
    
    print(f"✅ API key format is correct: {api_key[:10]}...")
    
    # Test OpenAI import
    try:
        import openai
        print(f"✅ OpenAI library imported successfully (v{openai.__version__})")
    except ImportError:
        print("❌ OpenAI library not installed")
        print("Install with: pip install openai")
        return False
    
    # Test API connection
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'API test successful'"}],
            max_tokens=10
        )
        
        if response.choices and response.choices[0].message.content:
            print(f"✅ API connection successful!")
            print(f"Response: {response.choices[0].message.content}")
            return True
        else:
            print("❌ API response was empty")
            return False
            
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🔗 Testing OpenAI API Connection")
    print("=" * 40)
    
    success = test_api_connection()
    
    print("=" * 40)
    if success:
        print("🎉 API connection test PASSED!")
        print("You can now run the voice assistant")
    else:
        print("❌ API connection test FAILED!")
        print("Please fix the issues above and try again")
    
    sys.exit(0 if success else 1)
