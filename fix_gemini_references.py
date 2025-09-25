#!/usr/bin/env python3
"""
Complete Gemini/Google Reference Removal Script
Removes all traces of Gemini and Google API references from the project
"""

import os
import re
import glob
from pathlib import Path

def fix_file_content(file_path, content):
    """Fix content by removing/replacing Gemini and Google references"""
    
    # Skip binary files and certain directories
    skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv'}
    if any(skip_dir in str(file_path) for skip_dir in skip_dirs):
        return content
    
    # Skip if not a text file
    try:
        content.encode('utf-8')
    except:
        return content
    
    original_content = content
    
    # Replace Gemini references with OpenAI
    replacements = [
        # API references
        (r'gemini[_-]voice[_-]assistant', 'openai-voice-assistant'),
        (r'OpenAIRealtimeClient', 'OpenAIRealtimeClient'),
        (r'OpenAIRealtimeConfig', 'OpenAIRealtimeConfig'),
        (r'MockOpenAIRealtimeAPI', 'MockOpenAIRealtimeAPI'),
        (r'MockOpenAIClient', 'MockOpenAIClient'),
        (r'openai_client', 'openai_client'),
        (r'openai_config', 'openai_config'),
        (r'openai_api', 'openai_api'),
        (r'openai_endpoint', 'openai_endpoint'),
        (r'openai_events', 'openai_events'),
        (r'openai_response', 'openai_response'),
        (r'openai_status', 'openai_status'),
        
        # Google API references
        (r'OPENAI_API_KEY', 'OPENAI_API_KEY'),
        (r'OPENAI_API_KEY', 'openai_api_key'),
        (r'your-openai-api-key-here', 'your-openai-api-key-here'),
        
        # Model references
        (r'gemini-[0-9.]*-flash[^"\']*', 'gpt-4o-mini'),
        (r'gemini-[0-9.]*-pro[^"\']*', 'gpt-4o-mini'),
        
        # Comments and documentation
        (r'# Using OpenAI for AI integration\\n]*', '# Using OpenAI for AI integration'),
        (r'OpenAI GPT-4 API', 'OpenAI GPT-4 API'),
        (r'OpenAI Realtime API', 'OpenAI Realtime API'),
        (r'OpenAI Whisper', 'OpenAI Whisper'),
        (r'OpenAI TTS', 'OpenAI TTS'),
        (r'OpenAI Text-to-Speech', 'OpenAI Text-to-Speech'),
        
        # URLs and endpoints
        (r'https://aistudio\.google\.com/', 'https://platform.openai.com/'),
        (r'wss://generativelanguage\.googleapis\.com/[^"\']*', 'wss://api.openai.com/v1/realtime'),
        
        # Import statements
        (r'# Removed Gemini import - using OpenAI
        (r'# Removed Gemini import - using OpenAI
        
        # Test and mock references
        (r'test_openai', 'test_openai'),
        (r'mock_openai', 'mock_openai'),
        (r'TEST_OPENAI_API_KEY', 'TEST_OPENAI_API_KEY'),
        
        # Function and method names
        (r'_handle_openai_', '_handle_openai_'),
        (r'openai_function', 'openai_function'),
        (r'to_openai_format', 'to_openai_format'),
        
        # Variable names in code
        (r'\\bgemini_\\w+', lambda m: m.group(0).replace('gemini_', 'openai_')),
        (r'\\bGemini\\w+', lambda m: m.group(0).replace('Gemini', 'OpenAI')),
    ]
    
    # Apply replacements
    for pattern, replacement in replacements:
        if callable(replacement):
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        else:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    # Special handling for specific file types
    if file_path.suffix == '.py':
        # Remove Gemini imports completely
        content = re.sub(r'^# Removed Gemini import - using OpenAI
        content = re.sub(r'^# Removed Gemini import - using OpenAI
        
        # Fix class inheritance
        content = re.sub(r'class.*\\(.*Gemini.*\\):', 
                        lambda m: m.group(0).replace('Gemini', 'OpenAI'), content)
    
    return content

def process_file(file_path):
    """Process a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = fix_file_content(file_path, content)
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Fixed: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function to process all files"""
    print("🧹 Removing all Gemini and Google API references...")
    
    # File patterns to process
    patterns = [
        '**/*.py',
        '**/*.md', 
        '**/*.txt',
        '**/*.conf',
        '**/*.yaml',
        '**/*.yml',
        '**/*.env*',
        '**/*.sh',
        '**/*.json'
    ]
    
    # Directories to skip
    skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'docs/Learning_Material'}
    
    files_processed = 0
    files_changed = 0
    
    for pattern in patterns:
        for file_path in Path('.').glob(pattern):
            # Skip directories we don't want to process
            if any(skip_dir in str(file_path) for skip_dir in skip_dirs):
                continue
                
            if file_path.is_file():
                files_processed += 1
                if process_file(file_path):
                    files_changed += 1
    
    print(f"\\n📊 Summary:")
    print(f"   Files processed: {files_processed}")
    print(f"   Files changed: {files_changed}")
    print(f"\\n🎉 Gemini/Google reference removal complete!")
    
    # Create a verification script
    create_verification_script()

def create_verification_script():
    """Create a script to verify all references are removed"""
    script_content = '''#!/usr/bin/env python3
"""
Verification script to check for remaining Gemini/Google references
"""

import os
import re
from pathlib import Path

def check_file(file_path):
    """Check a file for Gemini/Google references"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns to check for
        patterns = [
            r'\\bgemini\\b',
            r'\\bGemini\\b', 
            r'\\bGEMINI\\b',
            r'OPENAI_API_KEY',
            r'OPENAI_API_KEY',
            r'Google.*API',
            r'openai-voice-assistant',
            r'MockGemini',
            r'test_openai'
        ]
        
        issues = []
        for i, line in enumerate(content.split('\\n'), 1):
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(f"Line {i}: {line.strip()}")
        
        return issues
    except:
        return []

def main():
    """Check all files for remaining references"""
    print("🔍 Checking for remaining Gemini/Google references...")
    
    patterns = ['**/*.py', '**/*.md', '**/*.txt', '**/*.conf', '**/*.yaml', '**/*.yml']
    skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv'}
    
    total_issues = 0
    
    for pattern in patterns:
        for file_path in Path('.').glob(pattern):
            if any(skip_dir in str(file_path) for skip_dir in skip_dirs):
                continue
                
            if file_path.is_file():
                issues = check_file(file_path)
                if issues:
                    print(f"\\n⚠️  {file_path}:")
                    for issue in issues[:5]:  # Show first 5 issues
                        print(f"   {issue}")
                    if len(issues) > 5:
                        print(f"   ... and {len(issues) - 5} more")
                    total_issues += len(issues)
    
    if total_issues == 0:
        print("\\n✅ No Gemini/Google references found!")
    else:
        print(f"\\n❌ Found {total_issues} remaining references")

if __name__ == "__main__":
    main()
'''
    
    with open('verify_gemini_removal.py', 'w') as f:
        f.write(script_content)
    
    os.chmod('verify_gemini_removal.py', 0o755)
    print("📝 Created verification script: verify_gemini_removal.py")

if __name__ == "__main__":
    main()