#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 13:36:58 2021

@author: bing
"""

# import all the required  modules
import threading
import select
from tkinter import *
from tkinter import font
from tkinter import ttk
from tkinter import simpledialog
from chat_utils import *
import json

# GUI class for the chat
class GUI:
    # constructor method
    def __init__(self, send, recv, sm, s):
        # chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()
        self.send = send
        self.recv = recv
        self.sm = sm
        self.socket = s
        self.colors = ["#AD1D1D", '#33C1FF', '#FF33A8', '#E67E22', "#1EB73A", '#9B59B6', "#235168FF"]
        self.color_map = {}
        self.color_index = 0
        self.my_msg = ""
        self.system_msg = ""

    def login(self):
        # login window
        self.login = Toplevel()
        # set the title
        self.login.title("Login")
        self.login.resizable(width = False, 
                             height = False)
        self.login.configure(width = 400,
                             height = 300)
        # create a Label
        self.pls = Label(self.login, 
                       text = "Please login to continue",
                       justify = CENTER, 
                       font = "Helvetica 14 bold")
          
        self.pls.place(relheight = 0.15,
                       relx = 0.2, 
                       rely = 0.07)
        # create a Label
        self.labelName = Label(self.login,
                               text = "Name: ",
                               font = "Helvetica 12")
          
        self.labelName.place(relheight = 0.2,
                             relx = 0.1, 
                             rely = 0.2)
          
        # create a entry box for 
        # tyoing the message
        self.entryName = Entry(self.login, 
                             font = "Helvetica 14")
          
        self.entryName.place(relwidth = 0.4, 
                             relheight = 0.12,
                             relx = 0.35,
                             rely = 0.2)
          
        # set the focus of the curser
        self.entryName.focus()
          
        # create a Continue Button 
        # along with action
        self.go = Button(self.login,
                         text = "CONTINUE", 
                         font = "Helvetica 14 bold", 
                         command = lambda: self.goAhead(self.entryName.get()))
          
        self.go.place(relx = 0.4,
                      rely = 0.55)
        self.Window.mainloop()
  
    def goAhead(self, name):
        if len(name) > 0:
            msg = json.dumps({"action":"login", "name": name})
            self.send(msg)
            response = json.loads(self.recv())
            if response["status"] == 'ok':
                self.login.destroy()
                self.sm.set_state(S_LOGGEDIN)
                self.sm.set_myname(name)
                self.layout(name)
                self.textCons.config(state = NORMAL)
                self.textCons.insert(END, "Welcome to the Chat Room!\n", 'sys')
                self.textCons.insert(END, "Use the sidebar on the right to interface with the chat functions.\n\n", 'sys')
                self.textCons.insert(END, menu +"\n\n")      
                self.textCons.config(state = DISABLED)
                self.textCons.see(END)
                # while True:
                #     self.proc()
        # the thread to receive messages
            process = threading.Thread(target=self.proc)
            process.daemon = True
            process.start()
  
    # The main layout of the chat
    def layout(self, name):

        self.name = name
        # to show chat window
        self.Window.deiconify()
        self.Window.title("CHATROOM")
        self.Window.resizable(width = False,
                              height = False)
        self.Window.configure(width = 650,
                              height = 550,
                              bg = "#17202A")
        
        self.labelHead = Label(self.Window,
                             bg = "#17202A", 
                             fg = "#EAECEE",
                             text = self.name,
                             font = "Helvetica 13 bold",
                             pady = 5)
        self.labelHead.place(relwidth = 1, 
                             relheight = 0.05)
        
        self.labelMembers = Label(self.Window,
                                  bg = "#17202A",
                                  fg = "#2ECC71",
                                  text = "Members: (Not Connected)",
                                  font = "Helvetica 10 italic")
        self.labelMembers.place(relwidth = 1, 
                                rely = 0.05, 
                                relheight = 0.04)

        self.line = Label(self.Window, 
                          width = 450, 
                          bg = "#ABB2B9")
        self.line.place(relwidth = 1, 
                        rely = 0.09, 
                        relheight = 0.012)
        
        
        self.sidebar = Frame(self.Window, bg="#2C3E50")
        self.sidebar.place(relx=0.75, 
                           rely=0.10, 
                           relwidth=0.25, 
                           relheight=0.85)
        
        # Button: List Users
        self.btn_who = Button(self.sidebar,
                              text="List Users", 
                              font="Helvetica 10 bold", 
                              bg="#ABB2B9", 
                              command=lambda: self.sendButton("who"))
        self.btn_who.place(relx=0.1, 
                           rely=0.05, 
                           relwidth=0.8, 
                           height=30)
        
        # Button: Check Time
        self.btn_time = Button(self.sidebar,
                               text="Check Time",
                               font="Helvetica 10 bold", 
                               bg="#ABB2B9",
                               command=lambda: self.sendButton("time"))
        self.btn_time.place(relx=0.1, 
                            rely=0.15, 
                            relwidth=0.8, 
                            height=30)

        # Button: Create Room
        self.btn_create = Button(self.sidebar, 
                                 text="Create Room", 
                                 font="Helvetica 10 bold", 
                                 bg="#2ECC71", 
                                 fg="white",
                                 command=self.open_create_room_popup)
        self.btn_create.place(relx=0.1, 
                              rely=0.35, 
                              relwidth=0.8, 
                              height=30)
        
        # Button: Join Room
        self.btn_join = Button(self.sidebar, 
                               text="Join Room", 
                               font="Helvetica 10 bold", 
                               bg="#3498DB", 
                               fg="white",
                               command=self.open_join_room_popup)
        self.btn_join.place(relx=0.1,
                            rely=0.45, 
                            relwidth=0.8, 
                            height=30)

        # Button: Disconnect
        self.btn_bye = Button(self.sidebar, 
                              text="Disconnect", 
                              font="Helvetica 10 bold", 
                              bg="#E74C3C", 
                              fg="white",
                              command=lambda: self.sendButton("bye"))
        self.btn_bye.place(relx=0.1, 
                           rely=0.55, 
                           relwidth=0.8, 
                           height=30)
        
        # Button: Get Poem
        self.btn_poem = Button(self.sidebar, text="Read Poem", font="Helvetica 10 bold", 
                               bg="#ABB2B9", command=self.open_poem_popup)
        self.btn_poem.place(relx=0.1, rely=0.65, relwidth=0.8, height=30)

        # Button: Search
        self.btn_search = Button(self.sidebar, 
                                 text="Search History", 
                                 font="Helvetica 10 bold", 
                                 bg="#ABB2B9", 
                                 command=self.open_search_popup)
        self.btn_search.place(relx=0.1,
                              rely=0.75, 
                              relwidth=0.8, 
                              height=30)

        # Button: Clear Chat
        self.btn_clr = Button(self.sidebar,
                              text="Clear Chat",
                              font="Helvetica 10 bold", 
                              bg="#ABB2B9", 
                              command=self.clear_chat)
        self.btn_clr.place(relx=0.1, 
                           rely=0.85, 
                           relwidth=0.8, 
                           height=30)
          
        self.textCons = Text(self.Window,
                             width = 20, 
                             height = 2,
                             bg = "#17202A",
                             fg = "#EAECEE",
                             font = "Helvetica 14", 
                             padx = 5,
                             pady = 5,
                             wrap = WORD)
          
        self.textCons.place(relheight = 0.745,
                            relwidth = 0.75, 
                            rely = 0.08)
        
        #own messages
        self.textCons.tag_config('me', 
                                 justify='right',
                                 foreground="#FFFFFF", 
                                 rmargin=50)
        #peer messages
        self.textCons.tag_config('peer', 
                                 justify='left', 
                                 foreground="#49C219", 
                                 lmargin1=10,
                                 lmargin2=10)
        #server messages
        self.textCons.tag_config('sys', 
                                 justify='center', 
                                 foreground="#E9BE14", 
                                 font="Helvetica 10 italic")
          
        self.labelBottom = Label(self.Window,
                                 bg = "#ABB2B9",
                                 height = 80)
          
        self.labelBottom.place(relwidth = 0.75,
                               rely = 0.825)
          
        self.entryMsg = Entry(self.labelBottom,
                              bg = "#2C3E50",
                              fg = "#EAECEE",
                              font = "Helvetica 13")
        
        self.entryMsg.bind("<Return>", 
                           lambda event: self.sendButton(self.entryMsg.get()))  

        # place the given widget
        # into the gui window
        self.entryMsg.place(relwidth = 0.74,
                            relheight = 0.06,
                            rely = 0.008,
                            relx = 0.011)
          
        self.entryMsg.focus()
          
        # create a Send Button
        self.buttonMsg = Button(self.labelBottom,
                                text = "Send",
                                font = "Helvetica 10 bold", 
                                width = 20,
                                bg = "#ABB2B9",
                                command = lambda : self.sendButton(self.entryMsg.get()))
          
        self.buttonMsg.place(relx = 0.77,
                             rely = 0.008,
                             relheight = 0.06, 
                             relwidth = 0.22)
          
        self.textCons.config(cursor = "arrow")
          
        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)
          
        # place the scroll bar 
        # into the gui window
        scrollbar.place(relheight = 1,
                        relx = 0.974)
        
        scrollbar.config(command = self.textCons.yview)
          
        self.textCons.config(state = DISABLED)
  
    # function to basically start the thread for sending messages
    def sendButton(self, msg):
        #if msg.startswith("!bot"):
            #return

        if msg == "who" or msg == "time" or msg.startswith("p ") or msg.startswith("?"):
            self.textCons.config(state=NORMAL)
            self.textCons.insert(END, f"[System] Sending command: '{msg}'...\n", 'sys')                
            self.textCons.config(state=DISABLED)

        self.textCons.config(state = DISABLED)
        self.my_msg = msg
        self.entryMsg.delete(0, END)

    def open_create_room_popup(self):
        room_name = simpledialog.askstring("Create Room", "Enter Name for New Room:")
        if room_name:
            if not room_name.startswith("#"):
                room_name = "#" + room_name
            self.sendButton(f"c {room_name}")

    def open_join_room_popup(self):
        self.sendButton("rooms")
        self.Window.after(500, self.show_room_picker)

    def show_room_picker(self):
        picker = Toplevel()
        picker.title("Join Room")
        picker.geometry("300x400")
        picker.configure(bg="#2C3E50")
        
        Label(picker, text="Available Rooms", font="Helvetica 12 bold", 
              bg="#2C3E50", fg="#EAECEE", pady=10).pack()

        rooms = getattr(self.sm, 'room_list', [])
        
        if not rooms:
            Label(picker, text="No active rooms found.", bg="#2C3E50", fg="#E74C3C").pack(pady=20)
        else:
            for room_name in rooms:
                btn = Button(picker, 
                             text=room_name, 
                             font="Helvetica 11", 
                             bg="#3498DB", 
                             fg="white", 
                             width=25,
                             command=lambda r=room_name: self.join_specific_room(r, picker))
                btn.pack(pady=5)
        
        Button(picker, text="Cancel", command=picker.destroy).pack(side=BOTTOM, pady=10)

    def join_specific_room(self, room_name, window):
        self.sendButton(f"c {room_name}")
        window.destroy()
    def open_poem_popup(self):
        number = simpledialog.askinteger("Poem", "Enter poem number (1-108):")
        if number:
            self.sendButton(f"p{number}")

    def open_search_popup(self):
        term = simpledialog.askstring("Search", "Enter search phrase:")
        
        if term:
            self.sendButton(f"? {term}")
            
    def clear_chat(self):
        self.textCons.config(state=NORMAL)
        self.textCons.delete(1.0, END)
        self.textCons.config(state=DISABLED)

    def update_buttons(self, state):
        
        if state == S_LOGGEDIN:
            self.btn_who.config(state=NORMAL)
            self.btn_time.config(state=NORMAL)
            self.btn_create.config(state=NORMAL)
            self.btn_join.config(state=NORMAL)
            self.btn_poem.config(state=NORMAL)
            self.btn_search.config(state=NORMAL)
            self.btn_bye.config(state=DISABLED)
            
        elif state == S_CHATTING:
            self.btn_who.config(state=DISABLED)
            self.btn_time.config(state=DISABLED)
            self.btn_create.config(state=DISABLED)
            self.btn_join.config(state=DISABLED)
            self.btn_poem.config(state=DISABLED)
            self.btn_search.config(state=DISABLED)
            self.btn_bye.config(state=NORMAL)

    def update_member_list(self):
        current_members = getattr(self.sm, 'members', [])
        
        if not current_members:
            display_text = "Members: (Not Connected)"
        else:
            sorted_members = sorted(current_members)
            display_text = "Members: " + ", ".join(sorted_members)
            
        self.labelMembers.config(text=display_text)

    def get_user_tag(self, text):
        try:
            if text.startswith("[") and "]" in text:
                username = text.split("]")[0][1:] 
                
                if username not in self.color_map:
                    picked_color = self.colors[self.color_index % len(self.colors)]
                    self.color_map[username] = picked_color
                    self.color_index += 1
                    
                    tag_name = f"user_{username}"
                    self.textCons.tag_config(tag_name, 
                                             foreground=picked_color, 
                                             justify='left', 
                                             lmargin1=10, 
                                             lmargin2=10)
                
                return f"user_{username}"
        except:
            pass
            
        return "peer"

    def proc(self):
        while True:
            read, write, error = select.select([self.socket], [], [], 0)
            peer_msg = []
            if self.socket in read:
                peer_msg = self.recv()
            
            if len(self.my_msg) > 0 or len(peer_msg) > 0:
                state_before = self.sm.get_state()
                system_msg = self.sm.proc(self.my_msg, peer_msg)
                current_state = self.sm.get_state()
                self.update_buttons(current_state)
                self.update_member_list()
                
                if len(self.my_msg) > 0:
                    if state_before == S_CHATTING:
                        if self.my_msg != "bye":
                            self.textCons.config(state=NORMAL)
                            self.textCons.insert(END, self.my_msg.rstrip() + "\n", 'me')
                            self.textCons.config(state=DISABLED)
                            self.textCons.see(END)
                    self.my_msg = ""
                
                if len(system_msg) > 0:
                    clean_msg = system_msg.rstrip()
                    
                    self.textCons.config(state=NORMAL)
                    
                    state_after = self.sm.get_state()
                    
                    if state_after == S_CHATTING:
                        if ("Connect to" in clean_msg or 
                            "Request from" in clean_msg or 
                            "You are connected with" in clean_msg or 
                            "User is busy" in clean_msg or
                            "joined" in clean_msg or
                            "left the chat" in clean_msg):
                            
                            self.textCons.insert(END, clean_msg + "\n", 'sys')
                        else:
                            dynamic_tag = self.get_user_tag(clean_msg)
                            self.textCons.insert(END, clean_msg + "\n", dynamic_tag)

                    else:
                        if "disconnected from" in clean_msg:
                             self.textCons.insert(END, clean_msg + "\n", 'sys')
                        else:
                             self.textCons.insert(END, clean_msg + "\n")
                        
                    self.textCons.config(state=DISABLED)
                    self.textCons.see(END)

    def run(self):
        self.login()
# create a GUI class object
if __name__ == "__main__": 
    g = GUI()