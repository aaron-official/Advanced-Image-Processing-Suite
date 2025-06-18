#!/bin/bash
# Build and run the app in Docker

docker build -t image-processing-suite .
docker run -d -p 7860:7860 --env-file ./config/.env image-processing-suite
