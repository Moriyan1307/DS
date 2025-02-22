FROM python:3.9
WORKDIR /app
COPY . /app
RUN pip install grpcio grpcio-tools
CMD ["python", "server.py"]
