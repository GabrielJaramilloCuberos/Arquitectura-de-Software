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
    "origen": "Notificacion_Radicado",
    "mensaje": "Se ha radicado una nueva solicitud",
    "contador": 0
}

channel.basic_publish(
    exchange=EXCHANGE,
    routing_key="Extraer",
    body=json.dumps(mensaje)
)

print("📤 Productor Radicado → Extraer")
connection.close()
