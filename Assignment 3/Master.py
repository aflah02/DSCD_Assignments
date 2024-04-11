import grpc
from concurrent import futures
import map_reduce_pb2
import map_reduce_pb2_grpc
import subprocess
import argparse
import random

class Master(map_reduce_pb2_grpc.MasterServiceServicer):
    def __init__(self, mappers, reducers, centroids, max_iterations, data_path):
        self.num_mappers = mappers
        self.num_reducers = reducers
        self.num_centroids = centroids
        self.max_iterations = max_iterations
        self.indices_per_mapper = {}
        self.centroids = []
        self.data_path = data_path

    def invoke_mappers(self):
        for i in self.indices_per_mapper.keys():
            subprocess.Popen(["python3", "Mapper.py", "--portNo", f"{i}", "--numReducers", f'{self.num_reducers}'])

    def input_split(self):
        file = open(self.data_path, "r")
        data_points = file.read().split("\n")
        data_points = [map_reduce_pb2.Point(x=float(point.split(",")[0]), y=float(point.split(",")[1])) for point in data_points]
        # print(data_points)
        file.close()
        indices_per_mapper = {}
        for i in range(self.num_mappers):
            indices_per_mapper[50052+i] = []
        for i in range(len(data_points)):
            index = i%self.num_mappers
            indices_per_mapper.get(50052+index).append(i)

        self.indices_per_mapper = indices_per_mapper
        self.centroids = random.sample(data_points, self.num_centroids)
    
    def SendMapperData(self, request, context):
        data_indices = self.indices_per_mapper[request.mapper_id]
        centroids = self.centroids
        return map_reduce_pb2.MapDataResponse(input_split=data_indices, centroids=centroids, input_path=self.data_path)

    def InvokeReducers(self, request, context):
        pass

if __name__=='__main__':
    print("Starting KMeans using Map-Reduce...")
    num_mappers = int(input("Enter number of Mappers: "))
    num_reducers = int(input("Enter number of Reducers: "))
    num_centroids = int(input("Enter number of Centroids: "))
    max_iters = int(input("Enter number of Iterations: "))

    master = Master(num_mappers, num_reducers, num_centroids, max_iters, "./Input/points.txt")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
    # master.input_split("./Input/points.txt")
    map_reduce_pb2_grpc.add_MasterServiceServicer_to_server(master, server)
    print('Starting server. Listening on port 50051.')
    server.add_insecure_port('[::]:50051')
    server.start()
    master.input_split()
    master.invoke_mappers()
    server.wait_for_termination()

