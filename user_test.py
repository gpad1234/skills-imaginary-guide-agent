#!/usr/bin/env python3
"""
Interactive User Testing Script
Tests the MCP OSQuery Server with real examples
"""

import os
import sys
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv()

def main():
    """Run interactive user testing"""
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY not set in .env file")
        sys.exit(1)
    
    # Initialize Anthropic client
    client = Anthropic()
    
    print("=" * 60)
    print("🧪 MCP OSQuery Server - User Testing")
    print("=" * 60)
    print()
    print("Testing Claude with system queries via MCP tools")
    print()
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "System Information",
            "prompt": "What is this system's hostname and OS information?"
        },
        {
            "name": "Process Analysis", 
            "prompt": "Show me the top 5 processes by memory usage on this system."
        },
        {
            "name": "Network Status",
            "prompt": "What are the active network connections on this machine?"
        },
        {
            "name": "User Information",
            "prompt": "List the system users and their UIDs."
        },
        {
            "name": "Disk Usage",
            "prompt": "Check the disk usage and mount points."
        }
    ]
    
    # Run tests
    passed = 0
    failed = 0
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {scenario['name']}")
        print(f"{'='*60}")
        print(f"Prompt: {scenario['prompt']}")
        print()
        
        try:
            # Create message with Claude
            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": scenario['prompt']
                    }
                ]
            )
            
            # Display response
            response_text = message.content[0].text
            print("✅ Response received:")
            print("-" * 60)
            print(response_text[:500])  # Show first 500 chars
            if len(response_text) > 500:
                print("... (truncated)")
            print("-" * 60)
            
            passed += 1
            print(f"✅ PASSED")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print(f"❌ FAILED")
            failed += 1
    
    # Summary
    print()
    print("=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
    print()
    
    if failed == 0:
        print("🎉 All tests passed! System is working correctly.")
    else:
        print(f"⚠️  {failed} test(s) failed. Check configuration.")
    
    # Interactive mode
    print()
    print("=" * 60)
    print("💬 Interactive Mode")
    print("=" * 60)
    print("Type your queries below (Ctrl+C to exit):")
    print()
    
    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            
            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": user_input
                    }
                ]
            )
            
            response = message.content[0].text
            print(f"\nClaude: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()
