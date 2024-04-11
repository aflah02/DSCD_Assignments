import grpc
from concurrent import futures
import map_reduce_pb2
import map_reduce_pb2_grpc
import argparse
import socket
import math
import os
import shutil

class Mapper(map_reduce_pb2_grpc.MapperServiceServicer):
    def __init__(self, portNo, numReducers):
        self.indices = None
        self.centroids = None
        self.portNo = portNo
        self.numReducers = numReducers
        if os.path.exists(f"./Mappers/M{self.portNo-50051}"):
            # os.rmdir(f"./Mappers/M{portNo-50051}")
            shutil.rmtree(f"./Mappers/M{self.portNo-50051}")
        os.mkdir(f"./Mappers/M{self.portNo-50051}")
        self.ip = socket.gethostbyname(socket.gethostname())
        self.input_path = ""
        self.input = []

    def get_distance(self, point1, point2):
        return math.sqrt(math.pow(point1.x - point2.x, 2) + math.pow(point1.y-point2.y, 2))

    def GetData(self):
        channel = grpc.insecure_channel(self.ip+":50051")
        stub = map_reduce_pb2_grpc.MasterServiceStub(channel)
        request = map_reduce_pb2.MapDataRequest(ip="[::]:"+str(portNo), mapper_id=portNo)
        response = stub.SendMapperData(request)
        self.indices = response.input_split
        self.centroids = response.centroids
        # print(self.centroids)
        self.input_path = response.input_path
        self.Map(self.indices, self.centroids)

    def SendDataPoint(self, request, context):
        pass

    def Map(self, indices, centroids):
        file = open(self.input_path, "r")
        data_points = file.read().split("\n")
        data_points = [map_reduce_pb2.Point(x=float(data_points[i].split(",")[0]), y=float(data_points[i].split(",")[1])) for i in indices]
        # print(data_points)
        file.close()
        mapper_output = []
        self.input = data_points
        map = open(f"./Mappers/M{self.portNo-50051}/map.txt", "a")
        for point in self.input:
            min_dist = math.inf
            min_centroid = 0
            for i in range(len(centroids)):
                if min_dist > self.get_distance(point, centroids[i]):
                    min_centroid = i
                    min_dist = self.get_distance(point, centroids[i])
            mapper_output.append((min_centroid, point))
            map.write(f'({min_centroid}, {(point.x, point.y)})\n')
        map.close()
        self.Partition(mapper_output)

    def Partition(self, mapper_output):
        for i in range(self.numReducers):
            if not os.path.exists(f"./Mappers/M{self.portNo-50051}/partition_{i+1}.txt"):
                partition = open(f"./Mappers/M{self.portNo-50051}/partition_{i+1}.txt", "a")
                partition.close()

        for key, value in mapper_output:
            # Use a hash function to determine the reducer for this key
            reducer_id = key % self.numReducers
            partition = open(f"./Mappers/M{self.portNo-50051}/partition_{reducer_id+1}.txt", "a")
            partition.write(f'({key}, {(value.x, value.y)})\n')
            partition.close()


if __name__=='__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--portNo", type=int)
    argparser.add_argument("--numReducers", type=int)
    portNo = argparser.parse_args().portNo
    numReducers = argparser.parse_args().numReducers

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    mapper = Mapper(portNo, numReducers)
    map_reduce_pb2_grpc.add_MapperServiceServicer_to_server(mapper, server)

    server.add_insecure_port("[::]:"+str(portNo))
    server.start()
    mapper.GetData()
    server.wait_for_termination()