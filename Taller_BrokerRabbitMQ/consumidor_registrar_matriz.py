"""
Pontificia Universidad Javeriana
Autores: Gabriel Jaramillo, Guden Silva, Roberth Méndez, Luz Adriana Salazar, Jorge Olaya, Santiago Galindo
Fecha: Agosto 2026
Materia: Arquitectura de Software
Tema: RabbitMQ
Fichero: registrar_matriz.py
Descripción: Registro de los alimentos procesados en la matriz de participación.
"""

# Importamos json para convertir el mensaje recibido
# desde formato JSON a un diccionario de Python.
import json


# Importamos la función encargada de crear la conexión
# y el nombre del exchange.
from config import get_connection, EXCHANGE


def callback(ch, method, properties, body):
    """
    Procesa un mensaje recibido en la cola de la matriz.

    Esta función representa la etapa final del flujo.
    Actualmente no almacena físicamente la información
    en una base de datos; simplemente simula el registro
    mostrando la información en consola.
    """

    # Convertimos el mensaje JSON recibido
    # en un diccionario de Python.
    data = json.loads(body)


    # Incrementamos el contador para indicar que
    # el mensaje llegó a la última etapa del proceso.
    data["contador"] += 1


    # Mostramos un mensaje indicando que el registro
    # fue realizado.
    print(
        "✅ Registro Insertado en la "
        "Matriz de Participación"
    )


    # Mostramos el valor final del contador.
    print(
        f"   Contador final: "
        f"{data['contador']}"
    )


# ============================================================
# CREACIÓN DE CONEXIÓN Y CANAL
# ============================================================

# Establecemos la conexión con RabbitMQ.
connection = get_connection()


# Creamos un canal para trabajar con RabbitMQ.
channel = connection.channel()


# Declaramos el exchange utilizado por la aplicación.
channel.exchange_declare(
    exchange=EXCHANGE,
    exchange_type="topic",
    durable=True
)


# Declaramos la cola donde se recibirán
# los mensajes destinados a la matriz.
channel.queue_declare(
    queue="cola_matriz",
    durable=True
)


# Asociamos la cola con el exchange utilizando
# la routing key "Matriz".
channel.queue_bind(
    exchange=EXCHANGE,
    queue="cola_matriz",
    routing_key="Matriz"
)


# Indicamos que callback() será ejecutada
# cada vez que llegue un mensaje.
channel.basic_consume(
    queue="cola_matriz",
    on_message_callback=callback,
    auto_ack=True
)


# Indicamos que el consumidor está activo.
print("👂 Consumidor Registrar_Matriz escuchando...")


try:
    # Mantenemos el proceso escuchando mensajes.
    channel.start_consuming()


except KeyboardInterrupt:
    # Permite cerrar el consumidor mediante Ctrl + C.
    print("\n" + "=" * 35)
    print("👋 Cerrando consumidor Registrar_Matriz...")
    print("=" * 35)


finally:
    # Cerramos la conexión al finalizar.
    connection.close()