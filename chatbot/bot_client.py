'''
botclient = AI user inside the chat system
'''
import socket, threading
from chatbot.chat_bot_client import ChatBotClient

class BotClient:
    def __init__(self, name="Bot", host="127.0.0.1", port=50007):
        self.name = name
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        print(f"{self.name} connected.")

        self.bot = ChatBotClient()
        threading.Thread(target=self.listen_loop, daemon=True).start()

    def listen_loop(self):
        while True:
            data = self.sock.recv(4096).decode()
            if not data:
                continue
            sender, msg = data.split("|", 1)

            if sender == self.name:
                continue  # don't answer our own messages

            print(f"{sender}: {msg}")

            # later you can restrict this to @Bot or /askbot
            reply = self.bot.chat(msg)
            out = f"{self.name}|{reply}"
            self.sock.sendall(out.encode())

if __name__ == "__main__":
    BotClient()
    while True:
        pass

