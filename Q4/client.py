import grpc
import random
import time
import failure_detector_pb2
import failure_detector_pb2_grpc

NODES = [
    {"id": "A", "address": "localhost:50051"},
    {"id": "B", "address": "localhost:50052"},
    {"id": "C", "address": "localhost:50053"},
    {"id": "D", "address": "localhost:50054"},
]

TIMEOUT = 2  # Timeout for responses
K = 2  # Number of indirect probes

def send_ping(sender_id, receiver):
    with grpc.insecure_channel(receiver["address"]) as channel:
        stub = failure_detector_pb2_grpc.FailureDetectorStub(channel)
        request = failure_detector_pb2.PingRequest(sender_id=sender_id, receiver_id=receiver["id"])
        print(f"Component FailureDetector of Node {sender_id} sends RPC Ping to Component FailureDetector of Node {receiver['id']}")
        try:
            response = stub.Ping(request, timeout=TIMEOUT)
            return response.success
        except grpc.RpcError:
            return False

def send_indirect_ping(sender_id, target, helpers):
    for helper in helpers:
        with grpc.insecure_channel(helper["address"]) as channel:
            stub = failure_detector_pb2_grpc.FailureDetectorStub(channel)
            request = failure_detector_pb2.PingRequest(sender_id=sender_id, receiver_id=target["id"])
            print(f"Component FailureDetector of Node {sender_id} sends RPC IndirectPing to Component FailureDetector of Node {helper['id']}")
            try:
                response = stub.IndirectPing(request, timeout=TIMEOUT)
                if response.success:
                    return True
            except grpc.RpcError:
                pass
    return False

def failure_detection(node_id):
    while True:
        target = random.choice([n for n in NODES if n["id"] != node_id])
        if send_ping(node_id, target):
            print(f"Node {target['id']} is healthy.")
        else:
            print(f"Node {target['id']} did not respond. Requesting indirect probes.")
            helpers = random.sample([n for n in NODES if n["id"] not in (node_id, target["id"])], min(K, len(NODES)-2))
            if send_indirect_ping(node_id, target, helpers):
                print(f"Indirect probe succeeded, Node {target['id']} is healthy.")
            else:
                print(f"Node {target['id']} is marked as failed.")

        time.sleep(5)

if __name__ == "__main__":
    import sys
    node_id = sys.argv[1]
    failure_detection(node_id)
