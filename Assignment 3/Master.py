import grpc
from concurrent import futures
import map_reduce_pb2
import map_reduce_pb2_grpc
import subprocess
import argparse
import random
import socket
import time
import os
import threading

class MyTimer:
    def __init__(self, interval, onEndCallback) -> None:
        self.interval = interval
        self.onEndCallback = onEndCallback

    def start(self, ):
        self.start_time = time.time()
        self._timer = threading.Timer(self.interval, self.onEndCallback if self.onEndCallback is not None else lambda: None)
        self._timer.start()

    def cancel(self):
        self._timer.cancel()
class Master(map_reduce_pb2_grpc.MasterServiceServicer):
    def __init__(self, mappers, reducers, centroids, max_iterations, portNo, data_path):
        self.num_mappers = mappers
        self.num_reducers = reducers
        self.num_centroids = centroids
        self.max_iterations = max_iterations
        self.indices_per_mapper = {}
        self.mapper_ports = []
        self.reducer_ports = []
        self.mapper_port_id = {}
        self.reducer_port_id = {}
        self.centroids = []
        self.data_path = data_path
        self.portNo = portNo
        self.ip = socket.gethostbyname(socket.gethostname())
        self.timer = None

        for i in range(self.num_mappers):
            self.mapper_ports.append(self.portNo+i+1)
        for i in range(self.num_reducers):
            self.reducer_ports.append(self.mapper_ports[-1]+i+1)
    def invoke_mappers(self):
        mapper_id = 0
        for i in self.mapper_ports:
            subprocess.Popen(["python3", "Mapper.py", "--mapperId", f"{mapper_id}", "--portNo", f"{i}", "--numReducers", f'{self.num_reducers}'])
            self.mapper_port_id[i] = mapper_id
            mapper_id += 1
        time.sleep(5)
        print("Mappers Started", self.mapper_ports)
    
    def invoke_reducers(self):
        reducer_id = 0
        # print(' '.join(str(x) for x in self.mapper_ports))
        for i in self.reducer_ports:
            subprocess.Popen(["python3", "Reducer.py", "--reducerId", f"{reducer_id}", "--portNo", f"{i}", "--mappers", f"{' '.join(str(x) for x in self.mapper_ports)}"])
            self.reducer_port_id[i] = reducer_id
            reducer_id += 1
        time.sleep(5)
        print("Reducers Started", self.reducer_ports)
    
    def startTimer(self):
        self.timer = MyTimer(1, self.periodic_heartbeat)
        self.timer.start()

    def periodic_heartbeat(self):
        for mapper in self.mapper_ports:
            channel = grpc.insecure_channel(self.ip+":"+str(mapper))
            stub = map_reduce_pb2_grpc.MapperServiceStub(channel)
            request = map_reduce_pb2.Empty()
            try :
                response = stub.Heartbeat(request)
                print(f"Heartbeat from Mapper{response.mapper_id}: {response.status}")
            except:
                print(f"Heartbeat from Mapper{self.mapper_port_id[mapper]}: FAILURE")

        for reducer in self.reducer_ports:
            channel = grpc.insecure_channel(self.ip+":"+str(reducer))
            stub = map_reduce_pb2_grpc.ReducerServiceStub(channel)
            request = map_reduce_pb2.Empty()
            try:
                response = stub.Heartbeat(request)
                print(f"Heartbeat from Reducer{response.reducer_id}: {response.status}")
            except:
                print(f"Heartbeat from Reducer{self.reducer_port_id[reducer]}: FAILURE")
        self.timer.cancel()
        self.startTimer()

    def getNewCentroids(self):
        converged = True
        reducer_port_id = 0
        while reducer_port_id < len(self.reducer_ports):
            channel = grpc.insecure_channel(self.ip+":"+str(self.reducer_ports[reducer_port_id]))
            stub = map_reduce_pb2_grpc.ReducerServiceStub(channel)
            request = map_reduce_pb2.CentroidRequest(portNo=str(self.portNo))
            try:
                response = stub.SendNewCentroids(request)
                if response.status == "SUCCESS":
                    print(f"Status of Centroids Received from Reducer{self.reducer_ports[reducer_port_id]}: {response.status}")
                    key_values = response.key_value
                    for pair in key_values:
                        if pair.value != self.centroids[pair.key]:
                            converged = False
                        self.centroids[pair.key] = pair.value
                    reducer_port_id += 1
                else:
                    print(f"Status of Centroids Received from Reducer{self.reducer_ports[reducer_port_id]}: {response.status}")
            except:
                    print(f"Status of Centroids Received from Reducer{self.reducer_ports[reducer_port_id]}: FAILURE")

        # print(self.centroids)
        centroids = open(f"./centroids.txt", "w")
        dump = open("./dump.txt", "a")
        dump.write("\nNew Centroids:\n")
        for centroid in self.centroids:
            centroids.write(f"{centroid.x}, {centroid.y}\n")
            dump.write(f"{centroid.x}, {centroid.y}\n")
        centroids.close()
        dump.close()
        return converged

    def input_split(self):
        file = open(self.data_path, "r")
        data_points = file.read().split("\n")
        data_points = [map_reduce_pb2.Point(x=float(point.split(",")[0]), y=float(point.split(",")[1])) for point in data_points]
        # print(data_points)
        file.close()
        indices_per_mapper = {}
        for i in range(self.num_mappers):
            indices_per_mapper[i] = []
        for i in range(len(data_points)):
            index = i%self.num_mappers
            indices_per_mapper.get(index).append(i)

        self.indices_per_mapper = indices_per_mapper
        self.centroids = random.sample(data_points, self.num_centroids)
    
    def SendMapperData(self, request, context):
        data_indices = self.indices_per_mapper[request.mapper_id]
        centroids = self.centroids
        return map_reduce_pb2.MapDataResponse(input_split=data_indices, centroids=centroids, input_path=self.data_path)

    def sendMapperData(self):
        mapper_port_id = 0
        while mapper_port_id < len(self.mapper_ports):
            channel = grpc.insecure_channel(self.ip+":"+str(self.mapper_ports[mapper_port_id]))
            stub = map_reduce_pb2_grpc.MapperServiceStub(channel)
            indices = self.indices_per_mapper[self.mapper_port_id[self.mapper_ports[mapper_port_id]]]
            request = map_reduce_pb2.MapDataRequest(input_split=indices, centroids=self.centroids, input_path=self.data_path)
            try :
                response = stub.GetMapperData(request)
                print(f"Status of Data sent to Mapper{response.mapper_id}: {response.status}")
                if response.status == "SUCCESS":
                    mapper_port_id += 1
                else:
                    print(f"Mapper{response.mapper_id} FAILED. Retrying...")
            except:
                print(f"Status of Data sent to Mapper{self.mapper_port_id[self.mapper_ports[mapper_port_id]]}: FAILURE")

    def startMapping(self):
        mapper_port_id = 0
        while mapper_port_id < len(self.mapper_ports):
            channel = grpc.insecure_channel(self.ip+":"+str(self.mapper_ports[mapper_port_id]))
            stub = map_reduce_pb2_grpc.MapperServiceStub(channel)
            request = map_reduce_pb2.Empty()
            try:
                response = stub.Mapping(request)
                print(f"Status of Mapping of Mapper{response.mapper_id}: {response.status}")
                if response.status == "SUCCESS":
                    mapper_port_id += 1
                else:
                    print(f"Mapper{response.mapper_id} FAILED. Retrying...")
            except:
                print(f"Status of Mapping of Mapper{self.mapper_port_id[self.mapper_ports[mapper_port_id]]}: FAILURE")

    def startPartitioning(self):
        mapper_port_id = 0
        while mapper_port_id < len(self.mapper_ports):
            channel = grpc.insecure_channel(self.ip+":"+str(self.mapper_ports[mapper_port_id]))
            stub = map_reduce_pb2_grpc.MapperServiceStub(channel)
            request = map_reduce_pb2.Empty()
            try:
                response = stub.Partitioning(request)
                print(f"Status of Partitioning of Mapper{response.mapper_id}: {response.status}")
                if response.status == "SUCCESS":
                    mapper_port_id += 1
                else:
                    print(f"Mapper{response.mapper_id} FAILED. Retrying...")
            except:
                print(f"Status of Partitioning of Mapper{self.mapper_port_id[self.mapper_ports[mapper_port_id]]}: FAILURE")

    def startReducers(self):
        reducer_port_id = 0
        while reducer_port_id < len(self.reducer_ports):
            channel = grpc.insecure_channel(self.ip+":"+str(self.reducer_ports[reducer_port_id]))
            stub = map_reduce_pb2_grpc.ReducerServiceStub(channel)
            request = map_reduce_pb2.Empty()
            try:
                response = stub.GetMapperData(request)
                print(f"Status of Data Retrieval from Mappers by Reducer{response.reducer_id}: {response.status}")
                if response.status == "SUCCESS":
                    reducer_port_id += 1
                else:
                    print(f"Reducer{response.reducer_id} FAILED. Retrying...")
            except:
                print(f"Status of Data Retrieval from Mappers by Reducer{self.reducer_port_id[self.reducer_ports[reducer_port_id]]}: FAILURE")


    def startShuffleSort(self):
        reducer_port_id = 0
        while reducer_port_id < len(self.reducer_ports):
            channel = grpc.insecure_channel(self.ip+":"+str(self.reducer_ports[reducer_port_id]))
            stub = map_reduce_pb2_grpc.ReducerServiceStub(channel)
            request = map_reduce_pb2.Empty()
            try:
                response = stub.ShuffleSorting(request)
                print(f"Status of Shuffle Sort of Reducer{response.reducer_id}: {response.status}")
                if response.status == "SUCCESS":
                    reducer_port_id += 1
                else:
                    print(f"Reducer{response.reducer_id} FAILED. Retrying...")
            except:
                print(f"Status of Shuffle Sort of Reducer{self.reducer_port_id[self.reducer_ports[reducer_port_id]]}: FAILURE")


    def startReducing(self):
        reducer_port_id = 0
        while reducer_port_id < len(self.reducer_ports):
            channel = grpc.insecure_channel(self.ip+":"+str(self.reducer_ports[reducer_port_id]))
            stub = map_reduce_pb2_grpc.ReducerServiceStub(channel)
            request = map_reduce_pb2.Empty()
            try:
                response = stub.Reducing(request)
                print(f"Status of Reduce of Reducer{response.reducer_id}: {response.status}")
                if response.status == "SUCCESS":
                    reducer_port_id += 1
                else:
                    print(f"Reducer{response.reducer_id} FAILED. Retrying...")
            except:
                print(f"Status of Reduce of Reducer{self.reducer_port_id[self.reducer_ports[reducer_port_id]]}: FAILURE")


if __name__=='__main__':
    print("Starting KMeans using Map-Reduce...")
    num_mappers = int(input("Enter number of Mappers: "))
    num_reducers = int(input("Enter number of Reducers: "))
    num_centroids = int(input("Enter number of Centroids: "))
    max_iters = int(input("Enter number of Iterations: "))

    open('./dump.txt', 'w').close()

    master = Master(num_mappers, num_reducers, num_centroids, max_iters, 50051, "./Input/points.txt")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
    # master.input_split("./Input/points.txt")
    map_reduce_pb2_grpc.add_MasterServiceServicer_to_server(master, server)
    print('Starting server. Listening on port 50051.')
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Splitting Input Data...")
    master.input_split()
    print("Invoking Mappers...")
    master.invoke_mappers()
    print("Invoking Reducers...")
    master.invoke_reducers()
    time.sleep(5)
    
    master.startTimer()
    for iteration in range(master.max_iterations):
        print("\nIteration Number:", iteration+1)
        dump = open("./dump.txt", "a")
        dump.write(f"\nIteration {iteration+1}\n")
        dump.close()
        print("\nCentroids for this Iteration:")
        print(master.centroids)
        print("\nSending Data to Mappers...")
        master.sendMapperData()
        print("\nStart Mapping...")
        master.startMapping()
        print("\nStart Partitioning...")
        master.startPartitioning()

        print("\nStart Reducers to Get Data from Mappers...")
        master.startReducers()
        print("\nStart Shuffle Sorting...")
        master.startShuffleSort()
        print("\nStart Reducing...")
        master.startReducing()
        print("\nGetting New Centroids...")
        converged = master.getNewCentroids()
        print()
        if converged:
            print("Converged before Maximum Iterations")
            break
    print("KMeans Finished.")
    master.timer.cancel()
    server.wait_for_termination()

