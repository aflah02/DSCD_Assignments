import zmq
import datetime
import time

class GroupServer:
    def __init__(self, name, ip, port):
        self.group_name = name
        self.group_address = f"{ip}:{port}"
        self.context = zmq.Context()
        self.server_socket = self.context.socket(zmq.REQ)
        self.server_socket.connect("tcp://localhost:5555")
        self.group_server_socket = self.context.socket(zmq.REP)
        self.group_server_socket.bind(f"tcp://{self.group_address}")
        self.messages = []
        self.users = set()
        self.register_with_central_server()

    def register_with_central_server(self):
        print("Registering with Central Server")
        self.server_socket.send(b"REGISTER_GROUP_SERVER ; " + self.group_name.encode() + b" ; " + self.group_address.encode())
        print("Waiting for response from Central Server")
        response = self.server_socket.recv()
        print(f"Received response from Central Server: {response}")
        print("SUCCESS")

    def handle_users(self):
        recvd = self.group_server_socket.recv().decode()
        print(f"Received message: {recvd}")
        ls_recvd = recvd.split(" ; ")
        message = ls_recvd[0]
        if message.startswith("JOIN_GROUP"):
            assert len(ls_recvd) == 2
            user_id = ls_recvd[1]
            print(f"JOIN REQUEST FROM {user_id}")
            self.users.add(user_id)
            self.group_server_socket.send(f"SUCCESS".encode())
        elif message.startswith("LEAVE_GROUP"):
            assert len(ls_recvd) == 2
            user_id = ls_recvd[1]
            print(f"LEAVE REQUEST FROM {user_id}")
            if user_id not in self.users:
                self.group_server_socket.send(f"FAILED : User not in group".encode())
                return
            self.users.remove(user_id)
            self.group_server_socket.send(f"SUCCESS".encode())
        elif message.startswith("SEND_MESSAGE"):
            assert len(ls_recvd) == 3
            user_id = ls_recvd[1]
            # check if user is in group
            if user_id not in self.users:
                self.group_server_socket.send(f"FAIL".encode())
                return
            message = ls_recvd[2]
            print(f"MESSAGE SEND FROM {user_id}")
            # Get time in HH:MM:SS
            curr_time = datetime.datetime.now().strftime("%H:%M:%S")
            self.messages.append({"user_id": user_id, "message": message, "time": curr_time})
            self.group_server_socket.send(f"SUCCESS".encode())
        elif message.startswith("GET_MESSAGE"):
            assert len(ls_recvd) == 2 or len(ls_recvd) == 3
            print(f"MESSAGE REQUEST FROM {ls_recvd[1]}")
            if len(ls_recvd) == 2:
                msg = str(self.messages).encode()
                self.group_server_socket.send(msg)
            else:
                time = str(ls_recvd[2])
                filtered_messages = []
                for message in self.messages:
                    message_time = datetime.datetime.strptime(message["time"], "%H:%M:%S")
                    query_time = datetime.datetime.strptime(time, "%H:%M:%S")
                    # Both are in HH:MM:SS format string
                    if message_time >= query_time:
                        filtered_messages.append(message)
                msg = str(filtered_messages).encode()
                self.group_server_socket.send(msg)

    def start(self):
        while True:
            self.handle_users()


if __name__ == "__main__":
    group_server = GroupServer("Slytherin", '0.0.0.0', 5558)
    group_server.start()