import grpc
from concurrent import futures
import map_reduce_pb2
import map_reduce_pb2_grpc
import subprocess

class Master(map_reduce_pb2_grpc.MasterServiceServicer):
    def __init__(self, mappers, reducers, centroids, max_iterations):
        self.num_mappers = mappers
        self.num_reducers = reducers
        self.num_centroids = centroids
        self.max_iterations = max_iterations
        self.indices_per_mapper = {}

    def input_split(self, file_path):
        file = open(file_path, "r")
        data_points = file.read().split("\n")
        data_points = [tuple([float(x) for x in point.split(",")]) for point in data_points]
        file.close()
        indices_per_mapper = {}
        for i in range(self.num_mappers):
            indices_per_mapper[i] = []
        for i in range(len(data_points)):
            index = i%self.num_mappers
            indices_per_mapper.get(index).append(i)
        # print(indices_per_mapper)
        self.indices_per_mapper = indices_per_mapper
    
    def SendMapperData(self, request, context):
        pass

    def InvokeReducers(self, request, context):
        pass

if __name__=='__main__':
    print("Starting KMeans using Map-Reduce...")
    num_mappers = int(input("Enter number of Mappers: "))
    num_reducers = int(input("Enter number of Reducers: "))
    num_centroids = int(input("Enter number of Centroids: "))
    max_iters = int(input("Enter number of Iterations: "))

    master = Master(num_mappers, num_reducers, num_centroids, max_iters)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
    master.input_split("./Input/points.txt")
    map_reduce_pb2_grpc.add_MasterServiceServicer_to_server(Master(num_mappers, num_reducers, num_centroids, max_iters), server)
    print('Starting server. Listening on port 50051.')
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

