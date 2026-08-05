import json
from config import get_connection, EXCHANGE

def callback(ch, method, properties, body):
    data = json.loads(body)
    data["contador"] += 1
    data["origen"] = "Extraer_Texto"

    print(f"📥 Extraer_Texto | Contador: {data['contador']}")

    ch.basic_publish(
        exchange=EXCHANGE,
        routing_key="Clasificar",
        body=json.dumps(data)
    )

connection = get_connection()
channel = connection.channel()

channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
channel.queue_declare(queue="cola_extraer", durable=True)
channel.queue_bind(exchange=EXCHANGE, queue="cola_extraer", routing_key="Extraer")

channel.basic_consume(
    queue="cola_extraer",
    on_message_callback=callback,
    auto_ack=True
)

print("👂 Consumidor Extraer_Texto escuchando...")
channel.start_consuming()
