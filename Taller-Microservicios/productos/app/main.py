from fastapi import FastAPI, HTTPException

# Instancia ASGI que Uvicorn carga desde app.main:app. El título también se
# muestra en la documentación interactiva generada por FastAPI en /docs.
app = FastAPI(title="Microservicio Productos")

# Catálogo en memoria usado para el taller. Al no existir una base de datos,
# los datos se reinician cada vez que se recrea el proceso o el Pod.
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
    """Devuelve el catálogo completo de productos disponibles."""
    return productos


@app.get("/productos/{producto_id}")
def obtener_producto(producto_id: int):
    """Busca un producto por id o responde HTTP 404 si no existe."""

    # La anotación int hace que FastAPI valide y convierta el parámetro de ruta.
    for producto in productos:
        if producto["id"] == producto_id:
            return producto

    # HTTPException permite expresar el error como una respuesta HTTP de la API.
    raise HTTPException(
        status_code=404,
        detail="Producto no encontrado"
    )
