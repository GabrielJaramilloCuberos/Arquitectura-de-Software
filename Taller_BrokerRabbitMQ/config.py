import pika

# ===============================
# CONFIGURACIÓN RABBITMQ
# ===============================

# RABBITMQ_HOST = "gerbil.rmq.cloudamqp.com"
# RABBITMQ_PORT = 5672
# USERNAME = "etpyjjad"
# PASSWORD = "tNhqawuyTs3W0-pOrL6WpxU1SBCNZ1hb"
# VHOST = "etpyjjad"

RABBITMQ_HOST = "gerbil-01.rmq.cloudamqp.com"
RABBITMQ_PORT = 5672
USERNAME = "vwvppvmc"
PASSWORD = "WhlRmWYYWeScxi71jSNHqEJK5H8PsB1m"
VHOST = "vwvppvmc"

EXCHANGE = "taller_exchange"

def get_connection():
    
    #Retorna una conexión configurada a RabbitMQ
    
    credentials = pika.PlainCredentials(USERNAME, PASSWORD)

    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=VHOST,
        credentials=credentials
    )

    return pika.BlockingConnection(parameters)
