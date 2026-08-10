"""
Pontificia Universidad Javeriana
Autores: Gabriel Jaramillo, Guden Silva, Roberth Méndez, Luz Adriana Salazar, Jorge Olaya, Santiago Galindo
Fecha: Agosto 2026
Materia: Arquitectura de Software
Tema: RabbitMQ
Fichero: consumidor_registrar_matriz.py
Descripción: Consumidor final que registra en SQLite los elementos clasificados.
"""

# Importamos json para convertir los mensajes
# recibidos en formato JSON a diccionarios Python.
import json


# Importamos sqlite3 para crear y usar la base de datos
# local donde se almacenan los registros procesados.
import sqlite3


# Importamos Path para construir la ruta del archivo
# SQLite de manera segura y relativa al script.
from pathlib import Path


# Importamos la configuración del exchange y la función
# encargada de crear la conexión con RabbitMQ.
from config import EXCHANGE, get_connection


# Ruta del archivo SQLite donde se guardarán los registros.
DB_PATH = Path(__file__).with_name("registros_procesados.db")


# Nombre exacto de la cola final del flujo.
QUEUE_NAME = "cola-matriz"


def inicializar_base_datos():
    """
    Crea la base de datos SQLite y la tabla de registros.

    Si la base de datos no existe, SQLite la genera automáticamente.
    """

    with sqlite3.connect(DB_PATH) as conexion:
        cursor = conexion.cursor()


        # La tabla almacena el elemento y su clasificación final.
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS registros_procesados (
                elemento TEXT NOT NULL,
                tipo_elemento TEXT NOT NULL,
                contador_final INTEGER
            )
            """
        )


        # Si la base fue creada antes de incluir la columna
        # contador_final, la agregamos sin perder los datos previos.
        columnas = {
            fila[1] for fila in cursor.execute("PRAGMA table_info(registros_procesados)")
        }
        if "contador_final" not in columnas:
            cursor.execute(
                "ALTER TABLE registros_procesados ADD COLUMN contador_final INTEGER"
            )

        conexion.commit()


def obtener_datos_mensaje(body):
    """
    Extrae el elemento, el tipo y el contador desde el mensaje recibido.

    El consumidor acepta tanto las claves del taller original como una
    versión normalizada para mantener compatibilidad con el flujo.
    """

    data = json.loads(body.decode("utf-8"))


    # En el flujo del taller el elemento puede llegar como 'alimento'.
    elemento = data.get("elemento", data.get("alimento"))


    # La clasificación puede llegar como 'tipo' o como 'tipo_elemento'.
    tipo_elemento = data.get("tipo_elemento", data.get("tipo"))


    # El contador representa el avance del flujo y se incrementa al final.
    contador = data.get("contador", 0)

    if not elemento or not tipo_elemento:
        raise ValueError("El mensaje no contiene 'elemento' y 'tipo_elemento' válidos")

    if not isinstance(contador, int):
        raise ValueError("El campo 'contador' debe ser un numero entero")

    return elemento, tipo_elemento, contador + 1


def guardar_registro(elemento, tipo_elemento, contador_final):
    """
    Inserta un registro procesado dentro de SQLite.

    La escritura se hace en una transacción pequeña y directa para
    mantener simple la persistencia del consumidor final.
    """

    with sqlite3.connect(DB_PATH) as conexion:
        cursor = conexion.cursor()


        # Guardamos el elemento, su clasificación y el contador final.
        cursor.execute(
            """
            INSERT INTO registros_procesados (elemento, tipo_elemento, contador_final)
            VALUES (?, ?, ?)
            """,
            (elemento, tipo_elemento, contador_final),
        )

        conexion.commit()


def callback(ch, method, properties, body):
    """
    Procesa cada mensaje que llega a cola-matriz.

    Solo se envía ACK después de que el registro queda guardado en SQLite.
    """

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
    """
    Inicia el consumidor y deja el proceso en escucha permanente.
    """

    inicializar_base_datos()

    try:
        # Creamos la conexión y el canal contra CloudAMQP.
        connection = get_connection()
        channel = connection.channel()


        # Declaramos el exchange tipo topic y la cola final del flujo.
        channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.queue_bind(exchange=EXCHANGE, queue=QUEUE_NAME, routing_key="Matriz")


        # Procesamos un mensaje a la vez para confirmar solo
        # cuando la persistencia en SQLite haya sido exitosa.
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
