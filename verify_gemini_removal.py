#!/usr/bin/env python3
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
            r'\bgemini\b',
            r'\bGemini\b', 
            r'\bGEMINI\b',
            r'GOOGLE_API_KEY',
            r'google_api_key',
            r'Google.*API',
            r'gemini-voice-assistant',
            r'MockGemini',
            r'test_gemini'
        ]
        
        issues = []
        for i, line in enumerate(content.split('\n'), 1):
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
                    print(f"\n⚠️  {file_path}:")
                    for issue in issues[:5]:  # Show first 5 issues
                        print(f"   {issue}")
                    if len(issues) > 5:
                        print(f"   ... and {len(issues) - 5} more")
                    total_issues += len(issues)
    
    if total_issues == 0:
        print("\n✅ No Gemini/Google references found!")
    else:
        print(f"\n❌ Found {total_issues} remaining references")

if __name__ == "__main__":
    main()
