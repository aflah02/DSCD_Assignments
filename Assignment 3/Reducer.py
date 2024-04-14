import grpc
from concurrent import futures
import map_reduce_pb2
import map_reduce_pb2_grpc
import argparse
import socket
import os
from random import choices
import time

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
        flag = choices([0,1], [0.2, 0.8])[0]
        time.sleep(5)
        if flag == 1:
            new_centroids = []
            for key in self.reducer_output.keys():
                new_centroids.append(map_reduce_pb2.KeyValue(key=key, value=self.reducer_output[key]))
            return map_reduce_pb2.CentroidResponse(key_value=new_centroids, status="SUCCESS")
        return map_reduce_pb2.CentroidResponse(status="FAILURE")

    def Heartbeat(self, request, context):
        return map_reduce_pb2.ReduceDataResponse(mapper_id=self.reducerId, status="SUCCESS")
    
    def GetMapperData(self, request, context):
        flag = choices([0,1], [0.2, 0.8])[0]
        time.sleep(5)
        if flag == 1:
            self.GetDataFromMappers()
            return map_reduce_pb2.ReduceDataResponse(reducer_id=self.reducerId, status="SUCCESS")
        return map_reduce_pb2.ReduceDataResponse(reducer_id=self.reducerId, status="FAILURE")
    
    def ShuffleSorting(self, request, context):
        flag = choices([0,1], [0.2, 0.8])[0]
        time.sleep(5)
        if flag == 1:
            self.ShuffleSort()
            return map_reduce_pb2.ReduceDataResponse(reducer_id=self.reducerId, status="SUCCESS")
        return map_reduce_pb2.ReduceDataResponse(reducer_id=self.reducerId, status="FAILURE")
    
    def Reducing(self, request, context):
        flag = choices([0,1], [0.2, 0.8])[0]
        time.sleep(5)
        if flag == 1:
            self.Reduce(self.key_value)
            return map_reduce_pb2.ReduceDataResponse(reducer_id=self.reducerId, status="SUCCESS")
        return map_reduce_pb2.ReduceDataResponse(reducer_id=self.reducerId, status="FAILURE")

    def GetDataFromMappers(self):
        mapper_port_id = 0
        while mapper_port_id < len(self.mappers):
            channel = grpc.insecure_channel(self.ip+":"+str(self.mappers[mapper_port_id]))
            stub = map_reduce_pb2_grpc.MapperServiceStub(channel)
            request = map_reduce_pb2.KeyValueRequest(ip="[::]:"+str(self.portNo), reducerId=self.reducerId)
            try:
                dump_reducer = open(f"./Reducers/dump_reducer_R{self.reducerId}.txt", "a")
                dump_reducer.write(f"\nSending Request to M{mapper_port_id}\n")
                dump_reducer.close()
                response = stub.SendKeyValuePair(request)
                if response.status == "SUCCESS":
                    print(f"Status of Data from Mapper{mapper_port_id}: {response.status}")
                    self.key_value_pairs.extend(response.key_value_pairs)
                    mapper_port_id += 1
                else:
                    print(f"Status of Data from Mapper{mapper_port_id}: {response.status}")
            except Exception as e:
                print(e)
                print(f"Status of Data from Mapper{mapper_port_id}: FAILURE")

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
        dump_reducer = open(f"./Reducers/dump_reducer_R{reducerId}.txt", "a")
        dump_reducer.write(f"\nReduce Results for Reducer {self.reducerId}\n")
        for key in key_value.keys():
            mean_x = 0
            mean_y = 0
            for value in key_value[key]:
                mean_x += value.x
                mean_y += value.y
            mean_x /= len(key_value[key])
            mean_y /= len(key_value[key])
            reducer.write(f"({key}, ({mean_x}, {mean_y}))\n")
            dump_reducer.write(f"({key}, ({mean_x}, {mean_y}))\n")
            self.reducer_output[key] = map_reduce_pb2.Point(x=mean_x, y=mean_y)
        # print(self.reducer_output)
        reducer.close()
        dump_reducer.close()

if __name__=='__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--reducerId", type=int)
    argparser.add_argument("--portNo", type=int)
    argparser.add_argument("--mappers", type=str)
    
    reducerId = argparser.parse_args().reducerId
    portNo = argparser.parse_args().portNo
    
    mappers = argparser.parse_args().mappers.split(" ")
    # print(mappers)
    open(f"./Reducers/dump_reducer_R{reducerId}.txt", 'w').close()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    reducer = Reducer(reducerId, portNo, mappers)
    map_reduce_pb2_grpc.add_ReducerServiceServicer_to_server(reducer, server)

    server.add_insecure_port("[::]:"+str(portNo))
    server.start()
    # print(len(mappers))
    # reducer.GetDataFromMappers()
    server.wait_for_termination()