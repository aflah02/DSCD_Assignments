import threading
import time
import random
import zmq
import math

class MyTimer(threading._Timer):
    started_at = None
    def start(self):
        self.started_at = time.time()
        threading._Timer.start(self)
    def elapsed(self):
        return time.time() - self.started_at
    def remaining(self):
        return self.interval - self.elapsed()

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
        self.global_zmq_socket.bind("tcp://*:5555")

        # Connection to Nodes needs to be there somehow, let's assume it's a list of addresses
        self.connections = {}
        # {1: IP, 2: IP}

        self.handle_timers()

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
            self.timer.cancel()
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
                cId, cTerm, cLogLength, cLogTerm = message_parts[1:]
                self.handle_vote_request(int(cId), int(cTerm), int(cLogLength), int(cLogTerm))
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
        self.current_term += 1
        self.current_role = "Candidate"
        self.voted_for = self.node_id
        self.votes_received = {self.node_id}
        last_term = 0
        if len(self.log) > 0:
            last_term = self.log[-1]["term"]
        message = "VoteRequest " + str(self.node_id) + " " + str(self.current_term) + " " + str(len(self.log)) + " " + str(last_term)
        for n_id, connection in self.connections.items():
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.connect(connection)
            socket.send(message.encode())
            response = socket.recv().decode()
            reply_type, voterId, voter_term, granted = response.split(" ")
            granted = granted == "True"
            self.handle_vote_response(voterId, voter_term, granted)

    def handle_vote_request(self, cId, cTerm, cLogLength, cLogTerm):
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
            # Even if the one you vote for doesn't wins, you'll recieve heartbeat so no need to handle response 
            # response = self.global_zmq_socket.recv().decode()
            # # Handle response
        else:
            # Reply no vote
            message = "VoteResponse " + str(self.node_id) + " " + str(self.current_term) + " " + str(False)
            self.global_zmq_socket.send(message.encode())
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
                self.current_leader = self.node_id
                # Cancel election timer
                self.cancel_timers()
                self.handle_timers()
                # Send AppendEntries to all other nodes
                for follower, _ in self.connections.items():
                    self.sent_length[follower] = len(self.log)
                    self.acked_length[follower] = len(self.log)
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
        time_left_in_lease = self.lease_timer.time_left()
        message = "LogRequest " + str(leader_id) + " " + str(self.current_term) + " " + str(prefix_len) + " " + str(prefix_term) + " " + str(self.commit_length) + " " + str(suffix)
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
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

        if leader_commit > self.commit_length:
            for i in range(self.commit_length, leader_commit):
                # deliver log[i].message to application
                self.broadcast_messages(self.log[i]["message"])
            self.commit_length = leader_commit

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
            self.commit_length = max(ready)