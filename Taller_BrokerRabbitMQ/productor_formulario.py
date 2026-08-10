"""
Pontificia Universidad Javeriana
Autores: Gabriel Jaramillo, Guden Silva, Roberth Méndez, Luz Adriana Salazar, Jorge Olaya, Santiago Galindo
Fecha: Agosto 2026
Materia: Arquitectura de Software
Tema: RabbitMQ
Fichero: productor_formulario.py
Descripción: Producción de un mensaje correspondiente a la recepción de un formulario ciudadano.
"""

# Importamos json para convertir el diccionario
# del mensaje a formato JSON.
import json


# Importamos la función de conexión y el exchange.
from config import get_connection, EXCHANGE


# ============================================================
# CONEXIÓN CON RABBITMQ
# ============================================================

# Creamos una conexión con el servidor RabbitMQ.
connection = get_connection()


# Creamos un canal para realizar operaciones
# de publicación de mensajes.
channel = connection.channel()


try:

    # Declaramos el exchange que utilizará
    # el productor.
    #
    # exchange_type="topic":
    # permite utilizar routing keys para decidir
    # hacia qué colas deben dirigirse los mensajes.
    #
    # durable=True:
    # hace que el exchange sea persistente.
    channel.exchange_declare(
        exchange=EXCHANGE,
        exchange_type="topic",
        durable=True
    )


    # Creamos el mensaje que representa
    # la recepción de un formulario ciudadano.
    #
    # origen:
    # indica qué componente produjo el mensaje.
    #
    # mensaje:
    # contiene la información textual del evento.
    #
    # contador:
    # comienza en cero porque todavía no ha pasado
    # por ningún componente consumidor.
    mensaje = {
        "origen": "Notificacion_Formulario",
        "mensaje": "Formulario ciudadano recibido",
        "contador": 0
    }


    # Publicamos el mensaje en el exchange.
    #
    # routing_key="Matriz":
    # indica que el mensaje está dirigido
    # a la ruta asociada con la matriz.
    #
    # json.dumps(mensaje):
    # convierte el diccionario de Python en
    # una cadena JSON para poder transmitirlo.
    channel.basic_publish(
        exchange=EXCHANGE,
        routing_key="Matriz",
        body=json.dumps(mensaje)
    )


    # Confirmamos en consola que el mensaje fue publicado.
    print("📤 Productor Formulario → Matriz")


except KeyboardInterrupt:

    # Si el usuario interrumpe el programa mediante
    # Ctrl + C, mostramos un mensaje de cierre.
    print("\n" + "=" * 35)
    print("👋 Cerrando productor Formulario...")
    print("=" * 35)


finally:

    # Cerramos la conexión con RabbitMQ.
    #
    # Esto libera los recursos asociados al canal
    # y a la conexión.
    connection.close()