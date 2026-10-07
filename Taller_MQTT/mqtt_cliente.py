import paho.mqtt.client as mqtt

BROKER = "test.mosquitto.org"
PUERTO = 1883

# ================ FUNCIONES DE MQTT ================

# Se conecta al broker MQTT y devuelve el cliente
def conectar_mqtt(on_connect=None, on_message=None):
  cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
  if on_connect is not None:
    cliente.on_connect = on_connect
  if on_message is not None:
    cliente.on_message = on_message
  try:
    cliente.connect(BROKER, PUERTO, 60)
  except OSError as error:
    raise ConnectionError(
      f"No fue posible conectar al broker MQTT {BROKER}:{PUERTO}. "
      "Verifica la conexión a Internet, el firewall y que el broker esté disponible."
    ) from error
  return cliente

# Se suscribe a un grupo específico en el broker MQTT
def suscribir_grupo(cliente, grupo: int) -> None:
  cliente.subscribe(f"AS/G{grupo}")
  print(f"Suscrito a AS/G{grupo} en el broker MQTT {BROKER}:{PUERTO}")

# Se publica un código en un grupo específico en el broker MQTT
def publicar_codigo(cliente, grupo: int, codigo: str):
  return cliente.publish(f"AS/G{grupo}", codigo, retain=True)
