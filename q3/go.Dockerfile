FROM golang:1.20
WORKDIR /app
COPY . /app
RUN go mod tidy
RUN go build -o server server.go
CMD ["/app/server"]
