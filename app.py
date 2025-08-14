import openai

def ask_gpt(prompt):
    # Replace YOUR_API_KEY with your OpenAI API key
    openai.api_key = "YOUR_API_KEY"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

if __name__ == "__main__":
    print("Welcome to your AI app! Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        reply = ask_gpt(user_input)
        print("AI: " + reply)
