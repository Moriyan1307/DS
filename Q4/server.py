import grpc
from concurrent import futures
import time
import failure_detector_pb2
import failure_detector_pb2_grpc

class FailureDetectorServicer(failure_detector_pb2_grpc.FailureDetectorServicer):
    def __init__(self, node_id):
        self.node_id = node_id

    def Ping(self, request, context):
        print(f"Component FailureDetector of Node {self.node_id} runs RPC Ping called by Component FailureDetector of Node {request.sender_id}")
        return failure_detector_pb2.PingResponse(success=True)

    def IndirectPing(self, request, context):
        print(f"Component FailureDetector of Node {self.node_id} runs RPC IndirectPing called by Component FailureDetector of Node {request.sender_id}")
        return failure_detector_pb2.PingResponse(success=True)

def serve(node_id, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    failure_detector_pb2_grpc.add_FailureDetectorServicer_to_server(FailureDetectorServicer(node_id), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"Node {node_id} failure detector server started on port {port}.")
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    import sys
    node_id = sys.argv[1]
    port = sys.argv[2]
    serve(node_id, port)
