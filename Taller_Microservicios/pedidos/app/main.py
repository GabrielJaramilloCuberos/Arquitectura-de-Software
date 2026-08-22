from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os, requests
app = FastAPI(title="Microservicio Pedidos")
PRODUCTOS_URL=os.getenv("PRODUCTOS_URL","http://localhost:8001")
NOTIFICACIONES_URL=os.getenv("NOTIFICACIONES_URL","http://localhost:8003")
class Pedido(BaseModel):
    producto_id:int
    cantidad:int
@app.post("/pedidos")
def crear(pedido:Pedido):
    r=requests.get(f"{PRODUCTOS_URL}/productos/{pedido.producto_id}",timeout=3)
    if r.status_code != 200:
        raise HTTPException(status_code=400,detail="Producto no encontrado")
    producto=r.json()
    pedido_id=1001
    try:
        requests.post(f"{NOTIFICACIONES_URL}/notificaciones",
            json={"pedido_id":pedido_id,"mensaje":f"Pedido creado para {producto['nombre']}"},
            timeout=3)
    except requests.RequestException:
        pass
    return {"pedido_id":pedido_id,"producto":producto["nombre"],
            "cantidad":pedido.cantidad,"estado":"CREADO"}