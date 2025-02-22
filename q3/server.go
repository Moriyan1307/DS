package main

import (
	"context"
	"fmt"
	"net"

	pb "service/servicepb"

	"google.golang.org/grpc"
)

type server struct {
	pb.UnimplementedMathServiceServer
}

func (s *server) Add(ctx context.Context, req *pb.AddRequest) (*pb.AddResponse, error) {
	result := req.Num1 + req.Num2
	return &pb.AddResponse{Result: result}, nil
}

func main() {
	listener, err := net.Listen("tcp", ":50051")
	if err != nil {
		fmt.Println("Failed to listen:", err)
		return
	}

	grpcServer := grpc.NewServer()
	pb.RegisterMathServiceServer(grpcServer, &server{})

	fmt.Println("Go gRPC Server started on port 50051")
	if err := grpcServer.Serve(listener); err != nil {
		fmt.Println("Failed to serve:", err)
	}
}
