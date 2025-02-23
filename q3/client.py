import grpc
import service_pb2
import service_pb2_grpc

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = service_pb2_grpc.MyServiceStub(channel)
    response = stub.Greet(service_pb2.GreetingRequest(name="Alice"))
    print(f"Python Client received: {response.message}")

if __name__ == '__main__':
    run()
