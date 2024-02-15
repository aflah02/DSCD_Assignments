import zmq
import uuid

class CentralServer:
    def __init__(self):
        print("Central Server started")
        self.context = zmq.Context()
        self.server_socket = self.context.socket(zmq.REP)
        print("Central Server socket created")
        self.server_socket.bind("tcp://*:5555")
        print("Central Server socket bound")
        self.node_ids = set()

    def start(self):
        while True:
            print("Waiting for message from node")
            message = self.server_socket.recv()
            print(f"Received message: {message}")
            if message.startswith(b"REGISTER"):
                # Register new node and assign a unique id
                node_id = str(uuid.uuid1())
                self.node_ids.add(node_id)
                # str_to_send = f"NODE_ID: {node_id}"
                str_to_send = f"NODE_ID: {node_id}"
                byte_encoded = str_to_send.encode()
                self.server_socket.send(byte_encoded)
                print(f"Node {node_id} registered. All IDs: {self.node_ids}")
            elif message.startswith(b"GET_ALL_GROUPS"):
                # Return all group ids
                groups = " ".join(self.node_ids)
                self.server_socket.send(groups.encode())
            else:
                self.server_socket.send("Invalid message format. Use 'REGISTER'")


if __name__ == "__main__":
    central_server = CentralServer()
    central_server.start()