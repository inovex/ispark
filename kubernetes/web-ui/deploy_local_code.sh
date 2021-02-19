#!/bin/bash
IMAGE_TAG="02"

docker build -t <REGISTRY:$TAG> .
docker push <REGISTRY:$TAG>

#bash deploy_web_server.sh
