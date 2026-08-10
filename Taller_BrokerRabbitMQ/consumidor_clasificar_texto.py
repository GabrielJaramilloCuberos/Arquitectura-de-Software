import json
from config import get_connection, EXCHANGE
from alimentos import alimentos

def clasificar_alimento(data):
    alimento = data["alimento"]
    tipo = alimentos.get(alimento, "Desconocido")
    data["tipo"] = tipo
    return data

def callback(ch, method, properties, body):
    data = json.loads(body)
    data["contador"] += 1
    data["origen"] = "Clasificar_Texto"

    print("\n" + "=" * 45)
    print(f"📥 Clasificar_Texto | Contador: {data['contador']}")

    # Clasificar el alimento
    data = clasificar_alimento(data)
    print(f"📥 Alimento recibido: {data['alimento']}")
    print(f"🏷️  Tipo: {data['tipo']}")
    
    ch.basic_publish(
        exchange=EXCHANGE,
        routing_key="Matriz",
        body=json.dumps(data)
    )
    print(f"✅ Enviado a cola_matriz: {data['alimento']} ({data['tipo']})")
    print("=" * 45)

connection = get_connection()
channel = connection.channel()

channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
channel.queue_declare(queue="cola_clasificar", durable=True)
channel.queue_bind(exchange=EXCHANGE, queue="cola_clasificar", routing_key="Clasificar")

channel.basic_consume(
    queue="cola_clasificar",
    on_message_callback=callback,
    auto_ack=True
)

print("👂 Consumidor Clasificar_Texto escuchando...")

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("\n" + "=" * 45)
    print("👋 Cerrando consumidor Clasificar_Texto...")
    print("=" * 45)
finally:
    connection.close()
