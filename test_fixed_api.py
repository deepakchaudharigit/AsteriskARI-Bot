#!/usr/bin/env python3
"""
Test OpenAI API with the correct key
"""
import os

# Set the API key directly
os.environ['OPENAI_API_KEY'] = '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'

def test_api_connection():
    """Test OpenAI API connection"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"🔑 API Key: {api_key[:20]}...")
    
    # Check API key format
    if not api_key.startswith('sk-'):
        print(f"❌ Invalid API key format")
        return False
    
    print(f"✅ API key format is correct")
    
    # Test OpenAI import
    try:
        import openai
        print(f"✅ OpenAI library imported successfully (v{openai.__version__})")
    except ImportError:
        print("❌ OpenAI library not installed")
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
        print("✅ You can now run the voice assistant")
    else:
        print("❌ API connection test FAILED!")
        print("Please check your API key and try again")