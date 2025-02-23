package main

import (
	"context"
	"fmt"
	"log"
	"net"

	pb "my-proj/service"

	"google.golang.org/grpc"
)

type server struct {
	pb.UnimplementedMyServiceServer
}

func (s *server) Greet(ctx context.Context, in *pb.GreetingRequest) (*pb.GreetingResponse, error) {
	return &pb.GreetingResponse{Message: "Hello, " + in.GetName()}, nil
}

func main() {
	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	s := grpc.NewServer()
	pb.RegisterMyServiceServer(s, &server{})

	fmt.Println("Go Server started at :50051")
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
