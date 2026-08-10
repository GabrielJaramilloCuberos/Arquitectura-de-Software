import json
import sqlite3
from pathlib import Path

from config import EXCHANGE, get_connection

DB_PATH = Path(__file__).with_name("registros_procesados.db")
QUEUE_NAME = "cola-matriz"


def inicializar_base_datos():
    with sqlite3.connect(DB_PATH) as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS registros_procesados (
                elemento TEXT NOT NULL,
                tipo_elemento TEXT NOT NULL,
                contador_final INTEGER
            )
            """
        )
        columnas = {
            fila[1] for fila in cursor.execute("PRAGMA table_info(registros_procesados)")
        }
        # Mantiene los registros previos si la base fue creada antes de esta columna.
        if "contador_final" not in columnas:
            cursor.execute(
                "ALTER TABLE registros_procesados ADD COLUMN contador_final INTEGER"
            )
        conexion.commit()


def obtener_datos_mensaje(body):
    data = json.loads(body.decode("utf-8"))
    elemento = data.get("elemento", data.get("alimento"))
    tipo_elemento = data.get("tipo_elemento", data.get("tipo"))
    contador = data.get("contador", 0)

    if not elemento or not tipo_elemento:
        raise ValueError("El mensaje no contiene 'elemento' y 'tipo_elemento' válidos")

    if not isinstance(contador, int):
        raise ValueError("El campo 'contador' debe ser un numero entero")

    return elemento, tipo_elemento, contador + 1


def guardar_registro(elemento, tipo_elemento, contador_final):
    with sqlite3.connect(DB_PATH) as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO registros_procesados (elemento, tipo_elemento, contador_final)
            VALUES (?, ?, ?)
            """,
            (elemento, tipo_elemento, contador_final),
        )
        conexion.commit()


def callback(ch, method, properties, body):
    try:
        elemento, tipo_elemento, contador = obtener_datos_mensaje(body)
        guardar_registro(elemento, tipo_elemento, contador)

        ch.basic_ack(delivery_tag=method.delivery_tag)

        print("✅ Registro insertado en la Matriz de Participación")
        print(f"Contador final: {contador}")
    except (json.JSONDecodeError, ValueError) as error:
        print(f"⚠️  Mensaje inválido descartado: {error}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except sqlite3.Error as error:
        print(f"❌ Error de base de datos: {error}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    except Exception as error:
        print(f"❌ Error inesperado procesando el mensaje: {error}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def main():
    inicializar_base_datos()

    try:
        connection = get_connection()
        channel = connection.channel()

        channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.queue_bind(exchange=EXCHANGE, queue=QUEUE_NAME, routing_key="Matriz")

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=callback,
            auto_ack=False,
        )

        print("👂 Consumidor Registrar_Matriz escuchando en cola-matriz...")

        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n" + "=" * 35)
        print("👋 Cerrando consumidor Registrar_Matriz...")
        print("=" * 35)
    except Exception as error:
        print(f"❌ No fue posible iniciar el consumidor: {error}")
    finally:
        try:
            if "connection" in locals() and connection.is_open:
                connection.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
