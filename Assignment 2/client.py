import random
import zmq
import argparse
import socket as s
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

def event_monitor(monitor: zmq.Socket,leader_id,leaderdown) -> None:
    
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
    return leaderdown


def tcp_ping(address):
    # print(address.split(":"))
    _,host, port = address.split(":")
    host = host.replace("//", "")
    # print(f"Attempting to connect to {host}:{port}")
    port = int(port)
    # host = 'localhost'
    # port = 5558
    sock = s.socket(s.AF_INET, s.SOCK_STREAM)
    try:
        # Create a TCP socket

        sock.settimeout(5)  # Timeout for the connection attempt

        # Connect to the server
        sock.connect((host, port))
        print(f"Successfully connected to {host}:{port}")
        sock.close()
        return False

    except s.error as e:
        print(f"Failed to connect to {host}:{port} - {e}")
        sock.close()
        return True

    # finally:
    #     # Close the socket
    

    # finally:
    #     # Close the socket
 


with open('connections.json') as f:
    connections = json.load(f)

self_ip = "tcp://*:5562"
self_send_ip = "tcp://localhost:5562"
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
            checkPrevQuery = False
        if not leaderknown or leader_id==None:
            leader_id = random.choice(list(connections.keys()))
            print("Sampled node : ", leader_id)
        query_parts = query.split()
        # print("Query parts: ", query_parts)
        if query_parts[0].lower() == "set":
            if len(query_parts) != 3:
                print("Invalid query")
                checkPrevQuery = True
                continue
            queryToSend = query_parts[0].upper() + " " + query_parts[1] + " " + query_parts[2]+ " "+ self_send_ip

            leaderdown = False
            leaderdown = tcp_ping(connections[leader_id])
            if  leaderdown:
                print("Node is down")
                leaderknown = False
                continue
            # monitor = socket.get_monitor_socket()
            socket = zmq.Context().socket(zmq.PUSH)
            # print("Monitor Created")
            # t = threading.Thread(target=event_monitor, args=(monitor,leader_id,leaderdown))
            # print("Thread Created")
            # t.start()
            socket.connect(connections[leader_id])
            socket.send(queryToSend.encode())
            # close the socket
            socket.close()
            # time.sleep(1)
            # leaderdown = t.join()


            message = global_socket.recv().decode()
            print("Received reply: ", message)
            reply_parts = message.split()
            if str(reply_parts[0]) == "1":
                print("Key set successfully")
                leaderknown = True
                checkPrevQuery = True
            else:
                print("Leader is node "+str(reply_parts[1]))
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
            leaderdown = tcp_ping(connections[leader_id])
            if  leaderdown:
                print("Node is down")
                leaderknown = False
                continue
            # print("ZMQ Query to send: ", queryToSend)
            socket = zmq.Context().socket(zmq.PUSH)
            # print("Query to send: ", queryToSend)
            # monitor = socket.get_monitor_socket()
            # print("Monitor Created")
            # t = threading.Thread(target=event_monitor, args=(monitor,leader_id,leaderdown))
            # print("Thread Created")
            # t.start()
            socket.connect(connections[leader_id])
            # print("Connected to leader")
            socket.send(queryToSend.encode())
            # close the socket
            socket.close()
            # time.sleep(1)
            # leaderdown = t.join()
            message = global_socket.recv().decode()
            # print("Received reply: ", message)
            reply_parts = message.split()
            if str(reply_parts[0]) == "1":
                val = reply_parts[1]
                leaderknown = True
                checkPrevQuery = True
                print("Value of get "+str(query_parts)+" "+ str(val))
            elif str(reply_parts[0]) == "2":
                print("Key not found")
                leaderknown = True
                checkPrevQuery = True
            elif str(reply_parts[0]) == "0":
                print("Leader is node "+str(reply_parts[1]))
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
# test = "tcp://localhost:5556"
# tcp_ping(test)
