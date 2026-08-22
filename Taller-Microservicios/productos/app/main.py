from fastapi import FastAPI, HTTPException

app = FastAPI(title="Microservicio Productos")

productos = [
    {
        "id": 1,
        "nombre": "Laptop",
        "precio": 3500000,
        "disponible": True
    },
    {
        "id": 2,
        "nombre": "Monitor",
        "precio": 900000,
        "disponible": True
    },
    {
        "id": 3,
        "nombre": "Teclado",
        "precio": 150000,
        "disponible": True
    }
]


@app.get("/productos")
def obtener_productos():
    return productos


@app.get("/productos/{producto_id}")
def obtener_producto(producto_id: int):

    for producto in productos:
        if producto["id"] == producto_id:
            return producto

    raise HTTPException(
        status_code=404,
        detail="Producto no encontrado"
    )