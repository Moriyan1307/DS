import grpc
import service_pb2
import service_pb2_grpc

def run():
    channel = grpc.insecure_channel("server:50051")
    stub = service_pb2_grpc.MathServiceStub(channel)
    response = stub.Add(service_pb2.AddRequest(num1=10, num2=20))
    print(f"Python Client: 10 + 20 = {response.result}")

if __name__ == "__main__":
    run()
