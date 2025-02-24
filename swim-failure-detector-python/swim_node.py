import os
import random
import time
import threading
import grpc

from concurrent import futures
# Generated from the proto file
import swim_pb2
import swim_pb2_grpc

# Constants for the Failure Detector
T_PRIME = 5     # Ping interval (seconds)
K = 2           # Number of indirect pings
TIMEOUT = 4     # Timeout to wait for an ACK (seconds)

COMPONENT_NAME = "FailureDetector"

class SwimServiceServicer(swim_pb2_grpc.SwimServiceServicer):
    def __init__(self, node_id, node):
        self.node_id = node_id
        self.node = node  # reference to parent Node

    def Ping(self, request, context):
        # Server-side log
        print(f"Component {COMPONENT_NAME} of Node {self.node_id} "
              f"runs RPC Ping called by Component {COMPONENT_NAME} of Node {request.from_id}")

        # Return ACK
        response = swim_pb2.PingResponse(ack=True, from_id=self.node_id)
        return response

    def IndirectPing(self, request, context):
        # Server-side log
        print(f"Component {COMPONENT_NAME} of Node {self.node_id} "
              f"runs RPC IndirectPing called by Component {COMPONENT_NAME} of Node {request.original_id}")

        # Node X (self.node_id) pings B (request.target_id) on behalf of A (request.original_id)
        target_id = request.target_id
        if target_id not in self.node.members:
            # if we don't know the target node, return ack=False
            return swim_pb2.PingResponse(ack=False, from_id=self.node_id)

        channel = grpc.insecure_channel(self.node.members[target_id]['address'])
        stub = swim_pb2_grpc.SwimServiceStub(channel)

        # Client-side log
        print(f"Component {COMPONENT_NAME} of Node {self.node_id} sends RPC Ping "
              f"to Component {COMPONENT_NAME} of Node {target_id}")

        ack = False
        try:
            ping_response = stub.Ping(swim_pb2.PingRequest(from_id=self.node_id))
            ack = ping_response.ack
            if ack:
                # mark the target as alive in X's membership
                self.node.members[target_id]['alive'] = True
                self.node.members[target_id]['last_heartbeat'] = time.time()
        except:
            ack = False

        return swim_pb2.PingResponse(ack=ack, from_id=self.node_id)


class Node:
    def __init__(self, node_id, port, members):
        """
        members is a dict of {node_id: { address: 'host:port', alive: bool, last_heartbeat: float }}
        """
        self.node_id = node_id
        self.port = port
        self.members = members

        # Initialize membership
        for m_id, info in self.members.items():
            info.setdefault('alive', True)
            info.setdefault('last_heartbeat', time.time())

        # Start gRPC server
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        self.servicer = SwimServiceServicer(self.node_id, self)
        swim_pb2_grpc.add_SwimServiceServicer_to_server(self.servicer, self.server)
        self.server.add_insecure_port(f"[::]:{self.port}")

        self.server_thread = threading.Thread(target=self.server.start, daemon=True)
        self.server_thread.start()
        print(f"Node {self.node_id} gRPC server running on port {self.port}")

        # Start periodic pings
        self.ping_thread = threading.Thread(target=self.run_pings, daemon=True)
        self.ping_thread.start()

    def run_pings(self):
        while True:
            time.sleep(T_PRIME)

            # pick a random alive target
            alive_nodes = [m for m, info in self.members.items() if info['alive']]
            if len(alive_nodes) <= 1 and self.node_id in alive_nodes:
                continue  # no other node to ping

            target = random.choice(alive_nodes)
            if target == self.node_id:
                continue

            # Client-side log
            print(f"Component {COMPONENT_NAME} of Node {self.node_id} sends RPC Ping "
                  f"to Component {COMPONENT_NAME} of Node {target}")

            channel = grpc.insecure_channel(self.members[target]['address'])
            stub = swim_pb2_grpc.SwimServiceStub(channel)

            ack_received = False
            try:
                future = stub.Ping.future(swim_pb2.PingRequest(from_id=self.node_id))
                response = future.result(timeout=TIMEOUT)
                if response.ack:
                    ack_received = True
                    # mark them alive
                    self.members[target]['alive'] = True
                    self.members[target]['last_heartbeat'] = time.time()
            except:
                ack_received = False

            if not ack_received:
                print(f"Node {self.node_id} did NOT receive ACK from {target}. "
                      f"Attempting IndirectPing with k={K} other nodes.")

                other_candidates = [m for m in alive_nodes if m not in [self.node_id, target]]
                random.shuffle(other_candidates)
                indirect_nodes = other_candidates[:K]
                indirect_ack = False

                for ind_id in indirect_nodes:
                    # Client-side log
                    print(f"Component {COMPONENT_NAME} of Node {self.node_id} sends RPC IndirectPing "
                          f"to Component {COMPONENT_NAME} of Node {ind_id}")

                    channel_ind = grpc.insecure_channel(self.members[ind_id]['address'])
                    stub_ind = swim_pb2_grpc.SwimServiceStub(channel_ind)

                    try:
                        ip_resp = stub_ind.IndirectPing(swim_pb2.IndirectPingRequest(
                            original_id=self.node_id, target_id=target
                        ))
                        if ip_resp.ack:
                            # the target responded indirectly
                            self.members[target]['alive'] = True
                            self.members[target]['last_heartbeat'] = time.time()
                            indirect_ack = True
                            break
                    except:
                        pass

                if not indirect_ack:
                    # declare target failed
                    print(f"Node {target} is declared FAILED by {self.node_id}")
                    self.members[target]['alive'] = False

    def stop(self):
        self.server.stop(0)


def main():
    # read environment
    node_id = os.environ.get("NODE_ID", "Node1")
    port = os.environ.get("PORT", "50051")
    members_str = os.environ.get("MEMBERS", "")  # "Node1:localhost:50051,Node2:localhost:50052"

    members = {}
    if members_str:
        arr = [x.strip() for x in members_str.split(",") if x.strip()]
        for m in arr:
            parts = m.split(":")
            if len(parts) == 3:
                mid, host, prt = parts
                members[mid] = {"address": f"{host}:{prt}"}

    # ensure self is in membership
    if node_id not in members:
        members[node_id] = {"address": f"localhost:{port}"}

    node = Node(node_id, port, members)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        node.stop()


if __name__ == "__main__":
    main()
