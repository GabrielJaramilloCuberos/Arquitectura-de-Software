"""
Pontificia Universidad Javeriana
Autores: Gabriel Jaramillo, Guden Silva, Roberth Méndez, Luz Adriana Salazar, Jorge Olaya, Santiago Galindo
Fecha: Agosto 2026
Materia: Arquitectura de Software
Tema: RabbitMQ
Fichero: clasificar_texto.py
Descripción: Clasificación de los alimentos recibidos y envío del resultado hacia la matriz.
"""

# Importamos json para poder convertir los mensajes
# entre objetos/diccionarios de Python y texto JSON.
import json


# Importamos desde config:
#
# get_connection:
#     Función encargada de crear la conexión con RabbitMQ.
#
# EXCHANGE:
#     Nombre del exchange utilizado por la aplicación.
from config import get_connection, EXCHANGE


# Importamos el diccionario de alimentos.
#
# Este diccionario debe contener los alimentos y su
# correspondiente categoría.
#
# Por ejemplo:
#
# alimentos = {
#     "manzana": "Fruta",
#     "zanahoria": "Verdura",
#     "arroz": "Cereal"
# }
from alimentos import alimentos


def clasificar_alimento(data):
    """
    Clasifica el alimento recibido.

    Args:
        data (dict):
            Diccionario que contiene la información del mensaje.

    Returns:
        dict:
            El mismo diccionario recibido, pero agregando
            el campo "tipo" con la clasificación del alimento.
    """

    # Obtenemos el nombre del alimento desde el diccionario.
    #
    # Se utiliza data["alimento"] porque esperamos que todos
    # los mensajes recibidos contengan obligatoriamente
    # este campo.
    alimento = data["alimento"]


    # Buscamos el alimento dentro del diccionario "alimentos".
    #
    # Si encontramos el alimento, obtenemos su categoría.
    #
    # Si no existe, .get() devuelve "Desconocido".
    tipo = alimentos.get(
        alimento,
        "Desconocido"
    )


    # Agregamos al mensaje una nueva propiedad llamada "tipo".
    #
    # De esta manera el mensaje pasa de tener, por ejemplo:
    #
    # {
    #     "alimento": "manzana"
    # }
    #
    # a:
    #
    # {
    #     "alimento": "manzana",
    #     "tipo": "Fruta"
    # }
    data["tipo"] = tipo


    # Retornamos el diccionario modificado.
    return data


def callback(ch, method, properties, body):
    """
    Función ejecutada automáticamente cada vez que
    RabbitMQ entrega un mensaje a este consumidor.

    Args:
        ch:
            Canal de comunicación utilizado con RabbitMQ.

        method:
            Información relacionada con la entrega del mensaje,
            incluyendo la routing key.

        properties:
            Propiedades adicionales del mensaje.

        body:
            Contenido del mensaje recibido.
    """

    # El mensaje recibido por RabbitMQ llega como bytes.
    #
    # json.loads() convierte el contenido JSON en un
    # diccionario de Python.
    data = json.loads(body)


    # Incrementamos el contador.
    #
    # El contador permite observar cuántas etapas del flujo
    # ha atravesado el mensaje.
    data["contador"] += 1


    # Actualizamos el origen para indicar qué componente
    # procesó el mensaje por última vez.
    data["origen"] = "Clasificar_Texto"


    # Imprimimos una línea decorativa para facilitar
    # la lectura de los mensajes en la consola.
    print("\n" + "=" * 45)


    # Mostramos el nombre del componente y el contador
    # actual del mensaje.
    print(
        f"📥 Clasificar_Texto | "
        f"Contador: {data['contador']}"
    )


    # Ejecutamos la función encargada de clasificar
    # el alimento.
    data = clasificar_alimento(data)


    # Mostramos en consola el alimento recibido.
    print(
        f"📥 Alimento recibido: "
        f"{data['alimento']}"
    )


    # Mostramos la categoría encontrada.
    print(
        f"🏷️  Tipo: "
        f"{data['tipo']}"
    )


    # Publicamos nuevamente el mensaje en RabbitMQ.
    #
    # exchange:
    #     Exchange central de la aplicación.
    #
    # routing_key:
    #     "Matriz" indica que el mensaje debe dirigirse
    #     hacia los consumidores interesados en esta ruta.
    #
    # body:
    #     Convertimos nuevamente el diccionario Python
    #     a formato JSON.
    ch.basic_publish(
        exchange=EXCHANGE,
        routing_key="Matriz",
        body=json.dumps(data)
    )


    # Informamos que el mensaje fue enviado.
    print(
        f"✅ Enviado a cola_matriz: "
        f"{data['alimento']} "
        f"({data['tipo']})"
    )


    # Línea final para separar visualmente
    # los diferentes mensajes procesados.
    print("=" * 45)


# ============================================================
# CREACIÓN DE LA CONEXIÓN Y DEL CANAL
# ============================================================

# Obtenemos una conexión con RabbitMQ utilizando
# la función definida en config.py.
connection = get_connection()


# A partir de la conexión creamos un canal.
#
# El canal representa una sesión lógica de comunicación
# dentro de la conexión RabbitMQ.
channel = connection.channel()


# Declaramos el exchange utilizado por la aplicación.
#
# exchange_type="topic":
#     Permite enrutar mensajes utilizando routing keys.
#
# durable=True:
#     Indica que el exchange debe sobrevivir al reinicio
#     del servidor RabbitMQ.
channel.exchange_declare(
    exchange=EXCHANGE,
    exchange_type="topic",
    durable=True
)


# Declaramos la cola donde este consumidor recibirá
# los mensajes.
#
# durable=True hace que la cola sea persistente.
channel.queue_declare(
    queue="cola_clasificar",
    durable=True
)


# Vinculamos la cola con el exchange.
#
# Los mensajes publicados con routing_key="Clasificar"
# serán enviados a esta cola.
channel.queue_bind(
    exchange=EXCHANGE,
    queue="cola_clasificar",
    routing_key="Clasificar"
)


# Registramos la función callback como manejador
# de los mensajes recibidos.
#
# Cada vez que llegue un mensaje a cola_clasificar,
# RabbitMQ ejecutará callback().
#
# auto_ack=True significa que el mensaje se considera
# reconocido automáticamente después de ser entregado.
channel.basic_consume(
    queue="cola_clasificar",
    on_message_callback=callback,
    auto_ack=True
)


# Mensaje informativo indicando que el consumidor
# está preparado y esperando mensajes.
print("👂 Consumidor Clasificar_Texto escuchando...")


try:
    # Iniciamos el ciclo de consumo.
    #
    # Esta instrucción mantiene el programa escuchando
    # nuevos mensajes indefinidamente.
    channel.start_consuming()


except KeyboardInterrupt:
    # Permite cerrar el programa correctamente cuando
    # el usuario presiona Ctrl + C.
    print("\n" + "=" * 45)
    print("👋 Cerrando consumidor Clasificar_Texto...")
    print("=" * 45)


finally:
    # Independientemente de si ocurrió una interrupción
    # o una finalización normal, cerramos la conexión.
    connection.close()