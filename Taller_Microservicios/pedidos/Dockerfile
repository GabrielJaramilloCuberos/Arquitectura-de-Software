docker build -t micro-pedidos:1.0 ./pedidos
docker run --rm -p 8002:8000 ^
    -e PRODUCTOS_URL=http://host.docker.internal:8001 ^
    -e NOTIFICACIONES_URL=http://host.docker.internal:8003 ^
    micro-pedidos:1.0
POST http://localhost:8002/pedidos
{"producto_id":1,"cantidad":2}