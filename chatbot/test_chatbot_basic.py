# Testing chat_bot_client

from chat_bot_client import ChatBotClient

def main():
    bot = ChatBotClient()  # uses phi3:mini and system prompt

    print("Simple chatbot demo. Type 'quit' to exit.")
    print("Use `/persona ...` to change the bot's personality.\n")

    while True:
        user = input("You: ")
        text = user.strip()

        if text.lower() in {"quit", "exit", "/quit"}:
            print("Bot: Bye! 👋")
            break

        if text.startswith("/persona "):
            new_p = text[len("/persona "):].strip()
            bot.set_personality(new_p)
            print(f"Bot: Okay, I will now behave like: {new_p}")
            continue

        reply = bot.chat(user)
        print("Bot:", reply)

if __name__ == "__main__":
    main()

