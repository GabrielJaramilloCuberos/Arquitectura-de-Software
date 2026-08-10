import json
from config import get_connection, EXCHANGE

connection = get_connection()
channel = connection.channel()

channel.exchange_declare(
    exchange=EXCHANGE,
    exchange_type="topic",
    durable=True
)

print("📤 Productor Radicado - Escriba sus alimentos")

try:
    while True:
        print("\n" + "=" * 45)
        alimento = input("🍎 Alimento: ").strip()

        if alimento.lower() == "salir":
            raise KeyboardInterrupt

        if not alimento:
            print("⚠️  Debe ingresar un alimento.\n")
            print("=" * 45)
            continue

        mensaje = {
            "origen": "Notificacion_Radicado",
            "alimento": alimento,
            "contador": 0
        }

        channel.basic_publish(
            exchange=EXCHANGE,
            routing_key="Extraer",
            body=json.dumps(mensaje)
        )

        print(f"✅ Enviado a cola_extraer: {alimento}")
        print("=" * 45)
        
except KeyboardInterrupt:
    print("\n" + "=" * 35)
    print("👋 Cerrando productor...")
    print("=" * 35)
finally:
    connection.close()
