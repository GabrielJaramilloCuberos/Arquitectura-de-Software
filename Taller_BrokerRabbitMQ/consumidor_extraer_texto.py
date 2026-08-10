"""
Pontificia Universidad Javeriana
Autores: Gabriel Jaramillo, Guden Silva, Roberth Méndez, Luz Adriana Salazar, Jorge Olaya, Santiago Galindo
Fecha: Agosto 2026
Materia: Arquitectura de Software
Tema: RabbitMQ
Fichero: extraer_texto.py
Descripción: Extracción y normalización del texto correspondiente a los alimentos recibidos.
"""

# Biblioteca estándar de Python que permite trabajar
# con caracteres Unicode.
#
# La utilizaremos para eliminar las tildes y otros
# signos diacríticos del texto.
import unicodedata


# Importamos json para transformar los mensajes
# entre JSON y diccionarios de Python.
import json


# Importamos la función para establecer la conexión
# con RabbitMQ y el nombre del exchange.
from config import get_connection, EXCHANGE


def normalizar_alimento(texto):
    """
    Normaliza el nombre de un alimento.

    El proceso realiza tres operaciones principales:

    1. Elimina espacios innecesarios al principio y al final.
    2. Convierte el texto a minúsculas.
    3. Elimina tildes y otros signos diacríticos.

    Args:
        texto (str):
            Nombre del alimento recibido.

    Returns:
        str:
            Texto normalizado.
    """

    # strip() elimina espacios en blanco al inicio y al final.
    #
    # lower() convierte todas las letras a minúsculas.
    #
    # Ejemplo:
    #
    # "  ManZáNa  "
    #
    # se convierte inicialmente en:
    #
    # "manzána"
    texto = texto.strip().lower()


    # NFD significa "Normalization Form Decomposed".
    #
    # Unicode puede representar un carácter como una
    # combinación de:
    #
    # - letra base
    # - marca diacrítica
    #
    # Por ejemplo, "á" puede descomponerse conceptualmente
    # como "a" + "´".
    texto = unicodedata.normalize(
        "NFD",
        texto
    )


    # Recorremos todos los caracteres del texto.
    #
    # unicodedata.category(c) permite conocer la categoría
    # Unicode de cada carácter.
    #
    # La categoría "Mn" corresponde a marcas no espaciadas,
    # entre las cuales se encuentran muchos signos diacríticos
    # como las tildes.
    #
    # De esta forma conservamos la letra base y eliminamos
    # la tilde.
    return "".join(
        c
        for c in texto
        if unicodedata.category(c) != "Mn"
    )


def callback(ch, method, properties, body):
    """
    Procesa cada mensaje recibido desde RabbitMQ.

    El callback recibe el mensaje, normaliza el nombre
    del alimento y posteriormente lo publica nuevamente
    utilizando la routing key "Clasificar".
    """

    # Convertimos el mensaje JSON recibido a un
    # diccionario de Python.
    data = json.loads(body)


    # Incrementamos el contador para registrar
    # que el mensaje pasó por otro componente.
    data["contador"] += 1


    # Actualizamos el origen del mensaje.
    data["origen"] = "Extraer_Texto"


    # Normalizamos el nombre del alimento.
    #
    # El resultado reemplaza el valor original.
    data["alimento"] = normalizar_alimento(
        data["alimento"]
    )


    # Mostramos información del proceso en consola.
    print("\n" + "=" * 45)
    print(
        f"📥 Extraer_Texto | "
        f"Contador: {data['contador']}"
    )


    # Publicamos el mensaje ya normalizado.
    #
    # La routing key "Clasificar" hará que el mensaje
    # llegue a la cola vinculada a esa ruta.
    ch.basic_publish(
        exchange=EXCHANGE,
        routing_key="Clasificar",
        body=json.dumps(data)
    )


    # Confirmamos visualmente el envío.
    print(
        f"✅ Enviado a cola_clasificar: "
        f"{data['alimento']}"
    )

    print("=" * 45)


# ============================================================
# CONFIGURACIÓN DEL CONSUMIDOR
# ============================================================

# Creamos la conexión con RabbitMQ.
connection = get_connection()


# Creamos un canal de comunicación.
channel = connection.channel()


# Declaramos el exchange.
channel.exchange_declare(
    exchange=EXCHANGE,
    exchange_type="topic",
    durable=True
)


# Declaramos la cola que recibirá los mensajes
# destinados al proceso de extracción.
channel.queue_declare(
    queue="cola_extraer",
    durable=True
)


# Vinculamos la cola con el exchange.
#
# Solamente los mensajes cuya routing key sea
# "Extraer" serán enviados a esta cola.
channel.queue_bind(
    exchange=EXCHANGE,
    queue="cola_extraer",
    routing_key="Extraer"
)


# Registramos callback() como función encargada
# de procesar los mensajes.
channel.basic_consume(
    queue="cola_extraer",
    on_message_callback=callback,
    auto_ack=True
)


# Mensaje informativo para indicar que el proceso
# está esperando nuevos mensajes.
print("👂 Consumidor Extraer_Texto escuchando...")


try:
    # Iniciamos el consumo permanente de mensajes.
    channel.start_consuming()


except KeyboardInterrupt:
    # Capturamos Ctrl + C para cerrar de forma controlada.
    print("\n" + "=" * 38)
    print("👋 Cerrando consumidor Extraer_Texto...")
    print("=" * 38)


finally:
    # Cerramos la conexión con RabbitMQ.
    connection.close()