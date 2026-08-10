"""
Pontificia Universidad Javeriana
Autores: Gabriel Jaramillo, Guden Silva, Roberth Méndez, Luz Adriana Salazar, Jorge Olaya, Santiago Galindo
Fecha: Agosto 2026
Materia: Arquitectura de Software
Tema: RabbitMQ
Fichero: productor_radicado.py
Descripción: Recepción de alimentos ingresados por el usuario y publicación de solicitudes para su procesamiento.
"""

# Importamos json para convertir los diccionarios
# Python a mensajes en formato JSON.
import json


# Importamos la función encargada de crear
# la conexión con RabbitMQ y el nombre del exchange.
from config import get_connection, EXCHANGE


# ============================================================
# CONEXIÓN CON RABBITMQ
# ============================================================

# Establecemos la conexión con RabbitMQ.
connection = get_connection()


# Creamos un canal de comunicación.
channel = connection.channel()


# Declaramos el exchange que utilizará este productor.
#
# Se utiliza el mismo exchange que emplean
# los consumidores.
channel.exchange_declare(
    exchange=EXCHANGE,
    exchange_type="topic",
    durable=True
)


# Mostramos un mensaje inicial indicando que el productor
# está preparado para recibir alimentos.
print("📤 Productor Radicado - Escriba sus alimentos")


try:

    # Iniciamos un ciclo infinito.
    #
    # Esto permite que el usuario pueda ingresar
    # múltiples alimentos sin tener que reiniciar
    # el programa después de cada uno.
    while True:

        # Imprimimos una separación visual.
        print("\n" + "=" * 45)


        # Solicitamos al usuario el nombre del alimento.
        #
        # input() espera que el usuario escriba algo.
        #
        # strip() elimina espacios innecesarios al principio
        # y al final de la entrada.
        alimento = input(
            "🍎 Alimento: "
        ).strip()


        # Verificamos si el usuario desea terminar
        # la ejecución escribiendo "salir".
        #
        # lower() permite aceptar:
        #
        # SALIR
        # Salir
        # salir
        #
        # como la misma instrucción.
        if alimento.lower() == "salir":

            # Generamos KeyboardInterrupt manualmente
            # para reutilizar el mecanismo de cierre
            # definido más abajo.
            raise KeyboardInterrupt


        # Comprobamos si el usuario dejó el campo vacío.
        if not alimento:

            # Mostramos una advertencia.
            print(
                "⚠️  Debe ingresar un alimento.\n"
            )


            # Imprimimos nuevamente el separador.
            print("=" * 45)


            # continue hace que el programa regrese
            # directamente al comienzo del while,
            # solicitando nuevamente un alimento.
            continue


        # Construimos el mensaje que será enviado
        # al sistema de procesamiento.
        #
        # origen:
        # identifica el componente que creó el mensaje.
        #
        # alimento:
        # contiene el dato introducido por el usuario.
        #
        # contador:
        # comienza en cero porque todavía no ha pasado
        # por los consumidores del flujo.
        mensaje = {
            "origen": "Notificacion_Radicado",
            "alimento": alimento,
            "contador": 0
        }


        # Publicamos el mensaje en RabbitMQ.
        #
        # exchange:
        #     Exchange central del sistema.
        #
        # routing_key="Extraer":
        #     indica que el mensaje debe ser recibido
        #     por la cola que tenga asociada esta ruta.
        #
        # body:
        #     convertimos el diccionario a JSON.
        channel.basic_publish(
            exchange=EXCHANGE,
            routing_key="Extraer",
            body=json.dumps(mensaje)
        )


        # Informamos al usuario que el alimento
        # fue enviado correctamente.
        print(
            f"✅ Enviado a cola_extraer: "
            f"{alimento}"
        )


        # Separador visual.
        print("=" * 45)


except KeyboardInterrupt:

    # Este bloque se ejecuta cuando:
    #
    # 1. El usuario escribe "salir", o
    # 2. Presiona Ctrl + C.
    #
    # De esta forma el programa termina
    # de manera controlada.
    print("\n" + "=" * 35)
    print("👋 Cerrando productor...")
    print("=" * 35)


finally:

    # Cerramos la conexión con RabbitMQ
    # independientemente de cómo terminó el programa.
    connection.close()