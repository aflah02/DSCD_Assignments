import zmq
import uuid

class User:
    def __init__(self):
        self.context = zmq.Context()
        self.server_socket = self.context.socket(zmq.REQ)
        self.server_socket.connect("tcp://localhost:5555")
        self.user_id = str(uuid.uuid1())
        self.messages = []
        self.group_to_addr_mapping = None # [(group_name, port), ...]
        self.groups_joined = set()

    def get_group_details(self):
        print("Getting all groups")
        self.server_socket.send(b"GET_ALL_GROUPS")
        print("Waiting for response from Central Server")
        response = self.server_socket.recv()
        print(f"Received response from Central Server: {response}")
        self.group_to_addr_mapping = eval(response.decode())

    def join_group(self, group_name):
        desiredAddress = None
        for group, addr in self.group_to_addr_mapping:
            if group == group_name:
                desiredAddress = addr
                break
        print("Desired Address: ", desiredAddress)
        if desiredAddress is None:
            print("Group not found")
            return
        group_server_socket = self.context.socket(zmq.REQ)
        group_server_socket.connect(f"tcp://{desiredAddress.replace('0.0.0.0', 'localhost')}")
        print(f"JOINING GROUP {group_name}")
        group_server_socket.send(f"JOIN_GROUP ; {self.user_id}".encode())
        print("Waiting for response from Group Server")
        response = group_server_socket.recv()
        print(response.decode())

    def leave_group(self, group_name):
        desiredAddress = None
        for group, addr in self.group_to_addr_mapping:
            if group == group_name:
                desiredAddress = addr
                break
        print("Desired Address: ", desiredAddress)
        if desiredAddress is None:
            print("Group not found")
            return
        group_server_socket = self.context.socket(zmq.REQ)
        group_server_socket.connect(f"tcp://{desiredAddress.replace('0.0.0.0', 'localhost')}")
        print(f"LEAVING GROUP {group_name}")
        group_server_socket.send(f"LEAVE_GROUP ; {self.user_id}".encode())
        print("Waiting for response from Group Server")
        response = group_server_socket.recv()
        print(response.decode())

    def send_message(self, group_name, message):
        desiredAddress = None
        for group, addr in self.group_to_addr_mapping:
            if group == group_name:
                desiredAddress = addr
                break
        print("Desired Address: ", desiredAddress)
        if desiredAddress is None:
            print("Group not found")
            return
        group_server_socket = self.context.socket(zmq.REQ)
        group_server_socket.connect(f"tcp://{desiredAddress.replace('0.0.0.0', 'localhost')}")
        print(f"SENDING MESSAGE {message} TO GROUP {group_name}")
        group_server_socket.send(f"SEND_MESSAGE ; {self.user_id} ; {message}".encode())
        response = group_server_socket.recv()
        print(response.decode())

    def get_all_messages(self, group_name):
        desiredAddress = None
        for group, addr in self.group_to_addr_mapping:
            if group == group_name:
                desiredAddress = addr
                break
        print("Desired Address: ", desiredAddress)
        if desiredAddress is None:
            print("Group not found")
            return
        group_server_socket = self.context.socket(zmq.REQ)
        group_server_socket.connect(f"tcp://{desiredAddress.replace('0.0.0.0', 'localhost')}")
        print(f"GETTING ALL MESSAGES FROM GROUP {group_name}")
        group_server_socket.send(f"GET_MESSAGE ; {self.user_id}".encode())
        response = group_server_socket.recv()
        print(eval(response.decode()))

    def get_messages_after(self, group_name, time):
        desiredAddress = None
        for group, addr in self.group_to_addr_mapping:
            if group == group_name:
                desiredAddress = addr
                break
        print("Desired Address: ", desiredAddress)
        if desiredAddress is None:
            print("Group not found")
            return
        group_server_socket = self.context.socket(zmq.REQ)
        group_server_socket.connect(f"tcp://{desiredAddress.replace('0.0.0.0', 'localhost')}")
        print(f"GETTING ALL MESSAGES FROM GROUP {group_name} AFTER {time}")
        # Time is in HH:MM:SS format
        group_server_socket.send(f"GET_MESSAGE ; {self.user_id} ; {time}".encode())
        response = group_server_socket.recv()
        print(eval(response.decode()))

if __name__ == "__main__":
    user = User()
    print("Welcome to the chat application")
    print("Choose an option")
    print("1. Get all groups")
    print("2. Join a group")
    print("3. Leave a group")
    print("4. Send a message")
    print("5. Get all messages")
    print("6. Get messages after a particular time")
    print("7. Exit")
    while True:
        input_option = int(input("Enter your choice: "))
        if input_option == 1:
            user.get_group_details()
        elif input_option == 2:
            group_id = input("Enter the group id: ")
            user.join_group(group_id)
        elif input_option == 3:
            group_id = input("Enter the group id: ")
            user.leave_group(group_id)
        elif input_option == 4:
            group_id = input("Enter the group id: ")
            message = input("Enter the message: ")
            user.send_message(group_id, message)
        elif input_option == 5:
            group_id = input("Enter the group id: ")
            user.get_all_messages(group_id)
        elif input_option == 6:
            group_id = input("Enter the group id: ")
            time = input("Enter the time: ")
            user.get_messages_after(group_id, time)
        elif input_option == 7:
            break
        else:
            print("Invalid option")
