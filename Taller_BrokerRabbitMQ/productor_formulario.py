import json
from config import get_connection, EXCHANGE

connection = get_connection()
channel = connection.channel()

channel.exchange_declare(
    exchange=EXCHANGE,
    exchange_type="topic",
    durable=True
)

mensaje = {
    "origen": "Notificacion_Formulario",
    "mensaje": "Formulario ciudadano recibido",
    "contador": 0
}

channel.basic_publish(
    exchange=EXCHANGE,
    routing_key="Matriz",
    body=json.dumps(mensaje)
)

print("📤 Productor Formulario → Matriz")
connection.close()
