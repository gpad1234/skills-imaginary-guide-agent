import os
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv()

def main():
    # Initialize Anthropic client
    client = Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    try:
        # Example usage: Create a simple message
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": "Hello, Claude! Can you tell me a brief joke?"
                }
            ]
        )
        
        print("Claude's response:")
        print(message.content[0].text)
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have set your ANTHROPIC_API_KEY in the .env file")

if __name__ == "__main__":
    main()