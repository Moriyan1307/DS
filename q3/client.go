package main

import (
	"context"
	"fmt"
	"log"
	"os"

	pb "my-proj/service"

	"google.golang.org/grpc"
)

func main() {
	conn, err := grpc.Dial("go-server:50051", grpc.WithInsecure())
	if err != nil {
		log.Fatalf("did not connect: %v", err)
	}
	defer conn.Close()

	c := pb.NewMyServiceClient(conn)

	name := "Muskan - Golang"
	if len(os.Args) > 1 {
		name = os.Args[1]
	}

	r, err := c.Greet(context.Background(), &pb.GreetingRequest{Name: name})
	if err != nil {
		log.Fatalf("could not greet: %v", err)
	}

	fmt.Printf("Go Client received: %s\n", r.GetMessage())
}
