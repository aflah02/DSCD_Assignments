import threading
import time
import random
import zmq
import math
import os
from zmq.utils.monitor import recv_monitor_message
from typing import Dict, Any
import argparse
import json

class MyTimer:
    def __init__(self, interval, onEndCallback) -> None:
        self.interval = interval
        self.onEndCallback = onEndCallback
    
    def start(self, ):
        self.start_time = time.time()
        self._timer = threading.Timer(self.interval, self.onEndCallback if self.onEndCallback is not None else lambda: None)
        self._timer.start()

    def remaining(self):
        return self.start_time + self._timer.interval - time.time()
    
    def cancel(self):
        self._timer.cancel()

    def elapsed(self):
        return time.time() - self.start_time

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
        if evt['event'] == zmq.EVENT_CONNECT_RETRIED:
            print("Connection to Node "+str(id)+" failed. Retrying...")
            with open("logs_node_"+str(node_id)+"/dump.txt", "a", newline="") as file:
                file.write("Error occurred while sending RPC to Node "+str(follower_id)+"\n")
            print("Error occurred while sending RPC to Node "+str(follower_id))
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
        self.sent_length = {}
        self.acked_length = {}

        # Read connections.json
        with open('connections.json') as f:
            self.connections = json.load(f)

        self_addr = self.connections[str(node_id)]

        self_addr = self_addr.replace("localhost", "*")

        self.self_addr = self_addr

        del self.connections[str(node_id)]

        for key in self.connections:
            self.sent_length[key] = 0
            self.acked_length[key] = 0

        self.global_zmq_socket = zmq.Context().socket(zmq.PULL)
        self.global_zmq_socket.bind(self_addr)

        # Connection to Nodes needs to be there somehow, let's assume it's a list of addresses
        # self.connections = {'1': "tcp://localhost:5556", '2': "tcp://localhost:5557", '3': "tcp://localhost:5558", '4': "tcp://localhost:5559", '5': "tcp://localhost:5560"}
        # self.connections = {int(k): v for k, v in self.connections.items()}
        # {1: IP, 2: IP}
        self.clients = {}

        # self.log_file =  open("logs_node_0/logs.txt", "w")
        # TODO change the reconntruction of log file
        # if os.path.isfile("logs_node_"+str(node_id)+"/logs.txt"):
        #     os.remove("logs_node_"+str(node_id)+"/logs.txt")
        # if os.path.isfile("logs_node_"+str(node_id)+"/metadata.txt"):
        #     os.remove("logs_node_"+str(node_id)+"/metadata.txt")
        # if os.path.isfile("logs_node_"+str(node_id)+"/dump.txt"):
        #     os.remove("logs_node_"+str(node_id)+"/dump.txt")

        self.MAX_LEASE_TIMER_LEFT = 7
        self.HEARTBEAT_TIMEOUT = 1
        self.COUNT_OF_SUCCESSFUL_LEASE_RENEWALS = 0

        self.handle_timers()

    def handle_timers(self):
        print("handle timers called", self.current_role)
        if self.current_role == 'Leader':
            self.timer = MyTimer(self.HEARTBEAT_TIMEOUT, self.periodic_heartbeat)
            self.timer.start()
            self.lease_timer = MyTimer(self.MAX_LEASE_TIMER_LEFT, self.step_down)
            self.lease_timer.start()
        else:
            MIN_TIMEOUT = 10
            MAX_TIMEOUT = 20
            self.timer = MyTimer(random.randint(MIN_TIMEOUT, MAX_TIMEOUT), self.leader_failed_or_election_timeout)
            self.timer.start()
            self.lease_timer = MyTimer(self.MAX_LEASE_TIMER_LEFT, None)
            self.lease_timer.start()

    def cancel_timers(self):
        if hasattr(self, 'timer'):
            self.timer.cancel()
        if hasattr(self, 'lease_timer'):
            self.lease_timer.cancel()

    def step_down(self):
        if self.current_role == "Leader":
            print("Leader "+str(self.node_id)+" lease timer timed out. Stepping down.")
            self.current_role = "Follower"
            self.voted_for = None
            self.cancel_timers()
            self.handle_timers()

    def main(self):
        iteration = 0
        while True:
            print("Iteration: ", iteration)
            try:
                message = self.global_zmq_socket.recv().decode()
            except Exception as e:
                print("Exception: ", e)
                self.global_zmq_socket = zmq.Context().socket(zmq.PULL)
                self.global_zmq_socket.bind(self.self_addr)
                continue
            print("Received message: ", message , " at " , time.time())
            message_parts = message.split(" ")
            if message_parts[0] == "VoteRequest":
                cId, cTerm, cLogLength, cLogTerm = message_parts[1:]
                self.handle_vote_request(int(cId), int(cTerm), int(cLogLength), int(cLogTerm))
            elif message_parts[0] == "VoteResponse":
                voterId, term, granted, lease_timer_left_according_to_voter = message_parts[1:]
                self.handle_vote_response(int(voterId), int(term), granted == "True", float(lease_timer_left_according_to_voter))
            elif message_parts[0] == "LogRequest":
                print(message_parts)
                print("Length of message parts: ", len(message_parts))
                leader_id, term, prefix_len, prefix_term, leader_commit = message_parts[1:6]
                lease_timer_left_according_to_leader = message_parts[-1]
                suffix = message_parts[6:-1]
                suffix = " ".join(suffix)
                print(suffix)
                suffix = eval(suffix)
                print("Suffix: ", suffix)
                lease_timer_left_according_to_leader = float(lease_timer_left_according_to_leader)
                self.handle_log_request(int(leader_id), int(term), int(prefix_len), int(prefix_term), int(leader_commit), suffix, lease_timer_left_according_to_leader)
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
                # TODO: Need to change get_query to return only if reader
                key = message_parts[1]
                return_address = message_parts[2]
                status, returnVal = self.get_query(key)
                print("Get Query: ", status, returnVal)
                # Return the value to the return address
                # TODO : Check if client is active or not
                client_socket = zmq.Context().socket(zmq.PUSH)
                client_socket.connect(return_address)
                return_msg = str(status) + " " + str(returnVal)
                encoded_msg = return_msg.encode()
                client_socket.send(encoded_msg)
            elif message_parts[0] == "SET":
                # TODO  
                key, value,return_address = message_parts[1:]
                self.set_query(key, value,return_address)
            iteration += 1

    def get_query(self, key):
        if self.current_role == "Leader":
            print("Leader Get")
            print(self.data_truths)
            print(self.log)
            print(self.commit_length)
            if key in self.data_truths:
                return 1, self.data_truths[key]
            else:
                return 2, ""
        else:
            if self.current_leader is None:
                return 0, "None"
            else:
                return 0, self.current_leader
        
    def set_query(self, key, value,return_address):
        if self.current_role == "Leader":
            # don't we need to send some success or failure message to the client
            status = "1"
            client_socket = zmq.Context().socket(zmq.PUSH)
            client_socket.connect(return_address)
            client_socket.send(f"{status}".encode())
            self.broadcast_messages("SET " + key + " " + value)
        else:
            status = "0"
            returnVal = self.current_leader
            client_socket = zmq.Context().socket(zmq.PUSH)
            client_socket.connect(return_address)
            client_socket.send(f"{status} {returnVal}".encode())
            # return self.current_leader


    def recovery_from_crash(self):
        """
        From Pseudocode 1/9
        """
        self.current_role = "Follower"
        self.votes_received = set()
        self.sent_length = {}
        self.acked_length = {}
        for key in self.connections:
            self.sent_length[key] = 0
            self.acked_length[key] = 0
        self.current_leader = None

    def leader_failed_or_election_timeout(self):
        """
        From Pseudocode 1/9
        """
        with open("logs_node_"+str(self.node_id)+"/dump.txt", "a", newline="") as file:
            file.write("Node "+str(self.node_id)+" election timer timed out, Starting election. \n")

        print("Node "+str(self.node_id)+" election timer timed out, Starting election. ")
        self.current_term += 1
        self.current_role = "Candidate"
        self.voted_for = self.node_id
        self.votes_received = {self.node_id}
        last_term = 0
        if len(self.log) > 0:
            last_term = self.log[-1]["term"]
        message = "VoteRequest " + str(self.node_id) + " " + str(self.current_term) + " " + str(len(self.log)) + " " + str(last_term)
        for n_id, connection in self.connections.items():
            print("Sending Vote Request to Node "+str(n_id))
            context = zmq.Context()
            print("Context Created")
            socket = context.socket(zmq.PUSH)
            print("Socket Created")
            monitor = socket.get_monitor_socket()
            print("Monitor Created")
            t = threading.Thread(target=event_monitor, args=(monitor,self.node_id,n_id))
            print("Thread Created")
            t.start()
            print("Thread Started")
            socket.connect(connection)
            print("Connected")
            socket.send(message.encode())
            print("Message Sent")
            # response = socket.recv().decode()
            # reply_type, voterId, voter_term, granted = response.split(" ")
            # if granted == "True":
            #     self.handle_vote_response(voterId, voter_term, granted)
        self.cancel_timers()
        self.handle_timers()

    def handle_vote_request(self, cId, cTerm, cLogLength, cLogTerm):
        """
        From Pseudocode 2/9
        """
        self.cancel_timers()
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
            time_left_in_leader_lease = self.lease_timer.remaining()
            message = "VoteResponse " + str(self.node_id) + " " + str(self.current_term) + " " + str(True)  + " " + str(time_left_in_leader_lease)
            candidate_socket_addr = self.connections[str(cId)]
            context = zmq.Context()
            candidate_socket = context.socket(zmq.PUSH)
            monitor = candidate_socket.get_monitor_socket()
            print("Monitor Created")
            t = threading.Thread(target=event_monitor, args=(monitor,self.node_id,cId))
            print("Thread Created")
            t.start()
            candidate_socket.connect(candidate_socket_addr)
            candidate_socket.send(message.encode())
            with open("logs_node_"+str(self.node_id)+"/dump.txt", "a", newline="") as file:
                file.write("Vote Granted for Node "+str(cId)+" in term."+str(cTerm) +"\n")
            # Even if the one you vote for doesn't wins, you'll recieve heartbeat so no need to handle response 
            # response = self.global_zmq_socket.recv().decode()
            # # Handle response
        else:
            # Reply no vote
            time_left_in_leader_lease = self.lease_timer.remaining()
            message = "VoteResponse " + str(self.node_id) + " " + str(self.current_term) + " " + str(False) + " " + str(time_left_in_leader_lease)
            candidate_socket_addr = self.connections[str(cId)]
            context = zmq.Context()
            candidate_socket = context.socket(zmq.PUSH)
            monitor = candidate_socket.get_monitor_socket()
            print("Monitor Created")
            t = threading.Thread(target=event_monitor, args=(monitor,self.node_id,cId))
            print("Thread Created")
            t.start()
            candidate_socket.connect(candidate_socket_addr)
            candidate_socket.send(message.encode())
            with open("logs_node_"+str(self.node_id)+"/dump.txt", "a", newline="") as file:
                file.write("Vote denied for Node "+str(cId)+" in term."+str(cTerm) +"\n")
            # response = self.global_zmq_socket.recv().decode()
            # # Handle response
        self.handle_timers()
    
    def handle_vote_response(self, voterId, term, granted, lease_timer_left_according_to_voter):
        """
        From Pseudocode 3/9
        """
        self.MAX_LEASE_TIMER_LEFT = max(self.MAX_LEASE_TIMER_LEFT, lease_timer_left_according_to_voter)
        if self.current_role == 'Candidate' and term == self.current_term and granted:
            self.votes_received.add(voterId)
            if len(self.votes_received) >= math.ceil((len(self.connections) + 1) / 2):
                self.current_role = "Leader"
                with open("logs_node_"+str(self.node_id)+"/dump.txt", "a", newline="") as file:
                    file.write("Node "+str(self.node_id)+" became the leader for term "+str(term)+"\n")
                print("Node "+str(self.node_id)+" became the leader for term "+str(term))
                self.current_leader = self.node_id
                # Cancel election timer
                self.cancel_timers()
                self.handle_timers()
                # Send AppendEntries to all other nodes
                # TODO: Check if this is correct

                with open("logs_node_"+str(self.node_id)+"/logs.txt", "a", newline="") as file:
                    file.write("No-OP "+str(self.current_term) +"\n")
                print("No-OP "+str(self.current_term) )
                self.log.append({"term": self.current_term, "message": "No-OP"})
                # when it will be restarted it will reload logs

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
            with open("logs_node_"+str(self.node_id)+"/dump.txt", "a", newline="") as file:
                file.write("Leader Node "+str(self.node_id)+" received an entry request "+message+"\n")
            print("Leader Node "+str(self.node_id)+" received an entry request "+message+"\n")
            self.acked_length[self.node_id] = len(self.log)
            self.COUNT_OF_SUCCESSFUL_LEASE_RENEWALS = 0
            for follower, _ in self.connections.items():
                self.replicate_log(self.node_id, follower)
        else:
            # Forward to Leader
            context = zmq.Context()
            socket = context.socket(zmq.PUSH)
            socket.connect(self.connections[self.current_leader])
            monitor = socket.get_monitor_socket()
            t = threading.Thread(target=event_monitor, args=(monitor,1,0))
            t.start()
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
            self.COUNT_OF_SUCCESSFUL_LEASE_RENEWALS = 0
            # self.cancel_timers()
            # self.handle_timers()
            for follower, _ in self.connections.items():
                self.replicate_log(self.node_id, follower)

    def replicate_log(self, leader_id, follower_id):
        """
        From Pseudocode 5/9
        """
        # Cancelling and restarting the timers otherwise the leader keeps getting timed out
        print("Replicating log from Leader "+str(leader_id)+" to Follower "+str(follower_id))
        prefix_len = self.sent_length[follower_id]
        # [1,2,3,4,5]
        suffix = self.log[prefix_len:]
        prefix_term = 0
        if prefix_len > 0:
            prefix_term = self.log[prefix_len - 1]["term"]
        lease_timer_left = self.lease_timer.remaining()
        message = "LogRequest " + str(leader_id) + " " + str(self.current_term) + " " + str(prefix_len) + " " + str(prefix_term) + " " + str(self.commit_length) + " " + str(suffix) + " " + str(lease_timer_left)
        context = zmq.Context()
        socket = context.socket(zmq.PUSH)
        monitor = socket.get_monitor_socket()
        t = threading.Thread(target=event_monitor, args=(monitor,self.node_id,follower_id))
        t.start()
        socket.connect(self.connections[follower_id])
        socket.send(message.encode())
        print("Replicated log from Leader "+str(leader_id)+" to Follower "+str(follower_id))

    def handle_log_request(self, leader_id, term, prefix_len, prefix_term, leader_commit, suffix, lease_timer_left_according_to_leader):
        """
        From Pseudocode 6/9
        """
        if self.current_role != "Leader":
            self.cancel_timers()
            self.handle_timers()
        self.MAX_LEASE_TIMER_LEFT = max(self.MAX_LEASE_TIMER_LEFT, lease_timer_left_according_to_leader)
        if term > self.current_term:
            self.current_term = term
            self.voted_for = None
            self.cancel_timers()
            self.handle_timers()
        if term == self.current_term:
            self.current_role = "Follower"
            self.current_leader = leader_id
        print(self.log, prefix_len)
        logOk = len(self.log) >= prefix_len and (prefix_len == 0 or self.log[prefix_len-1]["term"] == prefix_term)
        if term == self.current_term and logOk:
            self.append_entries(prefix_len, leader_commit, suffix)
            ack = prefix_len + len(suffix)
            log_response_message = "LogResponse " + str(self.node_id) + " " + str(self.current_term) + " " + str(ack) + " " + str(True)
        else:
            log_response_message = "LogResponse " + str(self.node_id) + " " + str(self.current_term) + " " + str(prefix_len) + " " + str(False)
        candidate_socket_addr = self.connections[str(leader_id)]
        context = zmq.Context()
        candidate_socket = context.socket(zmq.PUSH)
        monitor = candidate_socket.get_monitor_socket()
        print("Monitor Created")
        t = threading.Thread(target=event_monitor, args=(monitor,self.node_id,leader_id))
        print("Thread Created")
        t.start()
        candidate_socket.connect(candidate_socket_addr)
        candidate_socket.send(log_response_message.encode())


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
        follower_id = str(follower_id)
        if success:
            self.COUNT_OF_SUCCESSFUL_LEASE_RENEWALS += 1
            if self.COUNT_OF_SUCCESSFUL_LEASE_RENEWALS >= math.ceil((len(self.connections) + 1) / 2):
                self.cancel_timers()
                self.handle_timers()
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
        return sum(1 for ack in self.acked_length if int(ack) >= length)
    

    def commit_log_entries(self):
        """
        From Pseudocode 9/9
        """
        min_acks = math.ceil((len(self.connections) + 1) / 2)
        ready = {i for i in range(len(self.log)) if self.acks(i) >= min_acks}
        print(self.acked_length, self.sent_length, self.log, self.commit_length, ready)
        max_ready_index_offset_handled = max(ready) + 1
        if len(ready) != 0 and max_ready_index_offset_handled + 1 > self.commit_length and self.log[max_ready_index_offset_handled - 1]["term"] == self.current_term:
            for i in range(self.commit_length, max_ready_index_offset_handled):
                last_message = self.log[i]["message"]
                # TODO why do we need to see SET - Update NVM
                if last_message.startswith("SET"):
                    _, key, value = last_message.split(" ")
                    self.data_truths[key] = value
                    with open("logs_node_"+str(self.node_id)+"/dump.txt", "a", newline="") as file:
                        file.write("Leader Node "+str(self.node_id)+" committed the entry "+last_message+" to the state machine \n")
                    print("Leader Node "+str(self.node_id)+" committed the entry "+last_message+" to the state machine ")
                
                # deliver log[i].message to application
                # self.broadcast_messages(self.log[i]["message"])

                # On the next LogRequest message that the leader sends to followers, the new value of 
                # commitLength will be included, causing the followers to commit and deliver the same log entries.



            self.commit_length = max_ready_index_offset_handled
            if os.path.isfile("logs_node_"+str(self.node_id)+"/metadata.txt"):
                os.remove("logs_node_"+str(self.node_id)+"/metadata.txt")
            with open("logs_node_"+str(self.node_id)+"/metadata.txt", "w") as file:
                file.write("Commit length "+str(self.commit_length)+" Term "+str(self.current_term)+" Node ID "+str(self.voted_for))
        

if __name__=='__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--nodeId", type=int)
    nodeId = argparser.parse_args().nodeId
    print("Starting Node with ID " + str(nodeId))
    node = RaftNode(nodeId)
    try:
        node.main()
        # context = zmq.Context()
        # socket = context.socket(zmq.PUSH)
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