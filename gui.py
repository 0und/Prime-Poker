import tkinter as tk
from tkinter import messagebox
import socket
import threading
import json
import env

HELP_MSG = """Commands:
    b: Begin game
    s: Show your hand
    S: Show game status
    p: Pass your turn
    d: Draw a card
    h: Help
    e: Exit
    t: Transfer
"""

class PokerCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Prime Poker Calculator")
        self.expression = ""
        self.cards_in_hand = []
        self.client_socket = None

        # One input field for both commands and expressions
        self.input_field = tk.Entry(self.root, width=30, font=("Arial", 16), bd=5, relief=tk.RIDGE)
        self.input_field.grid(row=0, column=0, columnspan=2)

        # Send button
        tk.Button(self.root, text="Send", command=self.on_send_clicked).grid(row=0, column=2)

        # Clear button
        tk.Button(self.root, text="Clear", command=self.clear_input).grid(row=0, column=3)

        # Display cards
        self.cards_frame = tk.Frame(self.root)
        self.cards_frame.grid(row=1, column=0, columnspan=4)

        # Messages window (resizable, hidden by default)
        self.messages_window = tk.Toplevel(self.root)
        self.messages_window.title("Server Messages")
        self.messages_window.geometry("600x300")
        self.messages_window.resizable(True, True)
        self.messages_window.withdraw() 
        self.messages_window.protocol("WM_DELETE_WINDOW", self.messages_window.withdraw)

        self.messages_text = tk.Text(self.messages_window)
        self.messages_text.pack(fill=tk.BOTH, expand=True)

        # Connect and start listener
        self.connect_to_server()
        threading.Thread(target=self.receive_messages, daemon=True).start()

        self.init_ui()

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect(('0.0.0.0', env.port))
            self.client_socket.sendall(json.dumps({'action': 'join', 'name': 'GUI_Player'}).encode())
        except Exception:
            messagebox.showerror("Connection Error", "Failed to connect to server")

    def receive_messages(self):
        while True:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                msg = data.decode().strip()
                print(f'Received: {msg}')
                self.messages_text.insert(tk.END, "-----\n" + msg + "\n")
                self.messages_text.see(tk.END)
                # If backend sends an updated list of cards:
                try:
                    data_json = json.loads(msg)
                    if 'cards' in data_json:
                        self.update_cards_in_hand(data_json['cards'])
                except:
                    pass
            except:
                break

    def on_send_clicked(self):
        cmd = self.input_field.get().strip()
        if not self.client_socket or not cmd:
            return
        self.handle_command(cmd)
        self.input_field.delete(0, tk.END)
        self.expression = ""

    def clear_input(self):
        self.input_field.delete(0, tk.END)
        self.expression = ""

    def handle_command(self, cmd):
        c = cmd[0]  # first char
        if c == 'h':
            message = {'action': 'help', 'name': 'GUI_Player'}
        elif c == 'e':
            message = {'action': 'disconnect', 'name': 'GUI_Player'}
        elif c == 'b':
            message = {'action': 'start'}
        elif c == 's':
            message = {'action': 'show', 'name': 'GUI_Player'}
        elif c == 'p':
            message = {'action': 'skip', 'name': 'GUI_Player'}
        elif c == 'd':
            message = {'action': 'draw', 'name': 'GUI_Player'}
        elif c == 'S':
            message = {'action': 'status', 'name': 'GUI_Player'}
        elif c == 't':
            message = {'action': 'transfer', 'name': 'GUI_Player', 'content': cmd}
        else:
            # Anything else = "play" the entire string
            message = {'action': 'play', 'name': 'GUI_Player', 'content': cmd}
        self.client_socket.sendall(str(message).encode())

    def update_cards_in_hand(self, cards):
        self.cards_in_hand = cards
        self.create_card_buttons()

    def create_card_buttons(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        for card in self.cards_in_hand:
            if isinstance(card, dict):
                display_text = self.format_card(card)
            else:
                display_text = str(card)
            btn = tk.Button(self.cards_frame, text=display_text, command=lambda c=card: self.append_to_expression(c))
            btn.pack(side=tk.LEFT, padx=3)

    def format_card(self, card):
        suit = card.get('suit', '?')
        val = card.get('value', 0)
        # Mirror the Card.__str__ logic
        if val == 1: 
            val_str = 'A'
        elif val == 11:
            val_str = 'J'
        elif val == 12:
            val_str = 'Q'
        elif val == 13:
            val_str = 'K'
        elif val == 0 and suit == 'Joker':
            val_str = 'Joker'
        else:
            val_str = str(val)
        return f"{val_str} of {suit}"

    def append_to_expression(self, value):
        # If it's a dict, build a short representation for expression
        if isinstance(value, dict):
            v = value.get('value', '?')
            suit = value.get('suit', '?')
            if v == 1: 
                v_str = 'A'
            elif v == 11:
                v_str = 'J'
            elif v == 12:
                v_str = 'Q'
            elif v == 13:
                v_str = 'K'
            elif v == 0 and suit == 'Joker':
                v_str = 'Joker'
            else:
                v_str = str(v)
            text = f"{v_str}"
        else:
            text = str(value)
        self.expression += text
        self.input_field.delete(0, tk.END)
        self.input_field.insert(0, self.expression)

    def toggle_messages_window(self):
        if self.messages_window.state() == 'withdrawn':
            self.messages_window.deiconify()
        else:
            self.messages_window.withdraw()

    def create_operator_buttons(self):
        ops_frame = tk.Frame(self.root)
        ops_frame.grid(row=2, column=0, columnspan=4)
        for op in ['*', '^', '=']:
            tk.Button(ops_frame, text=op, command=lambda o=op: self.append_to_expression(o)).pack(side=tk.LEFT, padx=5)

    def create_command_buttons(self):
        cmds_frame = tk.Frame(self.root)
        cmds_frame.grid(row=3, column=0, columnspan=4)
        for cmd in ['b','s','S','p','d','h','e','t']:
            tk.Button(cmds_frame, text=cmd, command=lambda c=cmd: self.handle_command(c)).pack(side=tk.LEFT, padx=5)
        tk.Button(cmds_frame, text="Messages", command=self.toggle_messages_window).pack(side=tk.LEFT, padx=5)

    def calculate(self):
        if '^' in self.expression:
            base, exp = self.expression.split('^')
            result = str(eval(f"{base}**{exp}"))
        else:
            result = str(eval(self.expression))
        self.expression = result
        self.input_field.delete(0, tk.END)
        self.input_field.insert(0, result)

    def init_ui(self):
        self.create_card_buttons()
        self.create_operator_buttons()
        self.create_command_buttons()

if __name__ == "__main__":
    root = tk.Tk()
    calculator = PokerCalculator(root)
    root.mainloop()
