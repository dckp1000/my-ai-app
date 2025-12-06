import os
from openai import OpenAI

# Initialize OpenAI client once at module level for better performance
# API key can be set via environment variable OPENAI_API_KEY or hardcoded
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "YOUR_API_KEY"))

def ask_gpt(prompt):
    """
    Send a prompt to GPT and get a response.
    Uses a shared client instance for better performance.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    print("Welcome to your AI app! Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        reply = ask_gpt(user_input)
        print("AI: " + reply)
