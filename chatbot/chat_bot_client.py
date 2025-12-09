import ollama

'''
Our chatbot uses ollama's local model phi3:mini.
Chatbotclient  = LLM brain
'''

class ChatBotClient():

    def __init__(self, name="3po", model="phi3:mini", personality = "helpful and concise"):
        self.name = name
        self.model = model
        self.messages = []
        self.personality = personality
        self._update_system_message()

    def _update_system_message(self):
        system_content = (
            f"You are a chatbot with the following personality: {self.personality}. "
            "Reply in one clear, complete sentence unless the user requests more detail. "
            "Never answer with just a single word or a fragment. "
            "For example, if the user asks 'What is the capital of France?', "
            "you MUST reply 'The capital of France is Paris.' and not just 'Paris'."
        )

        # Insert or update system message
        if self.messages and self.messages[0]["role"] == "system":
            self.messages[0]["content"] = system_content
        else:
            self.messages.insert(0, {"role": "system", "content": system_content})

    def set_personality(self, new_personality: str):
        self.personality = new_personality
        self._update_system_message()

    
    def chat(self, message: str) -> str:
        # Adding user message to history
        self.messages.append({"role": "user", "content": message})
        
        # Call local LLM through Ollama
        response = ollama.chat(
            model=self.model,
            messages=self.messages
        )

        reply = response["message"]["content"]

        # Save assistant reply to history
        self.messages.append({"role": "assistant", "content": reply})
        return reply
    
    def stream_chat(self, message: str) -> str:
        # Returns a stream reply (prints as it comes out) 
        # and returns full answer as string
        self.messages.append({
            'role': 'user',
            'content': message,
        })

        response = ollama.chat(model=self.model, messages=self.messages, stream=True)
        answer = ""
        for chunk in response:
            piece = chunk["message"]["content"]
            print(piece, end="")
            answer += piece
        # Add chatbot reply to history (stores past memory)
        self.messages.append({"role": "assistant", "content": answer})
        return answer
        

if __name__ == "__main__":
    bot = ChatBotClient()
    print(bot.chat("Your name is Tom, and you are the learning assistant of Python programming."))
    print()
    bot.stream_chat("What's your name and role?")