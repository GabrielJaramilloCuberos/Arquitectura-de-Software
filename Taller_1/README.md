El taller consiste en monitorear un servidor FTP y descargar automáticamente al equipo local los archivos que se vayan agregando, implementado de dos formas distintas:

- **Parte A**: monitoreo por *polling* implementado a mano con Apache Commons Net (`FTPClient`).
- **Parte B**: misma funcionalidad implementada como una ruta de integración con **Apache Camel** (`camel-ftp` + `camel-file`).

Para mayor detalle, ingresar:
[Informe](INFORME.md)

Para reporte en PDF:
[Reporte](Jaramillo_Mendez_Olaya_Salazar_Silva_Galindo_Informe_Taller_1.pdf)

## Estructura del proyecto

```
ServidorFTP/               # docker-compose para levantar un servidor FTP de pruebas
  docker-compose.yml
  ftp-data/                # carpeta que el servidor expone como home del usuario FTP

taller/                    # proyecto Maven con el código de Parte A y Parte B
  pom.xml
  src/main/resources/config.properties
  src/main/java/com/arqui/ParteA/AppA.java
  src/main/java/com/arqui/ParteB/AppB.java
```

## Requisitos previos

- Docker y Docker Compose
- JDK 21 o superior
- Maven 3.8+

## 1. Levantar el servidor FTP

```bash
cd ServidorFTP
docker compose up -d
```

Esto levanta un contenedor `pure-ftpd` con:

- Host/puerto: `localhost:21` (modo pasivo en el rango `30000-30009`)
- Usuario: `admin`
- Contraseña: `admin123`
- Home del usuario: `/home/admin`, mapeado al volumen local `ServidorFTP/ftp-data`

Para probar la Parte A o la Parte B, copia o descarga archivos dentro de `ServidorFTP/ftp-data` (por ejemplo el archivo `Canales.mp4` ya incluido, o cualquier archivo/carpeta nuevo) y estos aparecerán en el servidor FTP.

Para detener el servidor cuando termines:

```bash
docker compose down
```

## 2. Configuración común

Ambas partes leen la misma configuración desde `taller/src/main/resources/config.properties`:

```properties
ftp.host=127.0.0.1
ftp.port=21
ftp.user=admin
ftp.password=admin123

ftp.remote.directory=/

local.destination=./Arquitectura-de-Software/taller/src/main/java/com/arqui

poll.interval.seconds=2
```

- `ftp.*`: credenciales y dirección del servidor FTP levantado en el paso anterior.
- `ftp.remote.directory`: directorio remoto a monitorear (recursivo).
- `local.destination`: carpeta base local donde se guardan las descargas. Es una **ruta relativa al directorio desde el que ejecutes el comando `mvn`/`java`**, así que ten en cuenta desde dónde corres los comandos del paso 4 o 5.
- `poll.interval.seconds`: cada cuántos segundos se revisa el FTP en busca de archivos nuevos.

Cada parte agrega su propia subcarpeta dentro de `local.destination`:

- Parte A descarga en `local.destination/ParteA/CopiasA`
- Parte B descarga en `local.destination/ParteB/CopiasB`

Si quieres cambiar dónde se guardan las descargas, edita `local.destination` antes de compilar/ejecutar.

## 3. Compilar el proyecto

```bash
cd taller
mvn clean compile
```

## 4. Ejecutar Parte A (Apache Commons Net)

Desde `taller/`, con el servidor FTP corriendo:

```bash
mvn org.codehaus.mojo:exec-maven-plugin:3.1.0:java -Dexec.mainClass="com.arqui.ParteA.AppA"
```

Qué hace: se conecta al FTP, y cada `poll.interval.seconds` segundos recorre recursivamente `ftp.remote.directory` descargando los archivos nuevos a `ParteA/CopiasA`. Por consola verás:

```
Monitoreando el FTP en 127.0.0.1:21
Descargado: /Canales.mp4
```

Para detenerlo: `Ctrl+C`.

## 5. Ejecutar Parte B (Apache Camel)

Desde `taller/`, con el servidor FTP corriendo:

```bash
mvn org.codehaus.mojo:exec-maven-plugin:3.1.0:java -Dexec.mainClass="com.arqui.ParteB.AppB"
```

Qué hace: levanta un `CamelContext` con una ruta `ftp://... -> file:...` que hace polling del mismo directorio remoto (usando `delay` en milisegundos, calculado a partir de `poll.interval.seconds`) y copia los archivos nuevos a `ParteB/CopiasB`. Por consola verás:

```
Apache Camel monitoreando el FTP 
Descargado con Camel: Canales.mp4
```

Para detenerlo: `Ctrl+C` (la ruta de Camel se detiene correctamente gracias al shutdown hook).

## Alternativa sin exec-maven-plugin

Si `exec-maven-plugin` no puede descargarse (por ejemplo, sin acceso a Maven Central en ese momento) puedes compilar y correr manualmente con el classpath de Maven:

```bash
cd taller
mvn clean compile dependency:build-classpath -Dmdep.outputFile=cp.txt

# macOS/Linux
java -cp "target/classes:$(cat cp.txt)" com.arqui.ParteA.AppA
java -cp "target/classes:$(cat cp.txt)" com.arqui.ParteB.AppB

# Windows (PowerShell)
java -cp "target\classes;$(Get-Content cp.txt)" com.arqui.ParteA.AppA
java -cp "target\classes;$(Get-Content cp.txt)" com.arqui.ParteB.AppB
```
