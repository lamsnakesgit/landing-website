#!/bin/bash
cd /root/evolution-api
docker-compose up -d
echo "Waiting for Evolution API to start..."
sleep 20
docker logs --tail 20 evolution_api
