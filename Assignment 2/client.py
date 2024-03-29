import random
import zmq
import argparse
import json
from typing import Any, Dict
from zmq.utils.monitor import recv_monitor_message
import threading
import time
leaderknown = False
leaderdown = False

EVENT_MAP = {}
# print("Event names:")
for name in dir(zmq):
    if name.startswith('EVENT_'):
        value = getattr(zmq, name)
        # print("%21s : %4i" % (name, value))
        EVENT_MAP[value] = name

def event_monitor(monitor: zmq.Socket,leader_id) -> None:
    global leaderdown
    while monitor.poll():
        evt: Dict[str, Any] = {}
        mon_evt = recv_monitor_message(monitor)
        evt.update(mon_evt)
        evt['description'] = EVENT_MAP[evt['event']]
        # print(f"Event: {evt}") 
        if evt['event'] == zmq.EVENT_CONNECT_RETRIED:
            # print("Connection to Node "+str(id)+" failed. Retrying...")
            print("Connection to Node "+str(leader_id)+" failed.")
            leaderdown = True
            break
    monitor.close()
    print()



with open('connections.json') as f:
    connections = json.load(f)

self_ip = "tcp://*:5561"
self_send_ip = "tcp://localhost:5561"
context = zmq.Context()
socket = context.socket(zmq.PUSH)

global_socket = context.socket(zmq.PULL)
global_socket.bind(self_ip)

checkPrevQuery = True

leader_id = None
# used as a check to see if the previous query was a completed
while True:
    try:
        if leader_id == "None":
            leaderknown = False
        # write a zmq client which sends a message
        if checkPrevQuery:
            query = input("Enter type of query: Get or Set: ")
            print("Query: ", query)
        if not leaderknown or leader_id==None:
            leader_id = random.choice(list(connections.keys()))
        query_parts = query.split()
        print("Query parts: ", query_parts)
        if query_parts[0].lower() == "set":
            if len(query_parts) != 3:
                print("Invalid query")
                checkPrevQuery = True
                continue
            queryToSend = query_parts[0].upper() + " " + query_parts[1] + " " + query_parts[2]+ " "+ self_send_ip
            socket = zmq.Context().socket(zmq.PUSH)
            leaderdown = False
            monitor = socket.get_monitor_socket()
            # print("Monitor Created")
            t = threading.Thread(target=event_monitor, args=(monitor,leader_id))
            # print("Thread Created")
            t.start()
            socket.connect(connections[leader_id])
            socket.send(queryToSend.encode())
            # close the socket
            socket.close()
            time.sleep(1)
            if not leaderdown:
                message = global_socket.recv().decode()
                print("Received reply: ", message)
                reply_parts = message.split()
                if str(reply_parts[0]) == "1":
                    print("Key set successfully")
                    leaderknown = True
                    checkPrevQuery = True
                else:
                    leaderknown = True
                    checkPrevQuery = False
                    leader_id = str(reply_parts[1])
        elif query_parts[0].lower() == "get":
            if len(query_parts) != 2:
                print("Invalid query")
                checkPrevQuery = True
                continue
            queryToSend = query_parts[0].upper() + " " + query_parts[1] + " "+ self_send_ip
            leaderdown = False
            socket = zmq.Context().socket(zmq.PUSH)
            monitor = socket.get_monitor_socket()
            # print("Monitor Created")
            t = threading.Thread(target=event_monitor, args=(monitor,leader_id))
            # print("Thread Created")
            t.start()
            socket.connect(connections[leader_id])
            socket.send(queryToSend.encode())
            # close the socket
            socket.close()
            time.sleep(1)
            if not leaderdown:
                print("Sent query: ", query)
                message = global_socket.recv().decode()
                print("Received reply: ", message)
                reply_parts = message.split()
                if str(reply_parts[0]) == "1":
                    val = reply_parts[1]
                    leaderknown = True
                    checkPrevQuery = True
                    print("Value of get "+str(query_parts)+ str(val))
                elif str(reply_parts[0]) == "2":
                    print("Key not found")
                    leaderknown = True
                    checkPrevQuery = True
                elif str(reply_parts[0]) == "0":
                    leaderknown = True
                    checkPrevQuery = False
                    leader_id = str(reply_parts[1])
                    if leader_id == "None":
                        leaderknown = False
        else:
            print("Invalid query")
            continue
    except Exception as e:
        print("Exception: ", e)
        global_socket = context.socket(zmq.PULL)
        global_socket.bind(self_ip)

