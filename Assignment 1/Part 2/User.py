import zmq
import uuid

class User:
    def __init__(self):
        self.context = zmq.Context()
        self.server_socket = self.context.socket(zmq.REQ)
        self.server_socket.connect("tcp://localhost:5555")
        self.group_server_socket = self.context.socket(zmq.REQ)
        self.group_server_socket.bind("tcp://localhost:5556")
        self.user_id = str(uuid.uuid1())
        self.messages = []
        self.group_to_port_mapping = None
        self.groups_joined = set()

    def join_group(self, group_id):
        self.group_server_socket.send(f"JOIN_GROUP {group_id} {self.user_id}".encode())
        response = self.group_server_socket.recv()
        print(response.decode())

    def leave_group(self, group_id):
        self.group_server_socket.send(f"LEAVE_GROUP {group_id} {self.user_id}".encode())
        response = self.group_server_socket.recv()
        print(response.decode())

    def send_message(self, group_id, message):
        self.group_server_socket.send(f"SEND_MESSAGE {group_id} {self.user_id} {message}".encode())
        response = self.group_server_socket.recv()
        print(response.decode())

    def get_all_messages(self, group_id):
        self.group_server_socket.send(f"GET_ALL_MESSAGES".encode())
        response = self.group_server_socket.recv()
        print(response.decode())

    def get_messages_after(self, group_id, time):
        self.group_server_socket.send(f"GET_MESSAGES_AFTER {time}".encode())
        response = self.group_server_socket.recv()
        print(response.decode())