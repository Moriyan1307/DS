import grpc
from concurrent import futures
import service_pb2
import service_pb2_grpc

class MathServiceServicer(service_pb2_grpc.MathServiceServicer):
    def Add(self, request, context):
        result = request.num1 + request.num2
        return service_pb2.AddResponse(result=result)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_MathServiceServicer_to_server(MathServiceServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Python gRPC Server started on port 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
