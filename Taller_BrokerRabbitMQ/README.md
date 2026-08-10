# Taller Broker RabbitMQ

Taller de la materia **Arquitectura de Software** (Pontificia Universidad Javeriana) que implementa un flujo de mensajería con **RabbitMQ** usando la biblioteca `pika`. El sistema simula la recepción, normalización, clasificación y registro de alimentos radicados por un ciudadano, más un observador que monitorea todos los eventos que circulan por el exchange.

## Arquitectura del flujo

```
productor_radicado.py                         productor_formulario.py
   (routing_key="Extraer")                        (routing_key="Matriz")
          │                                                │
          ▼                                                │
  cola_extraer                                             │
          │                                                │
consumidor_extraer_texto.py                                │
   (normaliza texto)                                       │
   (routing_key="Clasificar")                              │
          │                                                │
          ▼                                                │
  cola_clasificar                                          │
          │                                                │
consumidor_clasificar_texto.py                             │
   (clasifica con alimentos.py)                            │
   (routing_key="Matriz")                                  │
          │                                                │
          ▼                                                ▼
                        cola-matriz
                            │
                            ▼
             consumidor_registrar_matriz.py
                 (guarda en SQLite: registros_procesados.db)

observador_eventos.py se suscribe a "#" (todas las routing keys)
del exchange "taller_2" y muestra en consola cada evento publicado.
```

Todos los componentes se comunican a través de un único **exchange topic** llamado `taller_2`, configurado en [config.py](config.py).

## Requisitos

- Python 3.9+
- Acceso a internet (el broker de RabbitMQ está alojado en [CloudAMQP](https://www.cloudamqp.com/), no requiere instalar RabbitMQ localmente)
- Dependencias listadas en [requirements.txt](requirements.txt)

## Instalación

1. Clonar el repositorio y ubicarse en la carpeta del taller:

   ```bash
   cd Taller_BrokerRabbitMQ
   ```

2. (Recomendado) Crear y activar un entorno virtual:

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # En Windows: venv\Scripts\activate
   ```

3. Instalar las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

> La conexión a RabbitMQ (host, usuario, contraseña y virtual host) ya está configurada en [config.py](config.py) apuntando a una instancia de CloudAMQP compartida para el taller, por lo que no es necesario levantar un servidor propio.

## Ejecución

El flujo funciona con varios procesos corriendo simultáneamente, cada uno en su propia terminal. Se recomienda el siguiente orden:

1. **Observador de eventos** (opcional, útil para ver todo el flujo en tiempo real):

   ```bash
   python observador_eventos.py
   ```

2. **Consumidores** (deben estar escuchando antes de producir mensajes, cada uno en una terminal distinta):

   ```bash
   python consumidor_extraer_texto.py
   python consumidor_clasificar_texto.py
   python consumidor_registrar_matriz.py
   ```

3. **Productores** (generan los mensajes que recorren el flujo):

   ```bash
   python productor_radicado.py
   ```

   Este productor pide por consola el nombre de un alimento (por ejemplo `manzana`, `pollo`, `zanahoria`) y lo publica hacia `cola_extraer`. Escriba `salir` o presione `Ctrl+C` para terminar.

   También puede ejecutar el productor de formulario, que publica un único evento de ejemplo directamente hacia la matriz:

   ```bash
   python productor_formulario.py
   ```

### Resultado esperado

Cada alimento ingresado en `productor_radicado.py` recorre:

1. `consumidor_extraer_texto.py` → limpia y normaliza el texto (minúsculas, sin tildes/espacios).
2. `consumidor_clasificar_texto.py` → determina la categoría del alimento usando el diccionario en [alimentos.py](alimentos.py) (Proteína, Fruta, Verdura o Desconocido).
3. `consumidor_registrar_matriz.py` → inserta el resultado final en la base de datos SQLite `registros_procesados.db` (se crea automáticamente en la primera ejecución).

Puede detener cualquier proceso con `Ctrl+C`; cada script cierra la conexión con RabbitMQ de forma controlada.

## Estructura del proyecto

| Archivo | Descripción |
|---|---|
| [config.py](config.py) | Configuración y creación de la conexión con RabbitMQ. |
| [productor_radicado.py](productor_radicado.py) | Recibe alimentos por consola y los publica en `cola_extraer`. |
| [productor_formulario.py](productor_formulario.py) | Publica un evento de ejemplo de "formulario recibido" directamente a la matriz. |
| [consumidor_extraer_texto.py](consumidor_extraer_texto.py) | Normaliza el texto del alimento recibido. |
| [consumidor_clasificar_texto.py](consumidor_clasificar_texto.py) | Clasifica el alimento según [alimentos.py](alimentos.py). |
| [consumidor_registrar_matriz.py](consumidor_registrar_matriz.py) | Persiste el resultado final en SQLite. |
| [observador_eventos.py](observador_eventos.py) | Se suscribe a todos los eventos del exchange (`routing_key="#"`) para monitoreo. |
| [alimentos.py](alimentos.py) | Diccionario de alimentos y su categoría. |
| [requirements.txt](requirements.txt) | Dependencias del proyecto (`pika`). |

## Autores

Gabriel Jaramillo, Guden Silva, Roberth Méndez, Luz Adriana Salazar, Jorge Olaya, Santiago Galindo — Pontificia Universidad Javeriana, Arquitectura de Software.
