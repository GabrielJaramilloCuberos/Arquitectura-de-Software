import json
from datetime import datetime
from config import get_connection, EXCHANGE

def callback(ch, method, properties, body):
    data = json.loads(body)

    print("🔎 EVENTO OBSERVADO")
    print(f"   🕒 Hora     : {datetime.now()}")
    print(f"   🧭 Tópico   : {method.routing_key}")
    print(f"   🏷️ Origen   : {data.get('origen')}")
    print(f"   🔢 Contador : {data.get('contador')}")
    print("-" * 60)

connection = get_connection()
channel = connection.channel()

channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)

result = channel.queue_declare(queue="", exclusive=True)
queue_name = result.method.queue

channel.queue_bind(
    exchange=EXCHANGE,
    queue=queue_name,
    routing_key="#"
)

channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=True
)

print("👁️ Observador de eventos escuchando TODO...")
channel.start_consuming()
