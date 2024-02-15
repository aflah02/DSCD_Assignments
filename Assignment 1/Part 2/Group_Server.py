import zmq
import uuid

class GroupServer:
    def __init__(self):
        self.context = zmq.Context()
        self.server_socket = self.context.socket(zmq.REQ)
        self.server_socket.connect("tcp://localhost:5555")
        self.group_server_socket = self.context.socket(zmq.REP)
        self.group_server_socket.bind("tcp://*:5556")
        self.group_id = None
        self.messages = []
        self.users = set()
        self.register_with_central_server()
        assert self.group_id is not None

    def register_with_central_server(self):
        print("Registering with Central Server")
        self.server_socket.send(b"REGISTER_GROUP_SERVER")
        print("Waiting for response from Central Server")
        response = self.server_socket.recv()
        print(f"Received response from Central Server: {response}")
        self.group_id = response.decode().split(" ")[1]

    def handle_users(self):
        message = self.group_server_socket.recv().decode()
        if message.startswith("JOIN_GROUP"):
            user_id = message.split(" ")[1]
            self.users.add(user_id)
            self.group_server_socket.send(f"User {user_id} joined the group".encode())
        elif message.startswith("LEAVE_GROUP"):
            user_id = message.split(" ")[1]
            self.users.remove(user_id)
            self.group_server_socket.send(f"User {user_id} left the group".encode())
        elif message.startswith("GET_ALL_MESSAGES"):
            self.group_server_socket.send(str(self.messages).encode())
        elif message.startswith("GET_MESSAGE_AFTER"):
            time_after = int(message.split(" ")[1])
            first_message_idx_after = -1
            for i, message in enumerate(self.messages):
                if message["time"] > time_after:
                    first_message_idx_after = i
                    break
            if first_message_idx_after == -1:
                self.group_server_socket.send(str([]).encode())
            else:
                self.group_server_socket.send(str(self.messages[first_message_idx_after:]).encode())
                
    def handle_request(self):
        message = self.server_socket.recv_string()
        node_id = int(message.split(":")[0])
        print(f"Received request from Node {node_id}: {message}")
        # Add your custom logic to handle node requests

    def start(self):
        while True:
            self.handle_registration()
            self.handle_request()


if __name__ == "__main__":
    group_server = GroupServer()
    group_server.start()