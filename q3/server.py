from concurrent import futures
import grpc
import service_pb2
import service_pb2_grpc

class MyServiceServicer(service_pb2_grpc.MyServiceServicer):
    def Greet(self, request, context):
        return service_pb2.GreetingResponse(message=f"Hello, {request.name}!")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_MyServiceServicer_to_server(MyServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("Python Server started at [::]:50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
