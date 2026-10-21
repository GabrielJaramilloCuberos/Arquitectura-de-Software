# Taller MQTT

## ¿Qué hace este programa?

Este taller simula una cadena de trabajo entre cinco grupos.

Cada grupo recibe un código de barras, revisa si le corresponde trabajar con él
y, si todavía faltan grupos, le suma uno al final del código y lo envía al
siguiente grupo. Cuando el código pasa por todos los grupos, el último grupo
envía el resultado por correo electrónico.

La comunicación entre grupos se hace por internet usando un servicio llamado
**broker MQTT**. Se puede entender como un buzón común:

- cada grupo tiene un buzón propio;
- un grupo deja allí el mensaje para el siguiente;
- el siguiente grupo revisa su buzón y continúa el proceso.

La forma en que cada grupo esté programado no es lo importante. Lo importante
es que todos usen los mismos nombres de buzón y envíen el código en el mismo
formato. Por eso esta implementación puede comunicarse con las implementaciones
de los demás grupos.

## Protocolo del código

Todos los grupos trabajan con un código de barras **EAN-13**. Los cinco
primeros dígitos siempre contienen una permutación aleatoria de los números
del `1` al `5`, sin repetirlos. Esa permutación define el orden en que deben
participar los grupos:

- el grupo indicado por el primer dígito inicia la cadena;
- cada grupo es responsable del dígito que corresponde a su número;
- el grupo que recibe el código incrementa en una unidad los dos últimos
  dígitos y envía el código actualizado al grupo indicado por el siguiente
  dígito;
- el grupo responsable del quinto dígito es el último de la cadena y envía el
  resultado por correo electrónico.

Por ejemplo, si los cinco primeros dígitos son `32145`, el recorrido es:

```text
grupo 3 → grupo 2 → grupo 1 → grupo 4 → grupo 5
```

El grupo 3 inicia la cadena. Después, el grupo 2 recibe el código actualizado,
vuelve a incrementar los dos últimos dígitos y lo envía al grupo 1. El grupo 5
realiza el último incremento y envía el resultado por correo.

El resto de los dígitos del EAN-13 no determina el grupo responsable. Por
consiguiente, un grupo puede implementar el proceso en un lenguaje, proyecto o
estructura interna diferente, siempre que respete este protocolo:

1. usar el mismo broker MQTT;
2. publicar el código como texto;
3. usar los buzones `AS/G1` a `AS/G5`;
4. conservar los cinco primeros dígitos como la secuencia de grupos;
5. incrementar los dos últimos dígitos antes de reenviar el código.

## Antes de empezar

Se necesita:

- Python instalado;
- conexión a internet;
- las dependencias del proyecto instaladas;
- un archivo `.env` con los datos del correo que enviará el resultado.

Desde esta carpeta, instalar las dependencias con:

```bash
pip install -r requirements.txt
```

El archivo `.env` debe tener este formato:

```env
CORREO_REMITENTE=correo.que.envia@gmail.com
CORREO_DESTINATARIO=correo.que.recibe@gmail.com
CORREO_CLAVE=clave_de_aplicacion_de_gmail
```

La clave debe ser una **contraseña de aplicación de Gmail**, no la contraseña
normal de la cuenta. El archivo `.env` es privado y no se debe compartir.

## Cómo ejecutar un grupo

El programa recibe el número del grupo como parámetro. Por ejemplo, para
ejecutar el grupo 2:

```bash
python main.py 2
```

El número debe estar entre `1` y `5`. Para ver la ayuda:

```bash
python main.py --help
```

Aunque el archivo se llama `main.py` porque así se llamó originalmente,
ahora sirve para ejecutar cualquiera de los cinco grupos.

## Cómo mostrar el proceso completo

Para ver la cadena completa, se deben abrir **cinco terminales** en esta misma
carpeta. En cada terminal se ejecuta el mismo programa con un número diferente:

```bash
python main.py 1
python main.py 2
python main.py 3
python main.py 4
python main.py 5
```

Para este caso, el código de barras es `5413212345671`. El primer dígito indica
que el recorrido comienza en el grupo 5 y después sigue este orden:
`5 → 4 → 1 → 3 → 2`.

Por eso, se recomienda abrir primero las terminales de los grupos 1, 2, 3 y 4
para que queden esperando sus mensajes. En cada una se debe esperar a ver los
mensajes `Conectado al broker` y `Suscrito a AS/G...`. Después se ejecuta el grupo 5; este
grupo lee la imagen, publica el primer mensaje y activa todo el recorrido.
También se puede iniciar todo rápidamente, siempre que el grupo 5 se ejecute
al final para comenzar la prueba.

En la pantalla se verán mensajes que indican:

- que el grupo se conectó;
- que quedó escuchando su buzón;
- que recibió un código;
- que envió el código al siguiente grupo;
- que el código llegó al final.

Como MQTT conserva el último mensaje enviado en cada buzón, si se repite una
prueba puede ser necesario limpiar los mensajes guardados ejecutando:

```bash
python eliminar_retenidos.py
```

Después de limpiarlos, se vuelven a ejecutar los cinco grupos.

## Cómo se hablan los grupos

Todos los grupos deben respetar estas reglas:

| Grupo | Buzón MQTT |
| ----- | ----------- |
| 1     | `AS/G1`   |
| 2     | `AS/G2`   |
| 3     | `AS/G3`   |
| 4     | `AS/G4`   |
| 5     | `AS/G5`   |

El mensaje que se envía es únicamente el código de barras como texto. No se
envía un objeto especial ni depende de que los demás grupos usen Python,
`paho-mqtt` o la misma estructura de archivos.

Por ejemplo, si un grupo recibe un código como `12345`, debe leer la posición
que indica el siguiente grupo, actualizar los dos últimos dígitos de acuerdo
con las reglas del taller y enviar el nuevo código al buzón correspondiente.
La implementación de cada grupo puede ser diferente, siempre que conserve:

1. los buzones `AS/G1` a `AS/G5`;
2. el código como mensaje de texto;
3. la misma regla para saber cuál es el siguiente grupo;
4. el mismo broker MQTT.

En esta implementación se usa el broker público `test.mosquitto.org`, en el
puerto `1883`. Por eso todas las implementaciones deben conectarse al mismo
broker para poder verse.

## Archivos principales

- `main.py`: inicia un grupo, recibe mensajes y envía el siguiente.
- `mqtt_cliente.py`: realiza la conexión y publica o recibe mensajes.
- `imagen.py`: lee la imagen y obtiene el código de barras.
- `correo.py`: envía por correo el código final y adjunta una imagen Code 128 con sus dígitos exactos.
- `eliminar_retenidos.py`: limpia los mensajes guardados para repetir una prueba.
- `codigo-barras-1.png`, `codigo-barras-2.png` y `codigo-barras-3.png`: casos de prueba con códigos de barras.

## Problemas comunes

### No se puede conectar

Revisar la conexión a internet y confirmar que el firewall no esté bloqueando
el puerto `1883`.

### No llega ningún mensaje

Confirmar que todos los grupos estén usando el mismo broker y los buzones
`AS/G1` a `AS/G5`. Si se está repitiendo una prueba, limpiar primero los
mensajes retenidos.

### No se puede enviar el correo

Revisar que el archivo `.env` exista, que los tres datos estén completos y que
`CORREO_CLAVE` sea una contraseña de aplicación de Gmail.
