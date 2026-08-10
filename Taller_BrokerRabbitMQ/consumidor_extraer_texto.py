import json
import unicodedata
from config import get_connection, EXCHANGE


def normalizar_alimento(texto):
    texto = texto.strip().lower()
    texto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")

def callback(ch, method, properties, body):
    data = json.loads(body)
    data["contador"] += 1
    data["origen"] = "Extraer_Texto"
    data["alimento"] = normalizar_alimento(data["alimento"])

    print("\n" + "=" * 45)
    print(f"📥 Extraer_Texto | Contador: {data['contador']}")

    ch.basic_publish(
        exchange=EXCHANGE,
        routing_key="Clasificar",
        body=json.dumps(data)
    )
    print(f"✅ Enviado a cola_clasificar: {data['alimento']}")
    print("=" * 45)

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

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("\n" + "=" * 38)
    print("👋 Cerrando consumidor Extraer_Texto...")
    print("=" * 38)
finally:
    connection.close()
