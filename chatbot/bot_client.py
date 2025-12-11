'''
TrishaBot = AI user inside the chat system

This connects to the server, logs in, joins room,
listens to messages, and responds when users type @trishabot ...
'''

import socket
import threading
import json
from chat_bot_client import ChatBotClient   # LLM wrapper
from nlp_tools import extract_keywords_yake, summarize_with_sumy #BONUS 2: NLP


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

        # <<< ADDED: for NLP
        self.chat_history = []
        self.max_history = 100

        # remember last answered question per user to avoid duplicate replies
        self.last_answered = {}   # maps from_name -> question string

        # ---- LOGIN to the server ----
        login_msg = json.dumps({"action": "login", "name": self.name})
        mysend(self.sock, login_msg)

        # ---- AUTO-JOIN GROUP ROOM FOR BONUS FEATURE ----
        group_room = "projectroom"   # 🔹 choose any room name you like
        connect_msg = json.dumps({
            "action": "connect",
            "target": group_room
        })
        mysend(self.sock, connect_msg)
        print(f"{self.name} joined group room:", group_room)

        self.bot = ChatBotClient()

        # start listening for messages
        threading.Thread(target=self.listen_loop, daemon=True).start()

# ------------ helper to send reply ------------
    # <<< ADDED: small helper so we don't repeat JSON code
    def send_reply(self, text: str):
        print("DEBUG sending reply:", repr(text))  # <--- ADD THIS
        reply_text = f": {text}"  # keep leading colon so GUI shows "TrishaBot: ..."
        out = json.dumps({
            "action": "exchange",
            "from": self.name,
            "message": reply_text
        })
        mysend(self.sock, out)

    # ------------ CHAT MESSAGE HANDLER ------------
    def handle_exchange(self, from_name, text):
        print("DEBUG received from server:", repr(from_name), repr(text))  # <--- ADD THIS

        # <<< ADDED: store every message in history (for NLP)
        self.chat_history.append(text)
        if len(self.chat_history) > self.max_history:
            self.chat_history = self.chat_history[-self.max_history:]

        # ignore own messages
        if from_name == self.name:
            return
        
        lower = text.lower().strip()

        # <<< ADDED: NLP KEYWORDS COMMAND
        if lower == "/keywords" or lower.startswith("@trishabot /keywords"):
            self.reply_keywords()
            return

        # <<< ADDED: NLP SUMMARY COMMAND
        if lower == "/summary" or lower.startswith("@trishabot /summary"):
            self.reply_summary()
            return

        # only respond to @trishabot
        if not text.lower().startswith("@trishabot"):
            return

        question = text[len("@trishabot"):].strip()
        if not question:
            return

        # --- NEW: dedupe per-user per-question ---
        last_q = self.last_answered.get(from_name)
        if last_q == question:
            print("DEBUG: duplicate question from same user, ignoring:", from_name, repr(question))
            return
        self.last_answered[from_name] = question
    # -----------------------------------------
        print(f"User asked TrishaBot: {question}")

        # ---- Call LLM here ----
        reply_text = self.bot.chat(question)  
        self.send_reply(reply_text)

        # ------------ NLP keyword reply ------------
    # <<< ADDED
    def reply_keywords(self):
        # use the last 40 messages for analysis
        messages = self.chat_history[-40:]
        keywords = extract_keywords_yake(messages, top_k=5)

        if not keywords:
            text = "No keywords found."
        else:
            text = "Keywords: " + ", ".join(keywords)

        self.send_reply(text)

    # ------------ NLP summary reply ------------
    # <<< ADDED
    def reply_summary(self):
        messages = self.chat_history[-40:]
        summary_sentences = summarize_with_sumy(messages, sentences_count=3)

        if not summary_sentences:
            text = "Not enough chat history to summarize."
        else:
            text = "Summary: " + " ".join(summary_sentences)

        self.send_reply(text)

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