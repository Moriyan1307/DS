FROM python:3.9-slim

# Install gRPC dependencies
RUN pip install grpcio grpcio-tools

WORKDIR /app

# Copy everything
COPY . /app

# Expose port
EXPOSE 50051

# Run the node
CMD ["python", "swim_node.py"]
