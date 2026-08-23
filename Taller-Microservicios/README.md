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
8. [Repositorio Git, ejecución y anexos](#8-repositorio-git-ejecución-y-anexos)

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

## 2.1 Diagrama de contexto de alto nivel - C4 Nivel 1
El usuario o evaluador interactúa con el sistema mediante Postman u otro cliente HTTP. El sistema comprende los tres microservicios y la infraestructura de ejecución proporcionada por Kubernetes.

```
C4Context
    title Nivel 1 C4 - Contexto del MiniSistema de Pedidos

    Person(usuario, "Usuario / Evaluador", "Prueba la API mediante Postman o un cliente HTTP")
    System(sistema, "MiniSistema de Pedidos", "Gestiona productos, pedidos y notificaciones mediante microservicios")
    System_Ext(kubernetes, "Plataforma Kubernetes", "Orquesta contenedores, red interna, réplicas y recuperación")

    Rel(usuario, sistema, "Crea y consulta pedidos", "HTTP/JSON")
    Rel(kubernetes, sistema, "Ejecuta y supervisa", "Deployments, Services y Pods")
```
Kubernetes funciona como plataforma de soporte y no como parte de la lógica de negocio. Para las pruebas desde el equipo local se utiliza `kubectl port-forward`, permitiendo acceder al microservicio Pedidos desde el host.

## 2.2 Diagrama de contenedores / arquitectura lógica - C4 Nivel 2
La solución separa tres capacidades de negocio. Cada microservicio es una aplicación FastAPI independiente, empaquetada en una imagen Docker y ejecutada mediante Uvicorn en el puerto interno `8000`.

```
C4Container
    title Nivel 2 C4 - Contenedores del MiniSistema de Pedidos

    Person(usuario, "Usuario / Postman", "Consume la API REST")

    System_Boundary(sistema, "MiniSistema de Pedidos") {
        Container(pedidos, "Microservicio Pedidos", "Python 3.12, FastAPI, Uvicorn", "Crea y consulta pedidos; coordina Productos y Notificaciones; puerto 8000")
        Container(productos, "Microservicio Productos", "Python 3.12, FastAPI, Uvicorn", "Publica el catálogo y consulta por id; puerto 8000")
        Container(notificaciones, "Microservicio Notificaciones", "Python 3.12, FastAPI, Uvicorn", "Simula el envío de alertas y lo registra en logs; puerto 8000")
    }

    Rel(usuario, pedidos, "POST/GET /pedidos", "HTTP/JSON")
    Rel(pedidos, productos, "GET /productos/{id}", "HTTP/JSON, productos:8000")
    Rel(pedidos, notificaciones, "POST /notificaciones", "HTTP/JSON, notificaciones:8000")
```

### Responsabilidades e interfaces
MicroservicioResponsabilidadEndpointsDependenciasProductosMantener y consultar el catálogo en memoria`GET /productos`, `GET /productos/{producto_id}`NingunaPedidosValidar productos, crear y consultar pedidos y coordinar la alerta`POST /pedidos`, `GET /pedidos`, `GET /pedidos/{pedido_id}`Productos y NotificacionesNotificacionesRecibir y simular el envío de una notificación`POST /notificaciones`NingunaEl acoplamiento entre servicios se limita a contratos HTTP/JSON y nombres DNS. No se comparte memoria, código de ejecución ni almacenamiento.

Sin embargo, existe acoplamiento de contrato y temporal entre Pedidos y Productos, ya que Pedidos conoce la estructura de la respuesta de Productos y realiza llamadas síncronas.

## 2.3 Diagrama de componentes de Pedidos - C4 Nivel 3
Los siguientes componentes representan responsabilidades lógicas identificadas dentro de `pedidos/app/main.py`. No implican necesariamente que cada componente corresponda a un archivo separado.

```
C4Component
    title Nivel 3 C4 - Componentes internos del microservicio Pedidos

    Container_Boundary(pedidos, "Microservicio Pedidos - app/main.py") {
        Component(api, "Aplicación FastAPI", "FastAPI", "Registra rutas, genera OpenAPI y transforma entradas/salidas HTTP")
        Component(modelo, "Modelo Pedido", "Pydantic BaseModel", "Valida producto_id y cantidad mayor que cero")
        Component(controlador_crear, "Controlador crear pedido", "POST /pedidos", "Orquesta validación, creación y notificación")
        Component(controlador_consultar, "Controladores de consulta", "GET /pedidos y GET /pedidos/{id}", "Consulta el almacenamiento local")
        Component(repositorio, "Repositorio en memoria", "Lista Python + contador", "Conserva pedidos e ids durante la vida del proceso")
        Component(cliente_productos, "Cliente HTTP de Productos", "requests.get", "Consulta el producto y controla timeout/errores")
        Component(cliente_notificaciones, "Cliente HTTP de Notificaciones", "requests.post", "Solicita una alerta sin bloquear la creación ante fallos")
        Component(configuracion, "Configuración de endpoints", "Variables de entorno", "Resuelve PRODUCTOS_URL y NOTIFICACIONES_URL")
    }

    Container_Ext(productos, "Microservicio Productos", "FastAPI", "Catálogo")
    Container_Ext(notificaciones, "Microservicio Notificaciones", "FastAPI", "Alertas")

    Rel(api, modelo, "Valida cuerpo JSON con")
    Rel(api, controlador_crear, "Delega POST /pedidos")
    Rel(api, controlador_consultar, "Delega peticiones GET")
    Rel(controlador_crear, cliente_productos, "Consulta producto")
    Rel(controlador_crear, repositorio, "Agrega pedido y obtiene id")
    Rel(controlador_crear, cliente_notificaciones, "Solicita alerta")
    Rel(controlador_consultar, repositorio, "Lee pedidos")
    Rel(configuracion, cliente_productos, "Proporciona URL")
    Rel(configuracion, cliente_notificaciones, "Proporciona URL")
    Rel(cliente_productos, productos, "GET /productos/{id}", "HTTP/JSON")
    Rel(cliente_notificaciones, notificaciones, "POST /notificaciones", "HTTP/JSON")
```

### Flujo de creación de un pedido

```
sequenceDiagram
    actor U as Usuario / Postman
    participant P as Pedidos
    participant PR as Service productos
    participant N as Service notificaciones

    U->>P: POST /pedidos {producto_id, cantidad}
    P->>PR: GET /productos/{producto_id}

    alt Producto válido
        PR-->>P: 200 + producto
        P->>P: Generar id y guardar en memoria
        P->>N: POST /notificaciones

        alt Notificación disponible
            N-->>P: 200 ENVIADA
        else Notificación falla o vence timeout
            P->>P: Conservar pedido sin revertirlo
        end

        P-->>U: Pedido CREADO

    else Producto inexistente
        PR-->>P: 404
        P-->>U: 400 Producto no encontrado

    else Productos no disponible
        P-->>U: 503 Dependencia no disponible
    end
```

## 2.4 Diagrama físico y de despliegue
La arquitectura de despliegue utiliza Services de tipo `ClusterIP` para proporcionar direcciones estables dentro del clúster. Productos puede ejecutarse con tres réplicas para demostrar escalamiento horizontal y balanceo de carga.

```
flowchart TB
    host["Máquina host<br/>Postman<br/>localhost:8002"]

    subgraph cluster["Clúster Kubernetes local"]
        dns["DNS interno de Kubernetes<br/>productos / pedidos / notificaciones"]

        subgraph nodo["Nodo Kubernetes - Docker Desktop"]
            svcPedidos["Service pedidos<br/>ClusterIP :8000"]
            podPedidos["Pod Pedidos<br/>micro-pedidos:1.0<br/>containerPort 8000"]

            svcProductos["Service productos<br/>ClusterIP :8000"]
            podProd1["Pod Productos 1<br/>containerPort 8000"]
            podProd2["Pod Productos 2<br/>containerPort 8000"]
            podProd3["Pod Productos 3<br/>containerPort 8000"]

            svcNotif["Service notificaciones<br/>ClusterIP :8000"]
            podNotif["Pod Notificaciones<br/>micro-notificaciones:1.0<br/>containerPort 8000"]
        end
    end

    host -->|"kubectl port-forward<br/>8002:8000"| svcPedidos
    svcPedidos --> podPedidos
    podPedidos -->|"http://productos:8000"| svcProductos
    svcProductos --> podProd1
    svcProductos --> podProd2
    svcProductos --> podProd3
    podPedidos -->|"http://notificaciones:8000"| svcNotif
    svcNotif --> podNotif
    dns -.-> svcPedidos
    dns -.-> svcProductos
    dns -.-> svcNotif
```

### Mapeo físico
ElementoCantidad objetivoPuertoFunciónDeployment Productos1No aplicaMantiene el estado deseado de tres PodsPods Productos38000Atienden consultas del catálogoService Productos18000 → 8000DNS estable y balanceo entre réplicasDeployment Pedidos1No aplicaMantiene un Pod de coordinaciónPod Pedidos18000Atiende la API principalService Pedidos18000 → 8000Punto estable para acceder al PodDeployment Notificaciones1No aplicaMantiene un Pod de notificaciónPod Notificaciones18000Recibe y registra alertasService Notificaciones18000 → 8000Nombre DNS estable para PedidosPort-forwardTemporal8002 → 8000Conecta el host con Service Pedidos
---

# 3. Implementación de los microservicios e integración

## 3.1 Microservicio Productos
El microservicio **Productos** es responsable de mantener y consultar el catálogo de productos. El almacenamiento utilizado es una estructura en memoria, por lo que los datos permanecen disponibles mientras el proceso esté activo.

Endpoints principales:

MétodoEndpointDescripciónGET`/productos`Retorna todos los productosGET`/productos/{producto_id}`Consulta un producto por identificadorCuando se solicita un producto inexistente, el servicio responde con **HTTP 404 Not Found**.

La documentación de la API se genera automáticamente mediante FastAPI y puede consultarse desde el endpoint `/docs`.

## 3.2 Microservicio Pedidos
**Pedidos** actúa como coordinador del caso de uso principal. Recibe una solicitud, valida su contenido mediante Pydantic, consulta el microservicio Productos para comprobar que el producto exista, registra temporalmente el pedido y solicita el envío de una notificación.

Endpoints:

MétodoEndpointDescripciónPOST`/pedidos`Crea un pedidoGET`/pedidos`Consulta todos los pedidosGET`/pedidos/{pedido_id}`Consulta un pedido específicoLa integración con Productos es síncrona. Si Productos no está disponible, Pedidos responde con **HTTP 503 Service Unavailable**. Si Notificaciones falla, el pedido no se revierte: la excepción se captura y el pedido permanece creado.

## 3.3 Microservicio Notificaciones
**Notificaciones** recibe solicitudes mediante `POST /notificaciones` y simula el envío de una alerta.

El envío no utiliza un proveedor externo. La actividad se registra en los logs del servicio, permitiendo comprobar que Pedidos realizó correctamente la solicitud de notificación.

## 3.4 Flujo de integración entre servicios
El flujo principal es:

```
Usuario / Postman
        |
        v
   Microservicio
      Pedidos
        |
        | GET /productos/{id}
        v
   Microservicio
     Productos
        |
        | 200 OK
        v
   Microservicio
      Pedidos
        |
        | POST /notificaciones
        v
   Microservicio
   Notificaciones
        |
        v
   Pedido creado
```
En el caso exitoso, Pedidos recibe la solicitud, valida el producto, crea el pedido en memoria y solicita una notificación.

<<<<<<< HEAD
En caso de que el producto no exista, se evita crear el pedido. En caso de que Productos no esté disponible, se retorna un error controlado. Si Notificaciones falla, el pedido permanece creado.
=======
El flujo de integración conecta las tres capacidades mediante llamadas HTTP/JSON
síncronas y Service Discovery por DNS interno de Kubernetes. Ningún microservicio
conoce direcciones IP de Pods: `pedidos` resuelve a los otros dos únicamente por
el nombre estable de su Service (`productos`, `notificaciones`), inyectado por las
variables de entorno `PRODUCTOS_URL` y `NOTIFICACIONES_URL` definidas en
`k8s/pedidos.yaml`.

**Secuencia de comunicación HTTP:**

1. El usuario (Postman) envía `POST /pedidos` al Service `pedidos`, expuesto en
   el host mediante `kubectl port-forward service/pedidos 8002:8000`.
2. `pedidos/app/main.py` valida el cuerpo con Pydantic (`producto_id`,
   `cantidad > 0`) y realiza `GET http://productos:8000/productos/{producto_id}`
   con un timeout de 3 segundos.
   - Si Productos no responde (excepción de red), Pedidos devuelve `503` sin
     llegar a crear el pedido.
   - Si Productos responde `404`, Pedidos traduce el error a `400 Producto no
     encontrado`.
   - Con `200`, Pedidos toma el nombre del producto y continúa el flujo.
3. Pedidos genera un `pedido_id` secuencial en memoria y guarda el pedido con
   estado `CREADO`.
4. Pedidos realiza `POST http://notificaciones:8000/notificaciones` con
   `{pedido_id, mensaje}`, también con timeout de 3 segundos.
   - Notificaciones registra el mensaje en su salida estándar (`print`) y
     responde `200 {"estado": "ENVIADA", "pedido_id": ...}`.
   - Esta llamada es de mejor esfuerzo: si falla o vence el timeout, la
     excepción se captura y se descarta (`except requests.RequestException:
     pass`). El pedido ya creado en el paso 3 **no se revierte**. Es una
     decisión deliberada del taller para desacoplar temporalmente la creación
     del pedido de la disponibilidad de Notificaciones, a costa de no
     garantizar la entrega de la alerta (sin reintentos ni cola de mensajes).
5. Pedidos responde al usuario con el pedido creado, independientemente del
   resultado del paso 4.

Este acoplamiento es exclusivamente de contrato HTTP/JSON y de nombre DNS: los
tres servicios corren en procesos, imágenes y Pods independientes, y ninguno
comparte memoria ni almacenamiento con los demás. El diagrama de secuencia
completo, incluidas las rutas alternativas de error, está en la
[sección 2.3](#23-diagrama-de-componentes-de-pedidos---c4-nivel-3).

**Prueba de extremo a extremo (crear pedido → notificar):**

Procedimiento reproducible para generar la evidencia de esta sección:

```powershell
kubectl apply -f k8s/productos.yaml
kubectl apply -f k8s/pedidos.yaml
kubectl apply -f k8s/notificaciones.yaml
kubectl get pods
kubectl port-forward service/pedidos 8002:8000
```

En otra terminal, seguir los logs de Notificaciones en tiempo real:

```powershell
kubectl logs -f deployment/notificaciones
```

Desde Postman, enviar `POST http://localhost:8002/pedidos` con cuerpo
`{"producto_id": 1, "cantidad": 2}`. El log del contenedor de Notificaciones
debe mostrar `NOTIFICACIÓN ENVIADA - Pedido <id>: Pedido creado para <producto>`
en el mismo instante en que Postman recibe la respuesta `200` de Pedidos.

**Pendiente de validación:** insertar la captura de pantalla de `kubectl logs -f`
junto a la petición de Postman correspondiente, y confirmar que el `pedido_id`
mostrado en el log coincide con el de la respuesta HTTP recibida por el usuario.
>>>>>>> 7dbf2dbb5fd75be074fc607dc4a5adcdbeca5a18

---

# 4. Contenerización con Docker
Cada microservicio dispone de un Dockerfile independiente basado en `python:3.12-slim`.

El proceso de construcción sigue la misma idea para los tres servicios:

1. Utilizar una imagen base de Python.
2. Copiar el archivo de dependencias.
3. Instalar las dependencias.
4. Copiar el código fuente.
5. Ejecutar Uvicorn sobre `0.0.0.0:8000`.

## 4.1 Construcción de imágenes
Desde la raíz del proyecto se pueden construir las imágenes con:

```
docker build -t micro-productos:1.0 ./productos
docker build -t micro-pedidos:1.0 ./pedidos
docker build -t micro-notificaciones:1.0 ./notificaciones
```
Verificación de las imágenes:

```
docker images
```
Las tres imágenes esperadas son:

```
micro-productos:1.0
micro-pedidos:1.0
micro-notificaciones:1.0
```

## 4.2 Ejecución local
La ejecución local de los contenedores requiere configurar las variables de entorno de Pedidos para que conozca las direcciones de Productos y Notificaciones.

En Kubernetes estas direcciones se resuelven mediante los Services:

```
PRODUCTOS_URL=http://productos:8000
NOTIFICACIONES_URL=http://notificaciones:8000
```
Las imágenes se encuentran preparadas para ejecutar Uvicorn en:

```
0.0.0.0:8000
```

> **Nota:** Los comandos de ejecución local exactos dependen del mapeo de puertos utilizado en la ejecución final del equipo. No se deben inventar puertos distintos a los documentados por el despliegue real.

---

# 5. Despliegue, Service Discovery y escalabilidad en Kubernetes

## 5.1 Aplicación de los manifiestos
Los microservicios se despliegan mediante manifiestos YAML.

```
kubectl apply -f k8s/productos.yaml
kubectl apply -f k8s/pedidos.yaml
kubectl apply -f k8s/notificaciones.yaml
```
Para comprobar el despliegue:

```
kubectl get deployments
kubectl get replicasets
kubectl get pods
kubectl get services
```
El objetivo es disponer de un Deployment por microservicio y de un Service que proporcione un punto de acceso estable dentro del clúster.

## 5.2 Service Discovery mediante DNS interno
Pedidos no necesita conocer las IP de los Pods de Productos o Notificaciones. En su lugar utiliza nombres de Service:

```
PRODUCTOS_URL=http://productos:8000
NOTIFICACIONES_URL=http://notificaciones:8000
```
Kubernetes proporciona resolución DNS para estos nombres. El Service recibe las solicitudes y las dirige hacia los Pods que cumplen con su selector.

Esto permite que los Pods sean eliminados y recreados sin que Pedidos tenga que actualizar sus direcciones.

## 5.3 Acceso desde la máquina host
El Service de Pedidos es interno al clúster. Para realizar las pruebas desde Postman se utiliza un port-forward:

```
kubectl port-forward service/pedidos 8002:8000
```
Después de establecer el túnel, las pruebas pueden realizarse desde:

```
http://localhost:8002
```
Por ejemplo:

```
GET http://localhost:8002/pedidos
```

## 5.4 Escalabilidad horizontal de Productos
Para demostrar el escalamiento horizontal se utilizan tres réplicas:

```
kubectl scale deployment productos --replicas=3
```
La cantidad de Pods puede comprobarse mediante:

```
kubectl get pods -l app=productos
```
Kubernetes crea tres instancias del microservicio Productos. El Service `productos` mantiene un único punto lógico de acceso y distribuye las solicitudes entre las réplicas disponibles.

El escalamiento es independiente: solamente Productos aumenta su número de instancias, sin necesidad de replicar Pedidos o Notificaciones.

## 5.5 Balanceo de carga
El Service de Productos utiliza las etiquetas de los Pods para identificar las réplicas disponibles.

Conceptualmente:

```
                     +--> Pod Productos 1
                     |
Pedidos --> Service -+--> Pod Productos 2
                     |
                     +--> Pod Productos 3
```

De esta manera, Pedidos solamente necesita conocer:

```
http://productos:8000
```
y no las direcciones IP individuales de los Pods.

## 5.6 Recuperación ante la eliminación de un Pod
Para probar la autorrecuperación se elimina deliberadamente un Pod:

```
kubectl delete pod <nombre-del-pod>
```
Posteriormente:

```
kubectl get pods
```
El Deployment mantiene el estado deseado mediante su ReplicaSet. Si se configuraron tres réplicas y una es eliminada, Kubernetes detecta la diferencia entre el estado deseado y el estado real y crea un nuevo Pod.

El flujo puede resumirse como:

```
Deployment
    |
    v
ReplicaSet
    |
    +--> Pod 1
    +--> Pod 2
    +--> Pod 3
```
Si se elimina Pod 2:

```
Deployment
    |
    v
ReplicaSet
    |
    +--> Pod 1
    +--> Pod 3
    +--> Nuevo Pod
```
Esto demuestra la capacidad de **self-healing** de Kubernetes.

---

# 6. Estrategia y resultados de pruebas
Las pruebas se enfocaron en validar los endpoints REST, la integración entre microservicios, la documentación Swagger y el comportamiento de Kubernetes frente al escalamiento y los fallos.

## 6.1 Matriz de pruebas
IDCasoAcciónResultado esperadoResultado observadoP01Swagger ProductosAbrir `/docs`Swagger carga correctamenteCorrectoP02Swagger PedidosAbrir `/docs`Swagger carga correctamenteCorrectoP03Swagger NotificacionesAbrir `/docs`Swagger carga correctamenteCorrectoP04Consultar Productos`GET /productos``200 OK` con productosCorrectoP05Consultar Producto`GET /productos/{id}``200 OK` con productoCorrectoP06Crear Pedido`POST /pedidos``200 OK`, pedido creadoCorrectoP07Consultar Pedidos`GET /pedidos``200 OK` con pedidosCorrectoP08Consultar Pedido`GET /pedidos/{id}``200 OK` con pedidoCorrectoP09Producto inexistente`POST /pedidos` con `producto_id` inexistenteError controlado`404 Not Found` desde Productos y respuesta de validación en PedidosP10Productos no disponibleCrear pedido con Productos detenido`503 Service Unavailable`CorrectoP11EscalamientoEscalar Productos a 3 réplicas3 Pods activosCorrectoP12RecuperaciónEliminar un PodKubernetes crea un reemplazoCorrecto
## 6.2 Documentación Swagger
Cada microservicio expone documentación mediante `/docs`.

### Productos

```
GET /productos
GET /productos/{producto_id}
```
La documentación permite consultar los endpoints y probar las operaciones de la API.

### Pedidos

```
POST /pedidos
GET /pedidos
GET /pedidos/{pedido_id}
```

### Notificaciones

```
POST /notificaciones
```
La documentación Swagger fue utilizada para comprobar que los servicios se encontraban disponibles y que sus endpoints estaban registrados correctamente.

## 6.3 Pruebas REST de Productos

### Consultar todos los productos

```
GET /productos
```
**Resultado esperado:** `200 OK` con el catálogo de productos.

**Resultado obtenido:** la consulta respondió correctamente con el listado disponible.

### Consultar producto por ID

```
GET /productos/{id}
```
**Resultado esperado:** `200 OK` con el producto solicitado.

**Resultado obtenido:** el producto solicitado fue retornado correctamente.

## 6.4 Pruebas REST de Pedidos

### Crear pedido

```
POST /pedidos
```
**Resultado esperado:** creación del pedido y respuesta `200 OK`.

**Resultado obtenido:** el pedido fue creado correctamente y quedó en estado `CREADO`.

### Consultar pedidos

```
GET /pedidos
```
**Resultado esperado:** `200 OK` con los pedidos existentes.

**Resultado obtenido:** se obtuvo el listado de pedidos, incluyendo el pedido creado.

### Consultar pedido por ID

```
GET /pedidos/{id}
```
**Resultado esperado:** `200 OK` con el pedido solicitado.

**Resultado obtenido:** el pedido fue consultado correctamente.

### Crear pedido con producto inexistente

```
POST /pedidos
```
Utilizando un `producto_id` que no existe.

**Resultado esperado:** el sistema debe impedir la creación del pedido y reportar el problema con el producto.

**Resultado obtenido:** se recibió una respuesta de error indicando que el producto no fue encontrado.

## 6.5 Prueba de falla de Productos
Para evaluar el comportamiento ante fallos se detuvo un Pod del microservicio Productos y posteriormente se intentó crear un pedido.

```
Usuario
   |
   v
Pedidos
   |
   X
Productos no disponible
```
El microservicio Pedidos controla el error de comunicación y retorna:

```
503 Service Unavailable
```
Esto demuestra que la indisponibilidad de una dependencia no produce una caída completa del proceso de Pedidos.

## 6.6 Prueba de escalamiento
Se ejecutó:

```
kubectl scale deployment productos --replicas=3
```
Después se verificaron los Pods:

```
kubectl get pods -l app=productos
```
El resultado esperado es contar con tres Pods activos del microservicio Productos.

## 6.7 Prueba de recuperación
Después de disponer de tres réplicas se eliminó deliberadamente una:

```
kubectl delete pod <nombre-del-pod>
```
Kubernetes creó automáticamente un nuevo Pod para volver al número deseado de réplicas.

Esto demuestra:

- Supervisión del estado deseado.
- Recuperación automática.
- Uso de ReplicaSet.
- Mantenimiento del número de réplicas.
- Aislamiento del fallo de un Pod.

---

# 7. Análisis arquitectónico comparativo

## 7.1 Del monolito a los microservicios
Una versión monolítica del MiniSistema de Pedidos agruparía Productos, Pedidos y Notificaciones dentro de un único proceso y una única unidad de despliegue.

Esta opción sería razonable para un sistema pequeño porque requiere menos infraestructura, simplifica las pruebas locales y evita costos asociados a la comunicación por red.

La solución desarrollada en el taller divide la aplicación alrededor de tres capacidades:

- **Productos:** catálogo.
- **Pedidos:** coordinación del caso de uso.
- **Notificaciones:** simulación de alertas.
Cada capacidad tiene su propia API, imagen, proceso y ciclo de despliegue.

Esta separación reduce el acoplamiento interno del código y permite modificar o escalar una capacidad de manera independiente. Sin embargo, también introduce complejidad de red, despliegue, configuración, observabilidad y manejo de errores distribuidos.

## 7.2 Consumo de memoria
Un monolito normalmente ejecutaría un solo intérprete de Python, una instancia de Uvicorn y una copia de las bibliotecas compartidas.

La arquitectura distribuida utiliza varios Pods. En la arquitectura objetivo se tienen:

- 3 Pods de Productos.
- 1 Pod de Pedidos.
- 1 Pod de Notificaciones.
Cada proceso mantiene su propio intérprete, dependencias y memoria de trabajo. Además, Docker Desktop y Kubernetes requieren recursos adicionales.

Por esta razón, para este sistema pequeño es razonable esperar un consumo de memoria superior al de un monolito equivalente.

No se presentan cifras de memoria inventadas. Una medición empírica debería realizarse mediante:

```
kubectl top pods
```
si el clúster dispone de Metrics Server o de un mecanismo equivalente.

## 7.3 Aislamiento y propagación de fallos
En un monolito, un error grave o una presión extrema de memoria puede afectar simultáneamente a todas las capacidades porque comparten el mismo proceso.

Los microservicios proporcionan aislamiento de proceso y despliegue. La caída de un Pod de Productos no finaliza automáticamente los Pods de Pedidos o Notificaciones.

Además, Kubernetes puede recrear el Pod perdido mediante el Deployment y el ReplicaSet.

Sin embargo, el aislamiento técnico no elimina la propagación funcional.

Pedidos necesita una respuesta válida de Productos para crear un pedido. Si Productos está indisponible, Pedidos responde:

```
503 Service Unavailable
```
En cambio, una falla de Notificaciones se tolera y el pedido permanece creado.

Esto evidencia dos políticas diferentes:

DependenciaPolítica ante falloProductosLa operación de creación falla de forma controladaNotificacionesEl pedido permanece creado aunque falle la notificación
## 7.4 Limitaciones de resiliencia
La implementación actual tiene varias limitaciones:

- Las llamadas entre servicios son síncronas.
- No existen reintentos automáticos.
- No existe circuit breaker.
- No existe una cola persistente.
- Los pedidos se almacenan únicamente en memoria.
- Si un Pod de Pedidos se reinicia, se pierde el estado local.
- Si Pedidos se replicara, cada réplica podría mantener un estado diferente.
Por tanto, aunque Kubernetes mejora el aislamiento y la recuperación de infraestructura, la solución todavía no proporciona persistencia ni entrega confiable de notificaciones.

## 7.5 Costos operativos de infraestructura
El monolito ofrece una operación sencilla:

- Una construcción.
- Un despliegue.
- Un conjunto de logs.
- Menos puntos de fallo.
- Menor complejidad de red.
Los microservicios requieren:

- Tres Dockerfiles.
- Tres imágenes.
- Manifiestos independientes.
- Configuración de red.
- DNS interno.
- Administración de réplicas.
- Observabilidad distribuida.
- Diagnóstico de fallos.
Kubernetes añade Deployments, ReplicaSets, Pods, Services y procedimientos de operación.

A cambio, la plataforma proporciona automatización para recuperación, balanceo y escalamiento.

## 7.6 Comparación resumida
AtributoMonolitoMicroservicios del tallerUnidad de despliegueUna aplicaciónTres imágenes y DeploymentsComunicación internaLlamadas en procesoHTTP/JSON y DNS de ServicesMemoria baseMenorMayor por procesos, réplicas y KubernetesEscalamientoReplica toda la aplicaciónPuede escalar solo ProductosAislamiento técnicoMenorSeparación por Pod y servicioPropagación funcionalDirecta dentro del procesoDepende de timeouts y políticasRecuperaciónReinicio de la aplicaciónDeployment recrea PodsPersistencia actualPuede centralizarse fácilmenteEl estado en memoria se pierdeOperaciónMás sencillaMayor complejidadConveniencia para este casoAdecuado si permanece pequeñoÚtil para demostrar autonomía y escalamiento
## 7.7 Conclusión
La arquitectura de microservicios no es automáticamente superior al monolito.

Para el tamaño actual del MiniSistema de Pedidos, una arquitectura monolítica probablemente sería más económica en memoria y operación. Sin embargo, la solución distribuida resulta útil cuando Productos necesita escalar independientemente, las capacidades evolucionan a ritmos diferentes o el aislamiento y la recuperación justifican la complejidad adicional de Kubernetes.

La decisión arquitectónica debe basarse en requisitos de calidad, carga, disponibilidad, autonomía y capacidad operativa, y no solamente en la disponibilidad de Docker o Kubernetes.

---

... (file truncated for brevity in tool output)