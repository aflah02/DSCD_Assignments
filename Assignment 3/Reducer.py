import grpc
from concurrent import futures
import map_reduce_pb2
import map_reduce_pb2_grpc
import argparse
import socket
import os
import shutil

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
        self.key_value_pairs = []
        self.reducer_output = {}

    def SendNewCentroids(self, request, context):
        new_centroids = []
        for key in self.reducer_output.keys():
            new_centroids.append(map_reduce_pb2.KeyValue(key=key, value=self.reducer_output[key]))
        return map_reduce_pb2.CentroidResponse(key_value=new_centroids)

    def GetMapperData(self, request, context):
        self.GetDataFromMappers()
        return map_reduce_pb2.ReduceDataResponse(reducer_id=self.reducerId, status="SUCCESS")

    def ShuffleSorting(self, request, context):
        self.ShuffleSort()
        return map_reduce_pb2.ReduceDataResponse(reducer_id=self.reducerId, status="SUCCESS")

    def Reducing(self, request, context):
        self.Reduce(self.key_value)
        return map_reduce_pb2.ReduceDataResponse(reducer_id=self.reducerId, status="SUCCESS")
    
    def GetDataFromMappers(self):
        for mapper in self.mappers:
            channel = grpc.insecure_channel(self.ip+":"+str(mapper))
            stub = map_reduce_pb2_grpc.MapperServiceStub(channel)
            request = map_reduce_pb2.KeyValueRequest(ip="[::]:"+str(self.portNo), reducerId=self.reducerId)
            response = stub.SendKeyValuePair(request)
            self.key_value_pairs.extend(response.key_value_pairs)
            # print(self.key_value_pairs)
        # self.ShuffleSort()

    def ShuffleSort(self):
        # self.key_value_pairs = sorted(self.key_value_pairs , key=lambda k: k.key)
        # print(self.key_value_pairs)

        for key_value in self.key_value_pairs:
            # print("Reducer ID:", self.reducerId)
            # print(key_value.key)
            if key_value.key in self.key_value.keys():
                self.key_value[key_value.key].append(key_value.value)
            else:
                self.key_value[key_value.key] = []
                self.key_value[key_value.key].append(key_value.value)

        # print(self.key_value)
        self.key_value = dict(sorted(self.key_value.items()))
        # print("Reducer ID:", self.reducerId)
        # print(self.key_value)
        # self.Reduce(self.key_value)


    def Reduce(self, key_value):
        reducer = open(f"./Reducers/R{self.reducerId}.txt", "a")
        for key in key_value.keys():
            mean_x = 0
            mean_y = 0
            for value in key_value[key]:
                mean_x += value.x
                mean_y += value.y
            mean_x /= len(key_value[key])
            mean_y /= len(key_value[key])
            reducer.write(f"({key}, ({mean_x}, {mean_y}))\n")
            self.reducer_output[key] = map_reduce_pb2.Point(x=mean_x, y=mean_y)
        # print(self.reducer_output)
        reducer.close()

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
    # print(len(mappers))
    # reducer.GetDataFromMappers()
    server.wait_for_termination(timeout=100000000000)