import grpc
from concurrent import futures
import map_reduce_pb2
import map_reduce_pb2_grpc

class Mapper(map_reduce_pb2_grpc.MapperServiceServicer):
    def __init__(self, indices, centroids):
        self.indices = indices
        self.centroids = centroids

    def map(self):
        pass
    
    def partition(self):
        pass
if __name__=='__main__':
    pass