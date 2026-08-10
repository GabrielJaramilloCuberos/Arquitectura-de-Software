"""
Pontificia Universidad Javeriana
Autores: Gabriel Jaramillo, Guden Silva, Roberth Méndez, Luz Adriana Salazar, Jorge Olaya, Santiago Galindo
Fecha: Agosto 2026
Materia: Arquitectura de Software
Tema: RabbitMQ
Fichero: config.py
Descripción: Configuración y creación de la conexión con el servidor RabbitMQ.
"""

# Importamos la biblioteca Pika.
# Pika es una biblioteca de Python que permite comunicarse
# con servidores RabbitMQ utilizando el protocolo AMQP.
import pika


# ============================================================
# CONFIGURACIÓN DE RABBITMQ
# ============================================================

# Las siguientes líneas corresponden a una configuración
# anterior de RabbitMQ.
#
# Se mantienen comentadas como referencia, pero no participan
# actualmente en la ejecución del programa.
#
# RABBITMQ_HOST = "gerbil.rmq.cloudamqp.com"
# RABBITMQ_PORT = 5672
# USERNAME = "etpyjjad"
# PASSWORD = "tNhqawuyTs3W0-pOrL6WpxU1SBCNZ1hb"
# VHOST = "etpyjjad"


# Dirección del servidor RabbitMQ.
#
# En este caso se utiliza un servidor proporcionado por
# CloudAMQP, que permite utilizar RabbitMQ como servicio
# alojado en la nube.
RABBITMQ_HOST = "gull-01.rmq.cloudamqp.com"


# Puerto utilizado para la conexión AMQP con RabbitMQ.
#
# El puerto 5672 corresponde al puerto estándar de AMQP
# cuando no se utiliza una conexión AMQP sobre TLS.
RABBITMQ_PORT = 5672


# Nombre de usuario utilizado para autenticarse
# en el servidor RabbitMQ.
USERNAME = "woqbgkcj"


# Contraseña correspondiente al usuario anterior.
#
# IMPORTANTE:
# En una aplicación real no es recomendable almacenar
# directamente las contraseñas dentro del código fuente.
# Lo recomendable es utilizar variables de entorno,
# archivos de configuración protegidos o un gestor de secretos.
PASSWORD = "472d6iqSz8VakpE3uME8Lywt2wquVZMa"


# Virtual Host de RabbitMQ.
#
# Un Virtual Host permite separar recursos de RabbitMQ,
# como exchanges, colas, usuarios y permisos.
VHOST = "woqbgkcj"


# Nombre del Exchange que utilizarán los diferentes
# productores y consumidores de la aplicación.
#
# Todos los procesos utilizan este mismo exchange para
# intercambiar mensajes.
EXCHANGE = "taller_2"


def get_connection():
    """
    Crea y retorna una conexión configurada con RabbitMQ.

    La función encapsula toda la lógica necesaria para
    autenticarse y establecer la comunicación con el
    servidor RabbitMQ.

    Returns:
        pika.BlockingConnection:
            Objeto que representa una conexión activa
            con el servidor RabbitMQ.
    """

    # Creamos las credenciales utilizando el usuario
    # y la contraseña configurados anteriormente.
    #
    # PlainCredentials representa autenticación mediante
    # usuario y contraseña.
    credentials = pika.PlainCredentials(
        USERNAME,
        PASSWORD
    )


    # Creamos los parámetros necesarios para establecer
    # la conexión con RabbitMQ.
    #
    # host:
    #     Servidor donde se encuentra RabbitMQ.
    #
    # port:
    #     Puerto utilizado para la comunicación.
    #
    # virtual_host:
    #     Espacio lógico de RabbitMQ que utilizaremos.
    #
    # credentials:
    #     Usuario y contraseña empleados para autenticarnos.
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=VHOST,
        credentials=credentials
    )


    # Finalmente establecemos una conexión sincrónica
    # con RabbitMQ.
    #
    # BlockingConnection permite que el programa trabaje
    # de manera sencilla y secuencial con RabbitMQ.
    #
    # La conexión creada es retornada para que otros
    # módulos puedan utilizarla.
    return pika.BlockingConnection(parameters)