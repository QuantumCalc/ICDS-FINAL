'''
TrishaBot = AI user inside the chat system

This connects to the server, logs in, joins room,
listens to messages, and responds when users type @trishabot ...
'''

import socket
import threading
import json
from chat_bot_client import ChatBotClient   # LLM wrapper

HOST = "127.0.0.1"      # same machine running the server
PORT = 1112             # MUST match CHAT_PORT in chat_utils.py

# ---------- protocol helpers copied from chat_utils.py ----------

SIZE_SPEC = 5

def mysend(s, msg):
    msg = ('0' * SIZE_SPEC + str(len(msg)))[-SIZE_SPEC:] + str(msg)
    msg = msg.encode()
    total_sent = 0
    while total_sent < len(msg):
        sent = s.send(msg[total_sent:])
        if sent == 0:
            print('server disconnected')
            break
        total_sent += sent

def myrecv(s):
    size = ''
    while len(size) < SIZE_SPEC:
        text = s.recv(SIZE_SPEC - len(size)).decode()
        if not text:
            print('disconnected')
            return ''
        size += text
    size = int(size)

    msg = ''
    while len(msg) < size:
        text = s.recv(size - len(msg)).decode()
        if not text:
            print('disconnected')
            break
        msg += text
    return msg

# ----------------------------------------------------------------


class BotClient:
    def __init__(self, name="TrishaBot"):
        self.name = name
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        print(f"{self.name} connected to {HOST}:{PORT}")

        # ---- LOGIN to the server ----
        login_msg = json.dumps({"action": "login", "name": self.name})
        mysend(self.sock, login_msg)

        # ---- AUTO-JOIN ROOM #TrishaBot ----
        # This tells the server "put TrishaBot into room #TrishaBot"
        connect_msg = json.dumps({
            "action": "connect",
            "target": self.name      # server will turn "TrishaBot" into "#TrishaBot"
        })
        mysend(self.sock, connect_msg)

        self.bot = ChatBotClient()

        # start listening for messages
        threading.Thread(target=self.listen_loop, daemon=True).start()


    # ------------ CHAT MESSAGE HANDLER ------------
    def handle_exchange(self, from_name, text):
        # ignore own messages
        if from_name == self.name:
            return

        # only respond to @trishabot
        if not text.lower().startswith("@trishabot"):
            return

        question = text[len("@trishabot"):].strip()
        if not question:
            return

        print(f"User asked TrishaBot: {question}")

        # ---- Call your LLM here ----
        reply_text = self.bot.chat(question)  
        reply_text = f": {reply_text}"
        
        # send reply back to server
        out = json.dumps({
            "action": "exchange",
            "from": self.name,
            "message": reply_text
        })
        mysend(self.sock, out)


    # ------------ MAIN LISTEN LOOP ------------
    def listen_loop(self):
        while True:
            data = myrecv(self.sock)
            if not data:
                continue

            try:
                msg = json.loads(data)
            except Exception as e:
                print("Bad JSON:", data, e)
                continue

            action = msg.get("action")

            if action == "exchange":
                sender = msg.get("from")
                text = msg.get("message", "")
                self.handle_exchange(sender, text)
            # ignore login/list/poem/time/etc.

# ------------ ENTRY POINT ------------
if __name__ == "__main__":
    BotClient(name="TrishaBot")
    # keep the program alive
    while True:
        pass