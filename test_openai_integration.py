#!/usr/bin/env python3
"""
NPCL Voice Assistant - OpenAI Integration Test
==============================================
Comprehensive test script to validate OpenAI integration functionality
Tests API connectivity, model access, and real-time capabilities
"""

import os
import sys
import asyncio
import json
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Test results tracking
@dataclass
class TestResult:
    name: str
    passed: bool
    message: str
    duration: float = 0.0

class OpenAIIntegrationTester:
    """Comprehensive OpenAI integration tester"""
    
    def __init__(self):
        self.results = []
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for test output"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('openai_integration_test.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def add_result(self, name: str, passed: bool, message: str, duration: float = 0.0):
        """Add test result"""
        result = TestResult(name, passed, message, duration)
        self.results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        self.logger.info(f"{status}: {name} - {message}")
        
        if duration > 0:
            self.logger.info(f"   Duration: {duration:.2f}s")
    
    def test_openai_import(self) -> bool:
        """Test OpenAI package import"""
        start_time = time.time()
        try:
            import openai
            version = openai.__version__
            duration = time.time() - start_time
            self.add_result(
                "OpenAI Import", 
                True, 
                f"Successfully imported OpenAI v{version}",
                duration
            )
            return True
        except ImportError as e:
            duration = time.time() - start_time
            self.add_result(
                "OpenAI Import", 
                False, 
                f"Failed to import OpenAI: {e}",
                duration
            )
            return False
    
    def test_api_key_configuration(self) -> bool:
        """Test OpenAI API key configuration"""
        start_time = time.time()
        
        # Check environment variable
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            duration = time.time() - start_time
            self.add_result(
                "API Key Configuration",
                False,
                "OPENAI_API_KEY environment variable not set",
                duration
            )
            return False
        
        # Check key format (should start with sk-)
        if not api_key.startswith('sk-'):
            duration = time.time() - start_time
            self.add_result(
                "API Key Configuration",
                False,
                "API key format invalid (should start with 'sk-')",
                duration
            )
            return False
        
        duration = time.time() - start_time
        self.add_result(
            "API Key Configuration",
            True,
            f"API key properly configured (length: {len(api_key)})",
            duration
        )
        return True
    
    def test_openai_client_creation(self) -> bool:
        """Test OpenAI client creation"""
        start_time = time.time()
        try:
            import openai
            
            client = openai.OpenAI(
                api_key=os.getenv('OPENAI_API_KEY')
            )
            
            duration = time.time() - start_time
            self.add_result(
                "OpenAI Client Creation",
                True,
                "OpenAI client created successfully",
                duration
            )
            return True
        except Exception as e:
            duration = time.time() - start_time
            self.add_result(
                "OpenAI Client Creation",
                False,
                f"Failed to create OpenAI client: {e}",
                duration
            )
            return False
    
    def test_basic_api_connectivity(self) -> bool:
        """Test basic API connectivity"""
        start_time = time.time()
        try:
            import openai
            
            client = openai.OpenAI(
                api_key=os.getenv('OPENAI_API_KEY')
            )
            
            # Test with a simple completion
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Use cheaper model for testing
                messages=[
                    {"role": "user", "content": "Say 'API test successful'"}
                ],
                max_tokens=10
            )
            
            if response.choices and response.choices[0].message.content:
                duration = time.time() - start_time
                self.add_result(
                    "Basic API Connectivity",
                    True,
                    f"API responded: {response.choices[0].message.content.strip()}",
                    duration
                )
                return True
            else:
                duration = time.time() - start_time
                self.add_result(
                    "Basic API Connectivity",
                    False,
                    "API response was empty",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.add_result(
                "Basic API Connectivity",
                False,
                f"API connectivity failed: {e}",
                duration
            )
            return False
    
    def test_realtime_model_access(self) -> bool:
        """Test access to GPT-4 Realtime model"""
        start_time = time.time()
        try:
            import openai
            
            client = openai.OpenAI(
                api_key=os.getenv('OPENAI_API_KEY')
            )
            
            # Test with the actual realtime model
            response = client.chat.completions.create(
                model="gpt-4o-realtime-preview-2024-10-01",
                messages=[
                    {"role": "user", "content": "Test realtime model access"}
                ],
                max_tokens=20
            )
            
            if response.choices and response.choices[0].message.content:
                duration = time.time() - start_time
                self.add_result(
                    "Realtime Model Access",
                    True,
                    f"Realtime model accessible: {response.choices[0].message.content.strip()}",
                    duration
                )
                return True
            else:
                duration = time.time() - start_time
                self.add_result(
                    "Realtime Model Access",
                    False,
                    "Realtime model response was empty",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            
            # Check for specific error types
            if "model_not_found" in error_msg or "does not exist" in error_msg:
                self.add_result(
                    "Realtime Model Access",
                    False,
                    "GPT-4 Realtime model not available (may need beta access)",
                    duration
                )
            elif "insufficient_quota" in error_msg or "quota" in error_msg:
                self.add_result(
                    "Realtime Model Access",
                    False,
                    "Insufficient quota for realtime model",
                    duration
                )
            else:
                self.add_result(
                    "Realtime Model Access",
                    False,
                    f"Realtime model access failed: {error_msg}",
                    duration
                )
            return False
    
    def test_voice_capabilities(self) -> bool:
        """Test voice-related capabilities"""
        start_time = time.time()
        try:
            import openai
            
            client = openai.OpenAI(
                api_key=os.getenv('OPENAI_API_KEY')
            )
            
            # Test TTS capability
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input="Testing OpenAI voice capabilities"
            )
            
            if response.content:
                duration = time.time() - start_time
                self.add_result(
                    "Voice Capabilities",
                    True,
                    f"TTS working, generated {len(response.content)} bytes of audio",
                    duration
                )
                return True
            else:
                duration = time.time() - start_time
                self.add_result(
                    "Voice Capabilities",
                    False,
                    "TTS response was empty",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.add_result(
                "Voice Capabilities",
                False,
                f"Voice capabilities test failed: {e}",
                duration
            )
            return False
    
    def test_settings_integration(self) -> bool:
        """Test integration with project settings"""
        start_time = time.time()
        try:
            from config.settings import get_settings
            
            settings = get_settings()
            
            # Check if OpenAI settings are present
            if hasattr(settings, 'openai_api_key'):
                if hasattr(settings, 'openai_model'):
                    duration = time.time() - start_time
                    self.add_result(
                        "Settings Integration",
                        True,
                        f"Settings loaded with OpenAI model: {settings.openai_model}",
                        duration
                    )
                    return True
                else:
                    duration = time.time() - start_time
                    self.add_result(
                        "Settings Integration",
                        False,
                        "OpenAI model not configured in settings",
                        duration
                    )
                    return False
            else:
                duration = time.time() - start_time
                self.add_result(
                    "Settings Integration",
                    False,
                    "OpenAI API key not configured in settings",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.add_result(
                "Settings Integration",
                False,
                f"Settings integration failed: {e}",
                duration
            )
            return False
    
    def test_ai_client_factory(self) -> bool:
        """Test AI client factory integration"""
        start_time = time.time()
        try:
            from src.voice_assistant.ai.ai_client_factory import AIClientFactory
            
            # Create OpenAI client through factory
            client = AIClientFactory.create_client('openai')
            
            if client:
                duration = time.time() - start_time
                self.add_result(
                    "AI Client Factory",
                    True,
                    f"AI client factory created OpenAI client: {type(client).__name__}",
                    duration
                )
                return True
            else:
                duration = time.time() - start_time
                self.add_result(
                    "AI Client Factory",
                    False,
                    "AI client factory returned None",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.add_result(
                "AI Client Factory",
                False,
                f"AI client factory test failed: {e}",
                duration
            )
            return False
    
    async def test_realtime_client(self) -> bool:
        """Test OpenAI Realtime client"""
        start_time = time.time()
        try:
            from src.voice_assistant.ai.openai_realtime_client_enhanced import OpenAIRealtimeClientEnhanced
            
            # Create realtime client
            client = OpenAIRealtimeClientEnhanced()
            
            # Test connection (without actually connecting)
            if hasattr(client, 'connect'):
                duration = time.time() - start_time
                self.add_result(
                    "Realtime Client",
                    True,
                    f"Realtime client created: {type(client).__name__}",
                    duration
                )
                return True
            else:
                duration = time.time() - start_time
                self.add_result(
                    "Realtime Client",
                    False,
                    "Realtime client missing connect method",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.add_result(
                "Realtime Client",
                False,
                f"Realtime client test failed: {e}",
                duration
            )
            return False
    
    def test_function_calling(self) -> bool:
        """Test function calling capabilities"""
        start_time = time.time()
        try:
            import openai
            
            client = openai.OpenAI(
                api_key=os.getenv('OPENAI_API_KEY')
            )
            
            # Test function calling
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "description": "Get weather information",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "The city name"
                                }
                            },
                            "required": ["location"]
                        }
                    }
                }
            ]
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": "What's the weather in New York?"}
                ],
                tools=tools,
                max_tokens=50
            )
            
            if response.choices:
                duration = time.time() - start_time
                self.add_result(
                    "Function Calling",
                    True,
                    "Function calling capability verified",
                    duration
                )
                return True
            else:
                duration = time.time() - start_time
                self.add_result(
                    "Function Calling",
                    False,
                    "Function calling response was empty",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.add_result(
                "Function Calling",
                False,
                f"Function calling test failed: {e}",
                duration
            )
            return False
    
    async def run_all_tests(self):
        """Run all integration tests"""
        self.logger.info("🚀 Starting OpenAI Integration Tests")
        self.logger.info("=" * 50)
        
        # Basic tests
        self.test_openai_import()
        self.test_api_key_configuration()
        self.test_openai_client_creation()
        
        # API tests (only if basic tests pass)
        if os.getenv('OPENAI_API_KEY'):
            self.test_basic_api_connectivity()
            self.test_realtime_model_access()
            self.test_voice_capabilities()
            self.test_function_calling()
        else:
            self.logger.warning("⚠️  Skipping API tests - OPENAI_API_KEY not set")
        
        # Integration tests
        self.test_settings_integration()
        self.test_ai_client_factory()
        await self.test_realtime_client()
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        self.logger.info("\n" + "=" * 50)
        self.logger.info("📊 OpenAI Integration Test Report")
        self.logger.info("=" * 50)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        self.logger.info(f"Total Tests: {total_tests}")
        self.logger.info(f"✅ Passed: {passed_tests}")
        self.logger.info(f"❌ Failed: {failed_tests}")
        
        if failed_tests == 0:
            self.logger.info("\n🎉 ALL TESTS PASSED!")
            self.logger.info("✅ OpenAI integration is working correctly")
        else:
            self.logger.info(f"\n⚠️  {failed_tests} test(s) failed")
            self.logger.info("❌ Some issues need to be resolved")
            
            self.logger.info("\nFailed Tests:")
            for result in self.results:
                if not result.passed:
                    self.logger.info(f"  - {result.name}: {result.message}")
        
        # Calculate total duration
        total_duration = sum(r.duration for r in self.results)
        self.logger.info(f"\nTotal test duration: {total_duration:.2f}s")
        
        # Save detailed report
        self.save_detailed_report()
    
    def save_detailed_report(self):
        """Save detailed test report to file"""
        report_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_tests": len(self.results),
                "passed": sum(1 for r in self.results if r.passed),
                "failed": sum(1 for r in self.results if not r.passed),
                "total_duration": sum(r.duration for r in self.results)
            },
            "results": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "message": r.message,
                    "duration": r.duration
                }
                for r in self.results
            ]
        }
        
        with open('openai_integration_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        self.logger.info("📄 Detailed report saved to: openai_integration_report.json")

async def main():
    """Main test execution"""
    tester = OpenAIIntegrationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())