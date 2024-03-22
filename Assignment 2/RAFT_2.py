import threading
import time
import random
import zmq
import math
import os
from zmq.utils.monitor import recv_monitor_message
from typing import Dict, Any

EVENT_MAP = {}
print("Event names:")
for name in dir(zmq):
    if name.startswith('EVENT_'):
        value = getattr(zmq, name)
        # print("%21s : %4i" % (name, value))
        EVENT_MAP[value] = name

def event_monitor(monitor: zmq.Socket,node_id,follower_id) -> None:
    while monitor.poll():
        evt: Dict[str, Any] = {}
        mon_evt = recv_monitor_message(monitor)
        evt.update(mon_evt)
        evt['description'] = EVENT_MAP[evt['event']]
        # print(f"Event: {evt}") 
        if evt['event'] == zmq.EVENT_ACCEPT_FAILED:
            print("Connection to Node "+str(id)+" failed. Retrying...")
            with open("logs_node_"+str(node_id)+"/dump.txt", "a", newline="") as file:
                file.write("“Error occurred while sending RPC to Node "+str(node_id)+"\n")
            break
    monitor.close()
    print()
    # print("event monitor thread done!")

class RaftNode:
    def __init__(self, node_id):
        """
        From Pseudocode 1/9
        """
        self.node_id = node_id
        self.current_term = 0
        self.voted_for = None
        self.log = []
        self.data_truths = {}
        self.commit_length = 0
        self.current_role = "Follower"
        self.current_leader = None
        self.votes_received = set()
        self.sent_length = []
        self.acked_length = []

        self.global_zmq_socket = zmq.Context().socket(zmq.REP)
        self.global_zmq_socket.bind("tcp://*:5558")

        # Connection to Nodes needs to be there somehow, let's assume it's a list of addresses
        # self.connections = {'1': "tcp://localhost:5556", '2': "tcp://localhost:5557", '3': "tcp://localhost:5558", '4': "tcp://localhost:5559", '5': "tcp://localhost:5560"}
        self.connections = {'2': "tcp://localhost:5557", '3': "tcp://localhost:5558", '4': "tcp://localhost:5559", '5': "tcp://localhost:5560"}
        self.handle_timers()
        # {1: IP, 2: IP}
        self.clients = {}

        # self.log_file =  open("logs_node_0/logs.txt", "w")
        if os.path.isfile("logs_node_"+str(node_id)+"/logs.txt"):
            os.remove("logs_node_"+str(node_id)+"/logs.txt")
        if os.path.isfile("logs_node_"+str(node_id)+"/metadata.txt"):
            os.remove("logs_node_"+str(node_id)+"/metadata.txt")
        if os.path.isfile("logs_node_"+str(node_id)+"/dump.txt"):
            os.remove("logs_node_"+str(node_id)+"/dump.txt")

        self.LEADER_LEASE_TIMEOUT = 7
        self.HEARTBEAT_TIMEOUT = 1

    def handle_timers(self, lease_timer_follower_duration):
        if self.current_role == 'Leader':
            self.timer = threading.Timer(self.HEARTBEAT_TIMEOUT, self.periodic_heartbeat)
            self.timer.start()
            self.lease_timer = threading.Timer(self.LEADER_LEASE_TIMEOUT, self.step_down)
            self.lease_timer.start()
        else:
            MIN_TIMEOUT = 5
            MAX_TIMEOUT = 10
            self.timer = threading.Timer(random.randint(MIN_TIMEOUT, MAX_TIMEOUT), self.leader_failed_or_election_timeout)
            self.timer.start()
            self.lease_timer = threading.Timer(lease_timer_follower_duration, self.step_down)
            self.lease_timer.start()

    def cancel_timers(self):
        if hasattr(self, 'timer'):
            self.cancel_timers()
        if hasattr(self, 'lease_timer'):
            self.lease_timer.cancel()

    def step_down(self):
        self.current_role = "Follower"
        self.voted_for = None
        self.cancel_timers()
        self.handle_timers()

    def main(self):
    
        while True:
            message = self.global_zmq_socket.recv().decode()
            message_parts = message.split(" ")
            if message_parts[0] == "VoteRequest":
                cId, cTerm, cLogLength, cLogTerm, LEADER_LEASE_TIMEOUT = message_parts[1:]
                self.handle_vote_request(int(cId), int(cTerm), int(cLogLength), int(cLogTerm), int(LEADER_LEASE_TIMEOUT))
            elif message_parts[0] == "VoteResponse":
                voterId, term, granted = message_parts[1:]
                self.handle_vote_response(int(voterId), int(term), granted == "True")
            elif message_parts[0] == "LogRequest":
                leader_id, term, prefix_len, prefix_term, leader_commit, suffix = message_parts[1:]
                suffix = eval(suffix)
                self.handle_log_request(int(leader_id), int(term), int(prefix_len), int(prefix_term), int(leader_commit), suffix)
            elif message_parts[0] == "LogResponse":
                follower_id, term, ack, success = message_parts[1:]
                self.handle_log_response(int(follower_id), int(term), int(ack), success == "True")
            # elif message_parts[0] == "AppendEntries":
            #     prefix_len, leader_commit, suffix = message_parts[1:]
            #     self.append_entries(int(message_parts[1]), int(message_parts[2]), message_parts[3])
            elif message_parts[0] == "Forward":
                node_id, current_term, message = message_parts[1:]
                self.broadcast_messages(message)
            elif message_parts[0] == "GET":
                key = message_parts[1]
                self.global_zmq_socket.send(str(self.data_truths[key]).encode())
            elif message_parts[0] == "SET":
                key, value = message_parts[1:]
                self.data_truths[key] = value
                self.broadcast_messages("SET " + key + " " + value)
            elif message_parts[0] == "CommitOnFollowers":
                self.commit_log_entries_follower()

    def get_query(self, key):
        return self.data_truths[key] if key in self.data_truths else "Key not found."
        
    def set_query(self, key, value):
        self.broadcast_messages("SET " + key + " " + value)

    def recovery_from_crash(self):
        """
        From Pseudocode 1/9
        """
        self.current_role = "Follower"
        self.votes_received = set()
        self.sent_length = []
        self.acked_length = []
        self.current_leader = None

    def leader_failed_or_election_timeout(self):
        """
        From Pseudocode 1/9
        """
        with open("logs_node_"+str(self.node_id)+"/dump.txt", "a", newline="") as file:
            file.write("Node "+str(self.node_id)+" election timer timed out, Starting election. \n")
        self.current_term += 1
        self.current_role = "Candidate"
        self.voted_for = self.node_id
        self.votes_received = {self.node_id}
        last_term = 0
        if len(self.log) > 0:
            last_term = self.log[-1]["term"]
        message = "VoteRequest " + str(self.node_id) + " " + str(self.current_term) + " " + str(len(self.log)) + " " + str(last_term) + " " + str(self.LEADER_LEASE_TIMEOUT)
        for n_id, connection in self.connections.items():
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            monitor = socket.get_monitor_socket()
            t = threading.Thread(target=event_monitor, args=(monitor,self.node_id,n_id))
            t.start()
            socket.connect(connection)
            socket.send(message.encode())
            # response = socket.recv().decode()
            # reply_type, voterId, voter_term, granted = response.split(" ")
            # if granted == "True":
            #     self.handle_vote_response(voterId, voter_term, granted)

    def handle_vote_request(self, cId, cTerm, cLogLength, cLogTerm, LEADER_LEASE_TIMEOUT):
        """
        From Pseudocode 2/9
        """
        if cTerm > self.current_term:
            self.current_role = "Follower"
            self.current_term = cTerm
            self.voted_for = None
        last_term = 0
        if len(self.log) > 0:
            last_term = self.log[-1]["term"]
        logOk = (cLogTerm > last_term) or (cLogTerm == last_term and cLogLength >= len(self.log))
        if cTerm == self.current_term and logOk and (self.voted_for is None or self.voted_for == cId):
            self.voted_for = cId
            message = "VoteResponse " + str(self.node_id) + " " + str(self.current_term) + " " + str(True)
            self.global_zmq_socket.send(message.encode())
            with open("logs_node_"+str(self.node_id)+"/dump.txt", "a", newline="") as file:
                file.write("Vote Granted for Node "+str(self.cId)+" in term."+str(cTerm) +"\n")
            # Even if the one you vote for doesn't wins, you'll recieve heartbeat so no need to handle response 
            # response = self.global_zmq_socket.recv().decode()
            # # Handle response
        else:
            # Reply no vote
            message = "VoteResponse " + str(self.node_id) + " " + str(self.current_term) + " " + str(False)
            self.global_zmq_socket.send(message.encode())
            with open("logs_node_"+str(self.node_id)+"/dump.txt", "a", newline="") as file:
                file.write("Vote denied for Node "+str(self.cId)+" in term."+str(cTerm) +"\n")
            # response = self.global_zmq_socket.recv().decode()
            # # Handle response
    
    def handle_vote_response(self, voterId, term, granted):
        """
        From Pseudocode 3/9
        """
        if self.current_role == 'Candidate' and term == self.current_term and granted:
            self.votes_received.add(voterId)
            if len(self.votes_received) >= math.ceil((len(self.connections) + 1) / 2):
                self.current_role = "Leader"
                with open("logs_node_"+str(self.node_id)+"/dump.txt", "a", newline="") as file:
                        file.write("Node "+str(self.node_id)+" became the leader for term "+str(term)+"\n")
                self.current_leader = self.node_id
                # Cancel election timer
                self.cancel_timers()
                self.handle_timers()
                # Send AppendEntries to all other nodes
                for follower, _ in self.connections.items():
                    self.sent_length[follower] = len(self.log)
                    self.acked_length[follower] = 0
                    self.replicate_log(self.node_id, follower)
        elif term > self.current_term:
            self.current_role = "Follower"
            self.current_term = term
            self.voted_for = None
            self.cancel_timers()
            self.handle_timers()

    def broadcast_messages(self, message):
        """
        From Pseudocode 4/9
        """
        if self.current_role == "Leader":
            self.log.append({"term": self.current_term, "message": message})
            self.acked_length[self.node_id] = len(self.log)
            for follower, _ in self.connections.items():
                self.replicate_log(self.node_id, follower)
        else:
            # Forward to Leader
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.connect(self.connections[self.current_leader])
            message = "Forward " + str(self.node_id) + " " + str(self.current_term) + " " + message
            socket.send(message.encode())

    def periodic_heartbeat(self):
        """
        From Pseudocode 4/9
        """
        if self.current_role == "Leader":
            # TODO = "Leader {NodeID of Leader} lease renewal failed. Stepping Down."
            with open("logs_node_"+str(self.node_id)+"/dump.txt", "a", newline="") as file:
                file.write("Leader "+str(self.node_id)+" sending heartbeat & Renewing Lease \n")
            for follower, _ in self.connections.items():
                self.replicate_log(self.node_id, follower)

    def replicate_log(self, leader_id, follower_id):
        """
        From Pseudocode 5/9
        """
        prefix_len = self.sent_length[follower_id]
        suffix = self.log[prefix_len:]
        prefix_term = 0
        if prefix_len > 0:
            prefix_term = self.log[prefix_len - 1]["term"]
        message = "LogRequest " + str(leader_id) + " " + str(self.current_term) + " " + str(prefix_len) + " " + str(prefix_term) + " " + str(self.commit_length) + " " + str(suffix)
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        monitor = socket.get_monitor_socket()
        t = threading.Thread(target=event_monitor, args=(monitor,self.node_id,follower_id))
        t.start()
        socket.connect(self.connections[follower_id])
        socket.send(message.encode())

    def handle_log_request(self, leader_id, term, prefix_len, prefix_term, leader_commit, suffix):
        """
        From Pseudocode 6/9
        """
        if term > self.current_term:
            self.current_term = term
            self.voted_for = None
            self.cancel_timers()
            self.handle_timers()
        if term == self.current_term:
            self.current_role = "Follower"
            self.current_leader = leader_id
        logOk = len(self.log) >= prefix_len and (self.log[prefix_len]["term"] == prefix_term or prefix_len == 0)
        if term == self.current_term and logOk:
            self.append_entries(prefix_len, leader_commit, suffix)
            ack = prefix_len + len(suffix)
            log_response_message = "LogResponse " + str(self.node_id) + " " + str(self.current_term) + " " + str(ack) + " " + str(True)
            self.global_zmq_socket.send(log_response_message.encode())
        else:
            log_response_message = "LogResponse " + str(self.node_id) + " " + str(self.current_term) + " " + str(prefix_len) + " " + str(False)
            self.global_zmq_socket.send(log_response_message.encode())

    def append_entries(self, prefix_len, leader_commit, suffix):
        """
        From Pseudocode 7/9
        """
        if len(suffix) > 0 and len(self.log) > prefix_len:
            index = min(len(self.log), prefix_len + len(suffix)) - 1
            if self.log[index]["term"] != suffix[index - prefix_len]["term"]:
                self.log = self.log[:prefix_len]
        
        if prefix_len + len(suffix) > len(self.log):
            for i in range(len(self.log) - prefix_len, len(suffix)):
                self.log.append(suffix[i])
                with open("logs_node_"+str(self.node_id)+"/dump.txt", "a", newline="") as file:
                    file.write("Node "+str(self.node_id)+"  accepted AppendEntries RPC from "+str(self.current_leader)+ "\n")

        if leader_commit > self.commit_length:
            for i in range(self.commit_length, leader_commit):
                # deliver log[i].message to application
                # Commit Here
                # TODO : Check if correct or not
                message = self.log[i]["message"]
                if message.startswith("SET"):
                    _, key, value = message.split(" ")
                    self.data_truths[key] = value
            self.commit_length = leader_commit

            if os.path.isfile("logs_node_"+str(self.node_id)+"/metadata.txt"):
                os.remove("logs_node_"+str(self.node_id)+"/metadata.txt")
            with open("logs_node_"+str(self.node_id)+"/metadata.txt", "w") as file:
                file.write("Commit length "+str(self.commit_length)+" Term "+str(self.current_term)+" Node ID "+str(self.voted_for))

    def handle_log_response(self, follower_id, term, ack, success):
        """
        From Pseudocode 8/9
        """
        if term == self.current_term and self.current_role == "Leader":
            if success and ack >= self.acked_length[follower_id]:
                self.acked_length[follower_id] = ack
                self.sent_length[follower_id] = ack
                self.commit_log_entries()
            elif self.sent_length[follower_id] > 0:
                self.sent_length[follower_id] -= 1
                self.replicate_log(self.node_id, follower_id)
        elif term > self.current_term:
            self.current_role = "Follower"
            self.current_term = term
            self.voted_for = None
            # Cancel election timer
            self.cancel_timers()
            self.handle_timers()

    def acks(self, length):
        """
        From Pseudocode 9/9
        """
        return sum(1 for ack in self.acked_length if ack >= length)
    

    def commit_log_entries(self):
        """
        From Pseudocode 9/9
        """
        min_acks = math.ceil((len(self.connections) + 1) / 2)
        ready = {i for i in range(len(self.log)) if self.acks(i) >= min_acks}
        if len(ready) != 0 and max(ready) > self.commit_length and self.log[max(ready) - 1]["term"] == self.current_term:
            for i in range(self.commit_length, max(ready)):
                last_message = self.log[i]["message"]
                if last_message.startswith("SET"):
                    _, key, value = last_message.split(" ")
                    self.data_truths[key] = value
                
                # deliver log[i].message to application
                self.broadcast_messages(self.log[i]["message"])

                # On the next LogRequest message that the leader sends to followers, the new value of 
                # commitLength will be included, causing the followers to commit and deliver the same log entries.



            self.commit_length = max(ready)
            if os.path.isfile("logs_node_"+str(self.node_id)+"/metadata.txt"):
                os.remove("logs_node_"+str(self.node_id)+"/metadata.txt")
            with open("logs_node_"+str(self.node_id)+"/metadata.txt", "w") as file:
                file.write("Commit length "+str(self.commit_length)+" Term "+str(self.current_term)+" Node ID "+str(self.voted_for))


    def commit_log_entries_follower(self):
        """
        From Pseudocode 9/9
        """
        

if __name__=='__main__':
    nodeId = 1
    print("Starting Node with ID " + str(nodeId))
    node = RaftNode(nodeId)
    try:
        node.main()
        # context = zmq.Context()
        # socket = context.socket(zmq.REQ)
    # Our event handling part
        # monitor = socket.get_monitor_socket()
        # t = threading.Thread(target=event_monitor, args=(monitor,1,0))
        # t.start()
        # socket.connect("tcp://localhost:5556")
        # socket.send("message".encode())

    except KeyboardInterrupt:
        node.timer.cancel()
        print("Exiting Node with ID " + str(nodeId))
        os._exit(0)