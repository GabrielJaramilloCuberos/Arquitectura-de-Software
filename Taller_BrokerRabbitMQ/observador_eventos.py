"""
Pontificia Universidad Javeriana
Autores: Gabriel Jaramillo, Guden Silva, Roberth Méndez, Luz Adriana Salazar, Jorge Olaya, Santiago Galindo
Fecha: Agosto 2026
Materia: Arquitectura de Software
Tema: RabbitMQ
Fichero: observador.py
Descripción: Observación y monitoreo de todos los eventos publicados en RabbitMQ.
"""

# Importamos json para convertir los mensajes
# recibidos en formato JSON a diccionarios Python.
import json


# Importamos datetime para obtener la fecha y hora
# en la que el observador recibe cada evento.
from datetime import datetime


# Importamos la conexión y el exchange configurados
# en config.py.
from config import get_connection, EXCHANGE


def callback(ch, method, properties, body):
    """
    Procesa cada evento observado en RabbitMQ.

    Este consumidor no modifica el mensaje ni lo reenvía.
    Su función es exclusivamente monitorear y mostrar
    información de los eventos que circulan por el exchange.
    """

    # Convertimos el mensaje JSON en un diccionario.
    data = json.loads(body)


    # Mostramos el título del evento.
    print("🔎 EVENTO OBSERVADO")


    # datetime.now() obtiene la fecha y hora actual
    # de la máquina donde está ejecutándose este programa.
    print(
        f"   🕒 Hora     : "
        f"{datetime.now()}"
    )


    # method.routing_key contiene la routing key con
    # la cual fue publicado el mensaje.
    #
    # Esto permite saber por qué ruta llegó el evento.
    print(
        f"   🧭 Tópico   : "
        f"{method.routing_key}"
    )


    # data.get("origen") obtiene el componente que
    # estableció el origen del mensaje.
    #
    # Se utiliza .get() en lugar de ["origen"] para evitar
    # un KeyError si el campo no existe.
    print(
        f"   🏷️  Origen   : "
        f"{data.get('origen')}"
    )


    # Mostramos el contador actual.
    #
    # Nuevamente utilizamos .get() para permitir que
    # el campo no exista sin provocar una excepción.
    print(
        f"   🔢 Contador : "
        f"{data.get('contador')}"
    )


    # Separador visual.
    print("=" * 45)


# ============================================================
# CONEXIÓN CON RABBITMQ
# ============================================================

# Creamos una conexión con RabbitMQ.
connection = get_connection()


# Creamos un canal.
channel = connection.channel()


# Declaramos el exchange.
channel.exchange_declare(
    exchange=EXCHANGE,
    exchange_type="topic",
    durable=True
)


# ============================================================
# CREACIÓN DE UNA COLA TEMPORAL
# ============================================================

# queue="" indica que RabbitMQ debe generar
# automáticamente un nombre único para la cola.
#
# exclusive=True significa que la cola pertenece
# exclusivamente a esta conexión.
#
# Cuando la conexión se cierre, RabbitMQ eliminará
# automáticamente esta cola.
result = channel.queue_declare(
    queue="",
    exclusive=True
)


# Obtenemos el nombre generado automáticamente
# para la cola.
queue_name = result.method.queue


# ============================================================
# SUSCRIPCIÓN A TODOS LOS EVENTOS
# ============================================================

# Asociamos nuestra cola temporal al exchange.
#
# La routing key "#" es un comodín de los exchanges
# de tipo topic.
#
# "#" puede representar cero o más palabras separadas
# por puntos dentro de una routing key.
#
# Por eso, esta cola puede recibir todos los mensajes
# publicados en el exchange.
channel.queue_bind(
    exchange=EXCHANGE,
    queue=queue_name,
    routing_key="#"
)


# Registramos callback() como manejador de los mensajes.
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=True
)


# Indicamos que el observador está activo.
print(
    "👁️  Observador de eventos "
    "escuchando TODO...\n"
)


try:
    # Iniciamos la escucha permanente.
    channel.start_consuming()


except KeyboardInterrupt:
    # Permitimos finalizar el observador mediante Ctrl + C.
    print("\n" + "=" * 38)
    print("👋 Cerrando observador de eventos...")
    print("=" * 38)


finally:
    # Cerramos la conexión.
    #
    # Como la cola fue declarada como exclusive,
    # RabbitMQ también podrá eliminarla al cerrarse
    # esta conexión.
    connection.close()