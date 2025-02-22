package main

import (
	"context"
	"fmt"
	"time"

	pb "service/servicepb"

	"google.golang.org/grpc"
)

func main() {
	conn, err := grpc.Dial("server:50051", grpc.WithInsecure())
	if err != nil {
		fmt.Println("Failed to connect:", err)
		return
	}
	defer conn.Close()

	client := pb.NewMathServiceClient(conn)

	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()

	resp, err := client.Add(ctx, &pb.AddRequest{Num1: 15, Num2: 25})
	if err != nil {
		fmt.Println("Error calling Add:", err)
		return
	}

	fmt.Printf("Go Client: 15 + 25 = %d\n", resp.Result)
}
