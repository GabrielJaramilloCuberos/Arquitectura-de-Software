# https://pypi.org/project/paho-mqtt/

# ---------------PYTHON------------------------
# ---------------------------------------------
# ------------Código Suscriptor ---------------
# ---------------------------------------------


import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Conexion OK "+str(rc))
    client.subscribe("Bogota/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("test.mosquitto.org", 1883, 60)
#client.loop_forever()


---------------------------------------------
------------Código Publicador ---------------
---------------------------------------------

pip install paho-mqtt

import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("test.mosquitto.org", 1883, 60)
client.publish("Bogota/Suba","402")



--------------- Node.js----------------------
---------------------------------------------
------------Código Suscriptor ---------------
---------------------------------------------
-------------- index.js ---------------------
var mqtt = require("mqtt");
var client = mqtt.connect("mqtt://test.mosquitto.org");

function EventoConectar() {
  client.subscribe("Bogota/Suba", function (err) {
    if (!err) {
      client.publish("Bogota/Suba", "Activo");
    }
  });
}

function EventoMensaje(topic, message) {
    if (topic == "Bogota/Suba") {
      console.log("El dato recibido es " + message.toString());
    }
    console.log(topic + " - " + message.toString());
    // client.end()
  }
  
  client.on("connect", EventoConectar);
  client.on("message", EventoMensaje);

-------------- package.js ---------------------
 Incluir librería 
