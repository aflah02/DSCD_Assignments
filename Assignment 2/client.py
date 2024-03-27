import random
import zmq
import argparse
import json

with open('connections.json') as f:
    connections = json.load(f)

self_ip = "tcp://*:5558"

context = zmq.Context()
socket = context.socket(zmq.REQ)
checkPrevQuery = True
leaderknown = False
leader_id = None
# used as a check to see if the previous query was a completed
while True:
    try:
        # write a zmq client which sends a message
        if checkPrevQuery:
            query = input("Enter type of query: Get or Set")
        if not leaderknown or leader_id==None:
            leader_id = random.choice(connections.keys())
        query_parts = query.split()
        if query_parts[0].lower() == "set":
            if len(query_parts) != 3:
                print("Invalid query")
                continue
            query = query_parts[0].upper() + " " + query_parts[1] + " " + query_parts[2]+ " "+ self_ip
            socket.connect(connections[leader_id])
            socket.send(query.encode())
            message = socket.recv().decode()
            print("Received reply: ", message)
            reply_parts = message.split()
        elif query_parts[0].lower() == "get":
            if len(query_parts) != 2:
                print("Invalid query")
                continue
            query = query_parts[0].upper() + " " + query_parts[1] + " "+ self_ip
            socket.connect(connections[leader_id])
            socket.send(query.encode())
            message = socket.recv().decode()
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
                checkPrevQuery = False
            elif str(reply_parts[0]) == "0":
                leaderknown = True
                checkPrevQuery = False
                leader_id = str(reply_parts[1])
        else:
            print("Invalid query")
            continue
        socket.connect(connections[leader_id])
        socket.send(query.encode())
        message = socket.recv().decode()
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
            checkPrevQuery = False
        elif str(reply_parts[0]) == "0":
            leaderknown = True
            checkPrevQuery = False
            leader_id = str(reply_parts[1])
    except:
        break

