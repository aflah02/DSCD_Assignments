import grpc
from concurrent import futures
import map_reduce_pb2
import map_reduce_pb2_grpc
import argparse

class Reducer(map_reduce_pb2_grpc.ReducerServiceServicer):
    def __init__(self):
        pass
    
    def SendPartition(self, request, context):
        pass
    def shuffle_sort(self):
        pass
    def reduce(self):
        pass

if __name__=='__main__':
    pass