#!/bin/bash
mkdir -p /root/evolution-api
cd /root/evolution-api

cat << 'EOF' > docker-compose.yml
version: '3.3'

services:
  evolution-api:
    image: evoapicloud/evolution-api:latest
    container_name: evolution_api
    restart: always
    ports:
      - "8080:8080"
    environment:
      - SERVER_URL=http://151.244.228.104:8080
      - DOCKER_ENV=true
      - LOG_LEVEL=ERROR,WARN,DEBUG,INFO,LOG,VERBOSE,DARK,FATAL
      - LOG_COLOR=true
      - AUTHENTICATION_TYPE=apikey
      - AUTHENTICATION_API_KEY=B6D711FCDE4D4FD5936544120E713976
      - AUTHENTICATION_EXPOSE_IN_ENV=true
      - DEL_INSTANCE=false
      - DATABASE_PROVIDER=postgresql
      - DATABASE_CONNECTION_URI=postgresql://postgres:postgres@postgres:5432/evolution?schema=public
      - DATABASE_CONNECTION_CLIENT_NAME=evolution_api
      - REDIS_ENABLED=true
      - REDIS_URI=redis://redis:6379/1
      - WEBSOCKET_ENABLED=false
      - RABBITMQ_ENABLED=false
      - SQS_ENABLED=false
      - WEBHOOK_GLOBAL_ENABLED=false
    volumes:
      - ./instances:/evolution/instances
      - ./store:/evolution/store
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15-alpine
    container_name: postgres_evo
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=evolution
    volumes:
      - ./postgres:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    container_name: redis_evo
    restart: always
    command: redis-server --appendonly yes
    volumes:
      - ./redis:/data
EOF

docker compose up -d
echo "Waiting for Evolution API to start..."
sleep 20
docker logs --tail 20 evolution_api
