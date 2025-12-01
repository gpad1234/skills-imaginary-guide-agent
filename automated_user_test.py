#!/usr/bin/env python3
"""
Automated User Testing Script
Tests the MCP OSQuery Server functionality
"""

import os
import sys
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv()

def main():
    """Run automated user testing"""
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY not set in .env file")
        return False
    
    # Initialize Anthropic client
    client = Anthropic()
    
    print("=" * 60)
    print("🧪 MCP OSQuery Server - Automated User Testing")
    print("=" * 60)
    print()
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "System Information",
            "prompt": "What is this system's hostname and OS information? Keep it brief."
        },
        {
            "name": "Process Analysis", 
            "prompt": "Show me 3 processes currently running on this system."
        },
        {
            "name": "Network Status",
            "prompt": "Are there any active network connections? List 2-3."
        },
        {
            "name": "User Information",
            "prompt": "What are 2-3 system users on this machine?"
        },
        {
            "name": "General Query",
            "prompt": "Give me a brief summary of this system's current state."
        }
    ]
    
    # Run tests
    passed = 0
    failed = 0
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n[Test {i}/{len(test_scenarios)}] {scenario['name']}")
        print(f"Prompt: {scenario['prompt']}")
        
        try:
            # Create message with Claude
            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=512,
                messages=[
                    {
                        "role": "user",
                        "content": scenario['prompt']
                    }
                ]
            )
            
            # Display response
            response_text = message.content[0].text
            print(f"✅ Response: {response_text[:200]}...")
            
            passed += 1
            results.append((scenario['name'], "PASSED"))
            
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")
            failed += 1
            results.append((scenario['name'], "FAILED"))
    
    # Summary
    print()
    print("=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    for name, status in results:
        symbol = "✅" if status == "PASSED" else "❌"
        print(f"{symbol} {name}: {status}")
    
    print()
    print(f"✅ Passed: {passed}/{len(test_scenarios)}")
    print(f"❌ Failed: {failed}/{len(test_scenarios)}")
    print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
    print()
    
    if failed == 0:
        print("🎉 All tests passed! System is working correctly.")
        return True
    else:
        print(f"⚠️  {failed} test(s) failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
