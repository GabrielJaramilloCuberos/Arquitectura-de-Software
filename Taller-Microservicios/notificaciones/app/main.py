from fastapi import FastAPI
from pydantic import BaseModel

# Aplicación ASGI del microservicio. FastAPI genera automáticamente el esquema
# OpenAPI y la interfaz Swagger disponible en /docs.
app = FastAPI(title="Microservicio Notificaciones")


class Notificacion(BaseModel):
    """Contrato JSON que Pedidos debe enviar para crear una notificación."""

    pedido_id: int
    mensaje: str


@app.post("/notificaciones")
def enviar(data: Notificacion):
    """Simula el envío de una notificación y confirma su recepción."""

    # En este ejercicio no se integra un proveedor real de correo o mensajería.
    # La salida queda en los logs del contenedor y sirve como evidencia del flujo.
    print(
        f"NOTIFICACIÓN ENVIADA - "
        f"Pedido {data.pedido_id}: {data.mensaje}"
    )

    # FastAPI serializa el diccionario como JSON con estado HTTP 200.
    return {
        "estado": "ENVIADA",
        "pedido_id": data.pedido_id
    }
