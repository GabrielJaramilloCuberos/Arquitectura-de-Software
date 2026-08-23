# Taller 3: Arquitectura de Microservicios con Docker y Kubernetes
**Integrantes:** Santiago Galindo, Roberth Méndez, Gabriel Jaramillo Cuberos, Jorge Enrique Olaya, Luz Adriana Salazar, Guden Sebastin Silva Rojas
**Universidad:** Pontificia Universidad Javeriana

---

## Contenido

1. [Introducción y descripción del problema](#1-introducción-y-descripción-del-problema)
2. [Vistas y diagramas de arquitectura](#2-vistas-y-diagramas-de-arquitectura)
3. [Implementación de los microservicios e integración](#3-implementación-de-los-microservicios-e-integración)
4. [Contenerización con Docker](#4-contenerización-con-docker)
5. [Despliegue, Service Discovery y escalabilidad en Kubernetes](#5-despliegue-service-discovery-y-escalabilidad-en-kubernetes)
6. [Estrategia y resultados de pruebas](#6-estrategia-y-resultados-de-pruebas)
7. [Análisis arquitectónico comparativo](#7-análisis-arquitectónico-comparativo)
8. [Repositorio, ejecución y anexos](#8-repositorio-ejecución-y-anexos)

---

# 1. Introducción y descripción del problema
El taller consiste en transformar conceptualmente un sistema monolítico de pedidos en una arquitectura basada en microservicios, utilizando **FastAPI, Docker y Kubernetes**. El sistema se divide en tres capacidades independientes: **Productos, Pedidos y Notificaciones**.

La solución permite consultar un catálogo de productos, crear pedidos asociados a productos existentes y simular el envío de notificaciones. Cada capacidad se implementa como un microservicio independiente, con su propia aplicación FastAPI, imagen Docker y ciclo de despliegue.

El propósito arquitectónico del ejercicio es observar las ventajas y costos de separar una aplicación en servicios independientes. En particular, se busca demostrar comunicación HTTP/REST entre servicios, descubrimiento mediante DNS de Kubernetes, escalamiento horizontal, balanceo de carga y recuperación automática ante fallos.

La arquitectura no utiliza una base de datos ni servicios externos reales. El almacenamiento de productos y pedidos se mantiene temporalmente en memoria, mientras que el envío de notificaciones se simula mediante registros en los logs del contenedor.

## 1.1 Objetivo general
Implementar y desplegar un MiniSistema de Pedidos basado en microservicios independientes, utilizando FastAPI para las APIs, Docker para la contenerización y Kubernetes para la orquestación, con el fin de analizar aspectos de integración, escalabilidad, disponibilidad y resiliencia de una arquitectura distribuida.

## 1.2 Objetivos específicos

- Implementar los microservicios de **Productos, Pedidos y Notificaciones** utilizando FastAPI.
- Exponer los recursos de cada microservicio mediante APIs REST.
- Contenerizar cada servicio mediante imágenes Docker independientes.
- Configurar la comunicación entre microservicios mediante HTTP/JSON.
- Utilizar Services y DNS interno de Kubernetes para evitar depender de las IP dinámicas de los Pods.
- Desplegar los microservicios mediante Deployments y Pods.
- Escalar horizontalmente el microservicio de Productos.
- Comprobar el balanceo de solicitudes entre réplicas.
- Simular la eliminación de un Pod y verificar la autorrecuperación proporcionada por Kubernetes.
- Validar el comportamiento del sistema ante la indisponibilidad del microservicio Productos.
- Comparar la arquitectura de microservicios con una alternativa monolítica.

## 1.3 Alcance
La solución cubre:

- Consulta del catálogo de productos.
- Consulta de un producto por identificador.
- Creación de pedidos.
- Consulta de todos los pedidos.
- Consulta de un pedido por identificador.
- Validación de la existencia de un producto antes de crear un pedido.
- Simulación del envío de notificaciones.
- Despliegue mediante Docker y Kubernetes.
- Service Discovery mediante DNS interno.
- Escalamiento horizontal de Productos.
- Recuperación automática de Pods.
El ejercicio **no incluye**:

- Base de datos persistente.
- Autenticación o autorización.
- API Gateway.
- Mensajería asíncrona.
- Proveedores reales de correo o notificaciones.
- Persistencia distribuida de pedidos.

---

# 2. Vistas y diagramas de arquitectura
(Diagrama C4 contextos y contenedores — mantenidos como en la versión de diseño del taller.)

Se incluyen los diagramas de contexto (Nivel 1), contenedores (Nivel 2) y
componentes de `pedidos` (Nivel 3) para mostrar responsabilidades y dependencias.

---

# 3. Implementación de los microservicios e integración

Carpeta principal del código en este repositorio:

```
Taller-Microservicios/
├── productos/
│   ├── app/
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── pedidos/
│   ├── app/
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── notificaciones/
│   ├── app/
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
└── k8s/
    ├── productos.yaml
    ├── pedidos.yaml
    └── notificaciones.yaml
```

## 3.1 Microservicio Productos
- Código: `productos/app/main.py`.
- Endpoints: `GET /productos`, `GET /productos/{producto_id}`.
- Respuesta 404 para producto inexistente.

Ejemplo de respuesta:

```
GET /productos/1
{
  "id": 1,
  "nombre": "Laptop",
  "precio": 3500000,
  "disponible": true
}
```

## 3.2 Microservicio Pedidos
- Código: `pedidos/app/main.py`.
- Endpoints: `POST /pedidos`, `GET /pedidos`, `GET /pedidos/{pedido_id}`.
- Validación con Pydantic: `cantidad > 0`.
- Consultas a `PRODUCTOS_URL` y notificaciones a `NOTIFICACIONES_URL`.

Ejemplo de request/response `POST /pedidos`:

Request:

```
POST /pedidos
{
  "producto_id": 1,
  "cantidad": 2
}
```

Response:

```
{
  "pedido_id": 1001,
  "producto_id": 1,
  "producto": "Laptop",
  "cantidad": 2,
  "estado": "CREADO"
}
```

## 3.3 Microservicio Notificaciones
- Código: `notificaciones/app/main.py`.
- Endpoint: `POST /notificaciones`.
- Simula el envío mediante `print()` en logs y responde `{"estado":"ENVIADA","pedido_id":...}`.

## 3.4 Flujo de integración
Resumen:

1. Cliente → `POST /pedidos` a `pedidos` (host vía port-forward).
2. `pedidos` valida y realiza `GET http://productos:8000/productos/{id}` (timeout 3s).
   - Si la llamada falla por red → `503`.
   - Si responde `404` → `400 Producto no encontrado`.
3. Si `200`, `pedidos` crea `pedido_id` en memoria y guarda el pedido.
4. `pedidos` hace `POST http://notificaciones:8000/notificaciones` (timeout 3s)
   - Llamada de mejor esfuerzo; si falla no revierte el pedido.
5. `pedidos` responde al cliente con el pedido creado.

Prueba E2E reproducible (ver sección 8 para comandos exactos y checklist).

---

# 4. Contenerización con Docker
Cada servicio incluye un `Dockerfile` equivalente; plantilla común:

```
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Comandos de construcción (desde la raíz):

```bash
docker build -t micro-productos:1.0 ./productos
docker build -t micro-pedidos:1.0 ./pedidos
docker build -t micro-notificaciones:1.0 ./notificaciones
```

Ejecutar contenedores localmente (ejemplo de mapeo de puertos para pruebas sin k8s):

```bash
docker run --rm -p 8001:8000 micro-productos:1.0   # productos en localhost:8001
docker run --rm -p 8003:8000 micro-notificaciones:1.0 # notificaciones en localhost:8003
docker run --rm -p 8000:8000 micro-pedidos:1.0     # pedidos apunta por defecto a localhost:8001 y 8003
```

---

# 5. Manifiestos Kubernetes (resumen)
Los manifiestos están en `k8s/`. Cada archivo define un `Deployment` y un `Service`.

Resumen `productos.yaml`:

- `apiVersion: apps/v1`, `kind: Deployment`.
- `spec.replicas`: número de réplicas (por defecto en el repo: 1).
- `spec.template.spec.containers[]`: imagen `micro-productos:1.0`, `containerPort: 8000`.
- `Service` tipo `ClusterIP` que expone `port: 8000` → `targetPort: 8000`.

`pedidos.yaml` incluye además variables de entorno inyectadas al contenedor:

```yaml
env:
  - name: PRODUCTOS_URL
    value: "http://productos:8000"
  - name: NOTIFICACIONES_URL
    value: "http://notificaciones:8000"
```

Esto permite resolver `productos` y `notificaciones` por nombre DNS interno.

Si se desea demostrar escalado para `productos`, actualizar `replicas` a 3
o escalar en runtime:

```bash
kubectl scale deployment productos --replicas=3
```

---

# 6. Requisitos y versiones recomendadas
- Docker Desktop (con Kubernetes habilitado).
- `kubectl` (CLI).
- Python 3.12 (para ejecución local sin contenedores).
- Postman o `curl`.
- Git.

Comprobaciones básicas:

```bash
docker --version
kubectl version --client
python --version
```

Versiones efectivas usadas en desarrollo (ejemplos, confirmen en su entorno):

| Herramienta | Versión ejemplo |
|---|---|
| Python | 3.12 |
| FastAPI | (según requirements.txt) |
| Uvicorn | (según requirements.txt) |
| Docker | >=20.x |
| Kubernetes | compatible con Docker Desktop |

---

# 7. Ejecución completa (paso a paso reproducible)

1. Clonar el repositorio:

```bash
git clone <URL_DEL_REPOSITORIO>
cd Taller-Microservicios
```

2. Construir imágenes Docker (opcional si usas las imágenes locales):

```bash
docker build -t micro-productos:1.0 ./productos
docker build -t micro-pedidos:1.0 ./pedidos
docker build -t micro-notificaciones:1.0 ./notificaciones
```

3. Habilitar Kubernetes en Docker Desktop y verificar nodos:

```bash
kubectl get nodes
```

4. Aplicar manifiestos en el clúster:

```bash
kubectl apply -f k8s/productos.yaml
kubectl apply -f k8s/pedidos.yaml
kubectl apply -f k8s/notificaciones.yaml
kubectl get pods
kubectl get services
```

5. (Opcional) Escalar `productos` a 3 réplicas para pruebas de balanceo:

```bash
kubectl scale deployment productos --replicas=3
kubectl get pods -l app=productos
```

6. Abrir acceso desde el host hacia `pedidos`:

```bash
kubectl port-forward service/pedidos 8002:8000
```

7. Probar endpoints desde Postman o `curl`:

```bash
curl http://localhost:8002/productos
curl http://localhost:8002/pedidos
curl -X POST http://localhost:8002/pedidos -H "Content-Type: application/json" -d '{"producto_id":1,"cantidad":2}'
```

8. Ver logs de notificaciones para comprobar envío simulado:

```bash
kubectl logs -f deployment/notificaciones
```

---

# 8. Contratos de API y códigos HTTP
Contrato `POST /pedidos` (request):

```
{
  "producto_id": int,
  "cantidad": int (>0)
}
```

Response exitoso:

```
{
  "pedido_id": int,
  "producto_id": int,
  "producto": string,
  "cantidad": int,
  "estado": "CREADO"
}
```

Tabla rápida de códigos HTTP

| Servicio | Situación | Código |
|---|---:|---:|
| Productos | Consulta exitosa | 200 |
| Productos | Producto inexistente | 404 |
| Pedidos | Pedido creado | 200 |
| Pedidos | Producto inexistente | 400 |
| Pedidos | Productos no disponible | 503 |
| Pedidos | Pedido no encontrado | 404 |
| Notificaciones | Notificación enviada | 200 |
| FastAPI | Body inválido / validación | 422 |

---

# 9. Evidencias, observabilidad y diagnóstico
Checklist de evidencias (añadir capturas/archivos en el anexo):

- `docker images` mostrando las tres imágenes construidas.
- `kubectl get pods` y `kubectl get services` mostrando los recursos.
- Captura de `kubectl get pods -l app=productos` con 3 réplicas (si se escala).
- `kubectl delete pod <pod>` y `kubectl get pods` mostrando el reemplazo.
- Captura de `/docs` de Productos, Pedidos y Notificaciones.
- Petición `POST /pedidos` en Postman y respuesta `200`.
- `kubectl logs deployment/notificaciones` mostrando la notificación.
- Captura de `kubectl describe pod <pod>` si hubo errores.

Comandos útiles para diagnóstico:

```bash
kubectl get pods -o wide
kubectl describe pod <pod>
kubectl logs <pod>
kubectl logs deployment/notificaciones
kubectl get events
```

Nota sobre comprobación de balanceo: para demostrar que las réplicas responden
distinto, se puede modificar temporalmente `productos` para devolver su hostname
en la respuesta JSON y hacer múltiples `GET` para observar pods distintos.

---

# 10. Health checks y readiness (mejora recomendada)
Recomendación: añadir endpoints simples como `GET /health` o `GET /ready` y
configurar `livenessProbe` y `readinessProbe` en los manifiestos Kubernetes.
Ejemplo (esquema):

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

Si no se implementan estos endpoints, incluir como trabajo futuro en el informe.

---

# 11. Seguridad y alcance
La solución **no** implementa autenticación, autorización, TLS o gestión de
secretos. Esta decisión es deliberada por alcance del taller: el objetivo es
practicar arquitectura, contenerización y orquestación. En produccion sería
necesario añadir:

- Autenticación/Autorización (JWT/OAuth2).
- Gestión de secretos (SealedSecrets, Vault).
- TLS en Ingress o en los servicios.

---

# 12. Implementado vs Diseñado vs Trabajo futuro

Implementado y verificado en código:
- Endpoints y lógica en `productos/app/main.py`, `pedidos/app/main.py`, `notificaciones/app/main.py`.
- Dockerfiles y `requirements.txt` para cada servicio.
- Manifiestos básicos `k8s/*.yaml` con `Deployments` y `Services`.

Diseñado pero parcialmente evidenciado:
- Escalamiento de `productos` a 3 réplicas (manifiesto original tiene `replicas: 1`, se puede escalar con `kubectl scale`).
- Pruebas de balanceo (requiere evidencia adicional para demostrar respuesta desde varias réplicas).

Trabajo futuro / mejoras sugeridas:
- Health checks (`/health`, `/ready`) y probes en YAML.
- Persistencia de pedidos (DB) y cola para notificaciones (RabbitMQ/Kafka).
- Reintentos, circuit breaker y observabilidad (Prometheus/Grafana).
- Autenticación y gestión de secretos.

---

# 13. Anexos y evidencias (qué adjuntar)

Colocar en la carpeta `anexos/` o en el entregable:

- Capturas de `docker images`.
- Export de la colección Postman (si se incluye).
- Capturas de `/docs` para cada servicio.
- Capturas de `kubectl get pods`, `kubectl get svc` y `kubectl get deployments`.
- Capturas de `kubectl logs deployment/notificaciones` durante la prueba E2E.
- Registro de comandos utilizados y salida relevante.

---

# Estado final y nota al revisor
He resuelto el conflicto de merge que aparecía anteriormente en la sección
de flujo de integración y he añadido las secciones prácticas solicitadas: estructura del
repositorio, prerequisitos, pasos reproducibles, resumen de manifiestos, contratos
de API, tabla de códigos HTTP, observabilidad, recomendaciones de health checks,
consideraciones de seguridad y checklist de evidencias.

Por favor indique cuál de las acciones siguientes desea que ejecute ahora:

1. Generar y añadir la colección Postman con ejemplos (`GET /productos`, `POST /pedidos`, etc.).
2. Actualizar `k8s/productos.yaml` a `replicas: 3` y aplicar los manifiestos en el clúster local (lo haré sólo si confirma).
3. Ejecutar los servicios localmente y capturar Swagger/logs para añadir evidencias.

Si confirma la opción 2 o 3, procederé y adjuntaré las evidencias en `anexos/`.
