from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import os
import requests

app = FastAPI(title="Microservicio Pedidos")

PRODUCTOS_URL = os.getenv(
    "PRODUCTOS_URL",
    "http://localhost:8001"
)

NOTIFICACIONES_URL = os.getenv(
    "NOTIFICACIONES_URL",
    "http://localhost:8003"
)


class Pedido(BaseModel):
    producto_id: int
    cantidad: int = Field(gt=0)


pedidos = []
pedido_actual = 1001


@app.post("/pedidos")
def crear(pedido: Pedido):
    global pedido_actual

    try:
        r = requests.get(
            f"{PRODUCTOS_URL}/productos/{pedido.producto_id}",
            timeout=3
        )
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=503,
            detail="No fue posible consultar el microservicio de Productos"
        ) from exc

    if r.status_code == 404:
        raise HTTPException(
            status_code=400,
            detail="Producto no encontrado"
        )

    if r.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Respuesta inesperada del microservicio de Productos"
        )

    producto = r.json()

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
        pass

    return pedido_creado


@app.get("/pedidos")
def consultar_pedidos():
    return pedidos


@app.get("/pedidos/{pedido_id}")
def consultar_pedido(pedido_id: int):
    for pedido in pedidos:
        if pedido["pedido_id"] == pedido_id:
            return pedido

    raise HTTPException(
        status_code=404,
        detail="Pedido no encontrado"
    )
