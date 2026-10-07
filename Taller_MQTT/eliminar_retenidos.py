import paho.mqtt.client as mqtt
import time


BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC_FILTER = "AS/#"

def borrarMensajeRetenido(client, userdata, message):
  if not message.retain:
      return

  client.publish(
      message.topic,
      payload="",
      qos=1,
      retain=True
  )
  print("\n" + "─" * 35)
  print(f"🧹 Mensaje retenido eliminado de {message.topic}")
  print("─" * 35)


def borrarMensajesRetenidos():
  client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
  client.on_message = borrarMensajeRetenido
  client.connect(BROKER, PORT, 60)
  client.loop_start()

  try:
      client.subscribe(TOPIC_FILTER, qos=1)
      time.sleep(3)
  finally:
      client.loop_stop()
      client.disconnect()


if __name__ == "__main__":
    borrarMensajesRetenidos()