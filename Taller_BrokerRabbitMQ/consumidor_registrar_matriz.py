import json
from config import get_connection, EXCHANGE

def callback(ch, method, properties, body):
    data = json.loads(body)
    data["contador"] += 1

    print("✅ Registro Insertado en la Matriz de Participación")
    print(f"   Contador final: {data['contador']}")

connection = get_connection()
channel = connection.channel()

channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
channel.queue_declare(queue="cola_matriz", durable=True)
channel.queue_bind(exchange=EXCHANGE, queue="cola_matriz", routing_key="Matriz")

channel.basic_consume(
    queue="cola_matriz",
    on_message_callback=callback,
    auto_ack=True
)

print("👂 Consumidor Registrar_Matriz escuchando...")

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("\n" + "=" * 35)
    print("👋 Cerrando consumidor Registrar_Matriz...")
    print("=" * 35)
finally:
    connection.close()
