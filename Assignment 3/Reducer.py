import grpc
from concurrent import futures
import map_reduce_pb2
import map_reduce_pb2_grpc
import argparse
import socket
import os
import ast

class Reducer(map_reduce_pb2_grpc.ReducerServiceServicer):
    def __init__(self, reducerId, portNo, mappers):
        self.reducerId = reducerId
        self.portNo = portNo
        self.mappers = mappers
        self.ip = socket.gethostbyname(socket.gethostname())
        self.key_value = {}
        if os.path.exists(f"./Reducers/R{self.reducerId}.txt"):
            os.remove(f"./Reducers/R{self.reducerId}.txt")
        reducer = open(f"./Reducers/R{self.reducerId}.txt", "a")
        reducer.close()

    def SendPartition(self, request, context):
        pass

    def GetDataFromMappers(self):
        for mapper in self.mappers:
            channel = grpc.insecure_channel(self.ip+":"+str(mapper))
            stub = map_reduce_pb2_grpc.MapperServiceStub(channel)
            request = map_reduce_pb2.KeyValueRequest(ip="[::]:"+str(self.portNo), reducerId=self.reducerId)
            response = stub.SendKeyValuePair(request)
            self.key_value_pairs = response.key_value_pairs
            # print(self.key_value_pairs)
            self.ShuffleSort()

    def ShuffleSort(self):
        self.key_value_pairs = sorted(self.key_value_pairs , key=lambda k: k.key)
        # print(self.key_value_pairs)

        for key_value in self.key_value_pairs:
            if key_value.key in self.key_value.keys():
                self.key_value[key_value.key].append(key_value.value)
            else:
                self.key_value[key_value.key] = []
        print(self.key_value)

    def Reduce(self):
        pass

if __name__=='__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--reducerId", type=int)
    argparser.add_argument("--portNo", type=int)
    argparser.add_argument("--mappers", type=str)
    
    reducerId = argparser.parse_args().reducerId
    portNo = argparser.parse_args().portNo
    
    mappers = argparser.parse_args().mappers.split(" ")
    print(mappers)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    reducer = Reducer(reducerId, portNo, mappers)
    map_reduce_pb2_grpc.add_ReducerServiceServicer_to_server(reducer, server)

    server.add_insecure_port("[::]:"+str(portNo))
    server.start()
    print(len(mappers))
    reducer.GetDataFromMappers()
    server.wait_for_termination()