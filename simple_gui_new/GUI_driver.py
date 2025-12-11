import socket
import argparse
from chat_utils import *
from chat_client_class import Client
from GUI import GUI
from client_state_machine import ClientSM

parser = argparse.ArgumentParser(description='chat client argument')
parser.add_argument('-d', type=str, default='127.0.0.1', help='server IP addr')
args = parser.parse_args()


client = Client(args) 

client.init_chat()

def send_wrapper(msg):
    mysend(client.socket, msg)

def recv_wrapper():
    return myrecv(client.socket)

print("Starting GUI...")
main_gui = GUI(send_wrapper, recv_wrapper, client.sm, client.socket)
main_gui.run()