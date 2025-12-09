import socket
import argparse
from chat_utils import *
from chat_client_class import Client
from GUI import GUI
from client_state_machine import ClientSM

# This is the standard setup to read command line arguments (IP and Port)
parser = argparse.ArgumentParser(description='chat client argument')
parser.add_argument('-d', type=str, default='127.0.0.1', help='server IP addr')
args = parser.parse_args()


# 1. Setup the socket connection
client = Client(args) 

client.init_chat()

# 2. Define helper functions so the GUI can send/recv without knowing about sockets
# The GUI expects send(msg) and recv(), but the system uses mysend(socket, msg)
def send_wrapper(msg):
    mysend(client.socket, msg)

def recv_wrapper():
    return myrecv(client.socket)

# 3. Start the GUI
# We pass the wrappers, the state machine (sm), and the socket (s)
print("Starting GUI...")
main_gui = GUI(send_wrapper, recv_wrapper, client.sm, client.socket)
main_gui.run()