import random
import zmq
import argparse
import json

with open('connections.json') as f:
    connections = json.load(f)

self_ip = "tcp://*:5558"
self_send_ip = "tcp://localhost:5558"
context = zmq.Context()
socket = context.socket(zmq.REQ)

global_socket = context.socket(zmq.REP)
global_socket.bind(self_ip)

checkPrevQuery = True
leaderknown = False
leader_id = None
# used as a check to see if the previous query was a completed
while True:
    try:
        # write a zmq client which sends a message
        if checkPrevQuery:
            query = input("Enter type of query: Get or Set: ")
            print("Query: ", query)
        if not leaderknown or leader_id==None:
            print("In If")
            leader_id = random.choice(list(connections.keys()))
            print("Leader ID: ", leader_id)
        query_parts = query.split()
        print("Query parts: ", query_parts)
        if query_parts[0].lower() == "set":
            if len(query_parts) != 3:
                print("Invalid query")
                checkPrevQuery = True
                continue
            queryToSend = query_parts[0].upper() + " " + query_parts[1] + " " + query_parts[2]+ " "+ self_send_ip
            socket = zmq.Context().socket(zmq.REQ)
            socket.connect(connections[leader_id])
            socket.send(queryToSend.encode())
            # close the socket
            socket.close()

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
            print("In get")
            if len(query_parts) != 2:
                print("Invalid query")
                checkPrevQuery = True
                continue
            print("Reached Here in Get")
            print("Query parts: ", query_parts)
            queryToSend = query_parts[0].upper() + " " + query_parts[1] + " "+ self_send_ip
            socket = zmq.Context().socket(zmq.REQ)
            socket.connect(connections[leader_id])
            socket.send(queryToSend.encode())
            # close the socket
            socket.close()
            print("Sent query: ", query)
            message = global_socket.recv().decode()
            print("Received reply: ", message)
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
        else:
            print("Invalid query")
            continue
    except Exception as e:
        print("Exception: ", e)
        global_socket = context.socket(zmq.REP)
        global_socket.bind(self_ip)

