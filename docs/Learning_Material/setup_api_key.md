# OpenAI API Key Setup Instructions

## 🔑 Getting Your OpenAI API Key

1. **Go to OpenAI Platform**: https://platform.openai.com/api-keys
2. **Sign in** to your OpenAI account
3. **Create a new API key**:
   - Click "Create new secret key"
   - Give it a name (e.g., "NPCL Voice Assistant")
   - Copy the key (starts with `sk-`)

## 🛠️ Setting Up the API Key

### Method 1: Environment Variable
```bash
export OPENAI_API_KEY="sk-your-actual-api-key-here"
```

### Method 2: Update .env file
```bash
# Edit .env file
nano .env

# Replace this line:
OPENAI_API_KEY=sk-your-valid-openai-api-key-here

# With your actual key:
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

### Method 3: Add to shell profile
```bash
echo 'export OPENAI_API_KEY="sk-your-actual-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

## ✅ Verify Setup
```bash
# Check if key is set
echo $OPENAI_API_KEY

# Test the key
python3 -c "
import openai
client = openai.OpenAI()
try:
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': 'Hello'}],
        max_tokens=5
    )
    print('✅ API key is working!')
except Exception as e:
    print(f'❌ API key error: {e}')
"
```

## 🚀 Next Steps
1. Set your API key using one of the methods above
2. Run: `./quick_test_macos.sh`
3. Run: `./migration_test_macos.sh`
4. Start the assistant: `python src/main.py`