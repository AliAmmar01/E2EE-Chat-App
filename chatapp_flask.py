import queue
import requests
from flask import Flask, request, jsonify
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
import aes
import rsa

# Create a Flask app
app = Flask(__name__)

connected_user = {
    "ip": "",
    "port": "",
    "public_key": "",
    "aes_key": "",
    "name": "Stranger"
}

my_keys = {
    "public_key": "",
    "private_key": ""
}
myip = ""
myport = ""

myname = ""

# Queues for thread communication
msg_queue = queue.Queue()  # For passing received messages to the tkinter thread

# ChatWindow class for tkinter GUI
class ChatWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat App")
        self.root.geometry("400x500")

        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED)
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Entry for typing messages
        self.message_entry = tk.Entry(root, font=("Arial", 14))
        self.message_entry.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)

        # Bind Enter key to send message
        self.message_entry.bind("<Return>", lambda event: self.send_message())

        # Send button
        send_button = tk.Button(root, text="Send", command=self.send_message)
        send_button.pack(side=tk.RIGHT, padx=10, pady=10)

        # Start a timer to check for new messages
        self.root.after(100, self.check_messages)

    def send_message(self):
        message = self.message_entry.get().strip()
         #check if msg == /connect 
        if message.startswith("/connect"):
            ip, port = message.split(" ")[1:]
            self.add_message(f"\nYou:\n{message}")
            self.message_entry.delete(0, tk.END)
            initiate_connect(ip, port)
            return
        # Send a JSON payload
        enc_message = aes.aes_enc(message, connected_user.get("aes_key"))
        url = f'http://{connected_user.get("ip")}:{connected_user.get("port")}/chat'
        payload = {'msg': enc_message}
        try:
            r = requests.post(url, json=payload)  
            print(f"Response: {r.status_code} - {r.text}")  # Log the response
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")  # Handle connection errors
        #add the msg to the chat window
        self.add_message(f"\nYou:\n{message}")
        # Clear the message entry
        self.message_entry.delete(0, tk.END)  



    def check_messages(self):
        while not msg_queue.empty():
            message = msg_queue.get()
            self.add_message(message)
        self.root.after(100, self.check_messages)  # Schedule the next check

    def add_message(self, message):
    #change msg color corresponding to the sender
        if message.startswith("You:"):
            color = "blue"
        else:
            color = "green"
        self.chat_display.tag_config(color, foreground=color)
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

# Get message from client
@app.route('/chat', methods=['POST'])
def chat():
    msg = request.json  # Parse the JSON data sent by the client
    #add msg to queue
    msg1 = aes.aes_dec(msg.get("msg"), connected_user.get("aes_key"))
    msg_queue.put(f"{connected_user['name']}:\n{msg1}\n")
    return jsonify(msg)  # Respond with the same message

@app.route('/connection_request', methods=['POST'])
def initiate_connection():
    #check if i am in a connection
    if connected_user.get("aes_key") != "":
        return jsonify({"error": "already in a connection."})
    #promt user to accept connection
    x = messagebox.askyesno("Connection Request", "Do you want to connect with this user?")
    #if user declines connection
    #return jsonify({"error": "connection declined."})
    if not x:
        return jsonify({"error": "connection declined."})
    #else
    #save his public key
    data = request.json
    connected_user["public_key"] = data.get("public_key")
    #save his ip and port
    connected_user["ip"] = request.remote_addr
    connected_user["port"] = data.get("port")
    connected_user["name"] = data.get("name")
    #split 
    #reply with my public key
    return jsonify({"public_key": my_keys.get("public_key"), "name": myname})

@app.route('/start_connection', methods=['POST'])
def start_connection():
    #send me a aes key encrypted with my public key 
    #reply with a success message
    data = request.json
    #should be decrypted with my private key
    encrypted_aes_key = data.get("aes_key")
    #decrypt aes key
    key = rsa.decrypt_rsa(encrypted_aes_key, my_keys.get("private_key"))
    key = aes.string_to_key(key)
    connected_user["aes_key"] = key
    return jsonify({"success": "connection established."})
    
    


def initiate_connect(ip, port):
    if not ip or not port:
        messagebox.showerror("Error", "IP and Port must be provided!")
        return
    # Send connection request
    url = f"http://{ip}:{port}/connection_request"
    try:
        response = requests.post(url, json={"public_key": my_keys.get("public_key"), "port": myport, "name": myname})
        response_data = response.json()
        if "error" in response_data:
            messagebox.showerror("Connection Error", response_data["error"])
        else:
            # Save public key and initiate AES key exchange
            connected_user["ip"] = ip
            connected_user["port"] = port
            connected_user["public_key"] = response_data.get("public_key")
            connected_user["name"] = response_data.get("name")
            messagebox.showinfo("Connection", "Connection established. Public key exchanged!")
            #start aes key exchange
            #generate aes key
            aes_key = aes.generate_key()
            connected_user["aes_key"] = aes_key
            aes_key = aes.key_to_string(aes_key)
            #encrypt aes key with his public key
            encrypted_aes_key = rsa.encrypt_rsa(aes_key, connected_user.get("public_key"))
            #send aes key to him
            url = f"http://{ip}:{port}/start_connection"
            response = requests.post(url, json={"aes_key": encrypted_aes_key})
            response_data = response.json()
            if "error" in response_data:
                messagebox.showerror("Connection Error", response_data["error"])
                #clear data
                connected_user["ip"] = ""
                connected_user["port"] = ""
                connected_user["public_key"] = ""
                connected_user["aes_key"] = ""
            else:
                messagebox.showinfo("Connection", "AES key exchange successful!")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to connect: {e}")


if __name__ == '__main__':
    # Generate RSA key pair
    my_public_key, my_private_key = rsa.generate_keys()
    my_keys["public_key"] = my_public_key
    my_keys["private_key"] = my_private_key

    root = tk.Tk()
    chat_window = ChatWindow(root)

    myip = "0.0.0.0"
    myport = "12346"
    myname = "Omar"
    #start server on a thread and a while true loop to keep sending messages
    threading.Thread(target=app.run, args=(myip, myport)).start()   
    # msg_queue.put")
    msg_queue.put(f"Server started on ws://{myip}:{myport}")

    root.mainloop()