from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import os
import requests

# Aplicación ASGI que expone la API REST de Pedidos.
app = FastAPI(title="Microservicio Pedidos")

# Direcciones de las dependencias externas. Los valores predeterminados sirven
# para ejecución local; Kubernetes los sobrescribe mediante variables de entorno
# con los nombres DNS estables de los Services: productos y notificaciones.
PRODUCTOS_URL = os.getenv(
    "PRODUCTOS_URL",
    "http://localhost:8001"
)

NOTIFICACIONES_URL = os.getenv(
    "NOTIFICACIONES_URL",
    "http://localhost:8003"
)


class Pedido(BaseModel):
    """Contrato de entrada para solicitar la creación de un pedido."""

    producto_id: int
    # Pydantic rechaza cantidades iguales o inferiores a cero con HTTP 422.
    cantidad: int = Field(gt=0)


# Almacenamiento temporal del taller. No se comparte entre réplicas ni sobrevive
# a la recreación del proceso; en producción correspondería a una base de datos.
pedidos = []
pedido_actual = 1001


@app.post("/pedidos")
def crear(pedido: Pedido):
    """Valida el producto, registra el pedido y solicita una notificación."""

    global pedido_actual

    # Cliente HTTP síncrono hacia Productos. El timeout evita que la petición al
    # usuario quede esperando indefinidamente si la dependencia no responde.
    try:
        r = requests.get(
            f"{PRODUCTOS_URL}/productos/{pedido.producto_id}",
            timeout=3
        )
    except requests.RequestException as exc:
        # 503 comunica que Pedidos funciona, pero una dependencia no está disponible.
        raise HTTPException(
            status_code=503,
            detail="No fue posible consultar el microservicio de Productos"
        ) from exc

    if r.status_code == 404:
        # La API de Pedidos traduce el producto inexistente a una solicitud inválida.
        raise HTTPException(
            status_code=400,
            detail="Producto no encontrado"
        )

    if r.status_code != 200:
        # 502 representa una respuesta inesperada recibida desde otro servicio.
        raise HTTPException(
            status_code=502,
            detail="Respuesta inesperada del microservicio de Productos"
        )

    producto = r.json()

    # Se genera un id secuencial únicamente en memoria.
    pedido_id = pedido_actual
    pedido_actual += 1

    pedido_creado = {
        "pedido_id": pedido_id,
        "producto_id": pedido.producto_id,
        "producto": producto["nombre"],
        "cantidad": pedido.cantidad,
        "estado": "CREADO"
    }
    pedidos.append(pedido_creado)

    # La notificación es una operación de mejor esfuerzo: su falla no revierte el
    # pedido ya creado. Esto reduce el acoplamiento temporal, aunque no garantiza
    # reintentos ni entrega; un sistema real podría usar una cola de mensajes.
    try:
        requests.post(
            f"{NOTIFICACIONES_URL}/notificaciones",
            json={
                "pedido_id": pedido_id,
                "mensaje": f"Pedido creado para {producto['nombre']}"
            },
            timeout=3
        )

    except requests.RequestException:
        # Decisión deliberada del taller: conservar el pedido aunque falle la alerta.
        pass

    return pedido_creado


@app.get("/pedidos")
def consultar_pedidos():
    """Devuelve todos los pedidos conservados por esta instancia."""
    return pedidos


@app.get("/pedidos/{pedido_id}")
def consultar_pedido(pedido_id: int):
    """Devuelve un pedido por id o responde HTTP 404 si no está registrado."""

    for pedido in pedidos:
        if pedido["pedido_id"] == pedido_id:
            return pedido

    raise HTTPException(
        status_code=404,
        detail="Pedido no encontrado"
    )
