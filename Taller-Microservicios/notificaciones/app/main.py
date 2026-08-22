from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Microservicio Notificaciones")


class Notificacion(BaseModel):
    pedido_id: int
    mensaje: str


@app.post("/notificaciones")
def enviar(data: Notificacion):

    print(
        f"NOTIFICACIÓN ENVIADA - "
        f"Pedido {data.pedido_id}: {data.mensaje}"
    )

    return {
        "estado": "ENVIADA",
        "pedido_id": data.pedido_id
    }