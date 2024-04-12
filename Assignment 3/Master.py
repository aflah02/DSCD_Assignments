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

    def getNewCentroids(self):
        converged = True
        for port in self.reducer_ports:
            channel = grpc.insecure_channel(self.ip+":"+str(port))
            stub = map_reduce_pb2_grpc.ReducerServiceStub(channel)
            request = map_reduce_pb2.CentroidRequest(portNo=str(self.portNo))
            response = stub.SendNewCentroids(request)
            key_values = response.key_value
            for pair in key_values:
                if pair.value != self.centroids[pair.key]:
                    converged = False
                self.centroids[pair.key] = pair.value
        # print(self.centroids)
        centroids = open(f"./centroids.txt", "w")
        dump = open("./dump.txt", "a")
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

    def SendMapperData(self):
        for mapper in self.mapper_ports:
            channel = grpc.insecure_channel(self.ip+":"+str(mapper))
            stub = map_reduce_pb2_grpc.MapperServiceStub(channel)
            indices = self.indices_per_mapper[self.mapper_port_id[mapper]]
            request = map_reduce_pb2.MapDataRequest(input_split=indices, centroids=self.centroids, input_path=self.data_path)
            try :
                response = stub.GetMapperData(request)
                print(f"Status of Data sent to Mapper{response.mapper_id}: {response.status}")
            except:
                print(f"Status of Data sent to Mapper{self.mapper_port_id[mapper]}: FAILURE")

    def StartMapping(self):
        for mapper in self.mapper_ports:
            channel = grpc.insecure_channel(self.ip+":"+str(mapper))
            stub = map_reduce_pb2_grpc.MapperServiceStub(channel)
            request = map_reduce_pb2.Empty()
            try:
                response = stub.Mapping(request)
                print(f"Status of Mapping of Mapper{response.mapper_id}: {response.status}")
            except:
                print(f"Status of Mapping of Mapper{self.mapper_port_id[mapper]}: FAILURE")

    def StartPartitioning(self):
        for mapper in self.mapper_ports:
            channel = grpc.insecure_channel(self.ip+":"+str(mapper))
            stub = map_reduce_pb2_grpc.MapperServiceStub(channel)
            request = map_reduce_pb2.Empty()
            try:
                response = stub.Partitioning(request)
                print(f"Status of Partitioning of Mapper{response.mapper_id}: {response.status}")
            except:
                print(f"Status of Partitioning of Mapper{self.mapper_port_id[mapper]}: FAILURE")

    def StartReducers(self):
        for reducer in self.reducer_ports:
            channel = grpc.insecure_channel(self.ip+":"+str(reducer))
            stub = map_reduce_pb2_grpc.ReducerServiceStub(channel)
            request = map_reduce_pb2.Empty()
            try:
                response = stub.GetMapperData(request)
                print(f"Status of Data Retrieval from Mappers by Reducer{response.reducer_id}: {response.status}")
            except:
                print(f"Status of Data Retrieval from Mappers by Reducer{self.reducer_port_id[reducer]}: FAILURE")


    def StartShuffleSort(self):
        for reducer in self.reducer_ports:
            channel = grpc.insecure_channel(self.ip+":"+str(reducer))
            stub = map_reduce_pb2_grpc.ReducerServiceStub(channel)
            request = map_reduce_pb2.Empty()
            try:
                response = stub.ShuffleSorting(request)
                print(f"Status of Shuffle Sort of Reducer{response.reducer_id}: {response.status}")
            except:
                print(f"Status of Shuffle Sort of Reducer{self.reducer_port_id[reducer]}: FAILURE")


    def StartReducing(self):
        for reducer in self.reducer_ports:
            channel = grpc.insecure_channel(self.ip+":"+str(reducer))
            stub = map_reduce_pb2_grpc.ReducerServiceStub(channel)
            request = map_reduce_pb2.Empty()
            try:
                response = stub.Reducing(request)
                print(f"Status of Reduce of Reducer{response.reducer_id}: {response.status}")
            except:
                print(f"Status of Reduce of Reducer{self.reducer_port_id[reducer]}: FAILURE")


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
    for iteration in range(master.max_iterations):
        print("\nIteration Number:", iteration+1)
        dump = open("./dump.txt", "a")
        dump.write(f"Iteration {iteration+1}\n")
        dump.close()
        print("\nCentroids for this Iteration:")
        print(master.centroids)
        print("\nSending Data to Mappers...")
        master.SendMapperData()
        print("\nStart Mapping...")
        master.StartMapping()
        print("\nStart Partitioning...")
        master.StartPartitioning()

        print("\nStart Reducers to Get Data from Mappers...")
        master.StartReducers()
        print("\nStart Shuffle Sorting...")
        master.StartShuffleSort()
        print("\nStart Reducing...")
        master.StartReducing()
        print("\nGetting New Centroids...")
        converged = master.getNewCentroids()
        print()
        if converged:
            print("Converged before Maximum Iterations")
            break
    print("KMeans Finished.")
    
    server.wait_for_termination()

