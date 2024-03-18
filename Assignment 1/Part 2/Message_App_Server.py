import zmq
import uuid

class CentralServer:
    def __init__(self):
        print("Central Server started")
        self.context = zmq.Context()
        self.server_socket = self.context.socket(zmq.REP)
        print("Central Server socket created")
        self.server_socket.bind("tcp://*:3389")
        print("Central Server socket bound")
        self.groups = []

    def start(self):
        while True:
            print("Waiting for message from node")
            recvd = self.server_socket.recv().decode()
            print(f"Received message: {recvd}")
            ls_recvd = recvd.split(" ; ")
            message = ls_recvd[0]
            print(f"Received message: {message}")
            if message.startswith("REGISTER"):
                assert len(ls_recvd) == 3
                group_name = ls_recvd[1]
                group_address = ls_recvd[2]
                print(f"JOIN REQUEST FROM {group_name} [{group_address}]")
                str_to_send = f"SUCCESS"
                byte_encoded = str_to_send.encode()
                self.server_socket.send(byte_encoded)
                print(f"Group {group_name} registered with address {group_address}")
                self.groups.append([group_name, group_address])
            elif message.startswith("GET_ALL_GROUPS"):
                # Return all group ids
                self.server_socket.send(str(self.groups).encode())
            else:
                self.server_socket.send("Invalid message format. Use 'REGISTER'")


if __name__ == "__main__":
    central_server = CentralServer()
    central_server.start()