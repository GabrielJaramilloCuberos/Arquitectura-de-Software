package com.arqui.ParteB;

import java.io.IOException;
import java.io.InputStream;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Properties;
import java.util.concurrent.CountDownLatch;

import org.apache.camel.CamelContext;
import org.apache.camel.Exchange;
import org.apache.camel.builder.RouteBuilder;
import org.apache.camel.impl.DefaultCamelContext;

/**
 * ParteB - Monitor FTP implementado con Apache Camel.
 *
 * A diferencia de AppA (que hace polling, listado recursivo y descarga a mano
 * con Apache Commons Net), aquí toda esa lógica se resume en UNA ruta Camel
 * declarativa: "escucha este FTP" -> "copia lo que llegue a esta carpeta local".
 * Camel se encarga internamente de: abrir la conexión FTP, hacer polling
 * periódico (opción "delay"), recorrer subdirectorios (opción "recursive"),
 * y evitar reprocesar archivos ya vistos (opción "idempotent").
 */
public class AppB {

    public static void main(String[] args) throws Exception {
        // Carga la configuración externa (host, credenciales, rutas, intervalo)
        // desde config.properties — mismo enfoque de configuración externa que AppA.
        Properties config = cargarConfiguracion();

        // Carpeta local donde Camel va a depositar los archivos descargados.
        Path destino = Paths.get(config.getProperty("local.destination"), "ParteB", "CopiasB");
        Files.createDirectories(destino);

        // El CamelContext es el "motor" de Camel: administra el ciclo de vida
        // de las rutas (arrancar, detener, procesar mensajes).
        CamelContext contexto = new DefaultCamelContext();

        // Se define una única ruta: de dónde vienen los datos (from) y hacia
        // dónde van (to), más un paso intermedio de procesamiento (process).
        contexto.addRoutes(new RouteBuilder() {
            @Override
            public void configure() {
                from(crearEndpointFtp(config))          // origen: el servidor FTP
                        .routeId("ftp-a-directorio-local") // nombre identificador de la ruta (útil en logs)
                        .to(crearEndpointDestino(destino)) // destino: carpeta local
                        .process(exchange -> imprimirArchivoDescargado(exchange)); // acción extra: loguear
            }
        });

        // Registra un "shutdown hook": si el proceso se cierra (Ctrl+C, kill,
        // etc.), se asegura de detener el contexto de Camel de forma ordenada
        // en vez de dejarlo cortado abruptamente.
        Runtime.getRuntime().addShutdownHook(new Thread(() -> detenerContexto(contexto)));

        // Arranca el contexto: en este momento Camel empieza a ejecutar la
        // ruta definida arriba, incluyendo el primer ciclo de polling al FTP.
        contexto.start();
        System.out.println("Apache Camel monitoreando el FTP ");

        // Mantiene vivo el hilo principal indefinidamente (CountDownLatch(1)
        // nunca llega a cero porque nadie llama a countDown()), ya que Camel
        // corre en sus propios hilos internos y si main() termina, la JVM
        // podría cerrarse y detener todo el monitoreo.
        new CountDownLatch(1).await();
    }

    /**
     * Lee config.properties desde el classpath, igual que en AppA.
     */
    private static Properties cargarConfiguracion() throws IOException {
        Properties config = new Properties();

        try (InputStream input = AppB.class.getClassLoader()
                .getResourceAsStream("config.properties")) {

            if (input == null) {
                throw new RuntimeException("No se encontro config.properties");
            }

            config.load(input);
        }

        return config;
    }

    /**
     * Construye la URI del endpoint FTP de origen que usa Camel en el "from(...)".
     * Toda la configuración de conexión y comportamiento de polling se expresa
     * como parámetros de query en la URI, en vez de código imperativo:
     *
     * - binary=true       -> transferencia en modo binario (evita corromper PDFs/imágenes).
     * - passiveMode=true  -> modo pasivo FTP (necesario detrás de NAT/Docker).
     * - recursive=true    -> Camel recorre subcarpetas automáticamente (reemplaza
     *                        la recursión manual que hace AppA en procesarDirectorio()).
     * - noop=true         -> tras leer el archivo, Camel NO lo borra ni mueve en el
     *                        origen (No-OPeration); lo deja intacto en el FTP.
     * - idempotent=true   -> Camel usa un repositorio interno para no reprocesar
     *                        el mismo archivo dos veces (equivalente al HashSet
     *                        "archivosDescargados" de AppA, pero manejado por el framework).
     * - delay=intervaloMs -> cada cuánto tiempo Camel vuelve a revisar el FTP
     *                        (equivalente al Thread.sleep(intervalo) de AppA).
     */
    private static String crearEndpointFtp(Properties config) {
        String host = config.getProperty("ftp.host");
        String puerto = config.getProperty("ftp.port");
        // Usuario y clave se codifican como parámetros de URL por si contienen
        // caracteres especiales (espacios, '@', '&', etc.) que romperían la URI.
        String usuario = codificarParametro(config.getProperty("ftp.user"));
        String password = codificarParametro(config.getProperty("ftp.password"));
        String directorio = normalizarDirectorioRemoto(config.getProperty("ftp.remote.directory"));
        long intervaloMs = Long.parseLong(config.getProperty("poll.interval.seconds")) * 1000L;

        return "ftp://" + host + ":" + puerto + directorio
                + "?username=" + usuario
                + "&password=" + password
                + "&binary=true"
                + "&passiveMode=true"
                + "&recursive=true"
                + "&noop=true"
                + "&idempotent=true"
                + "&delay=" + intervaloMs;
    }

    /**
     * Construye la URI del endpoint local que usa Camel en el "to(...)".
     * El componente "file:" de Camel escribe el mensaje recibido (el archivo
     * descargado) en el sistema de archivos local.
     *
     * - autoCreate=true          -> crea la carpeta destino si no existe.
     * - fileName=${file:name}    -> usa una expresión Simple (lenguaje propio de
     *                               Camel) para conservar el mismo nombre de
     *                               archivo que tenía en el origen.
     */
    private static String crearEndpointDestino(Path destino) {
        // Camel espera rutas con "/" incluso en Windows, por eso se reemplazan
        // las barras invertidas del Path nativo.
        String rutaDestino = destino.toString().replace("\\", "/");
        return "file:" + rutaDestino + "?autoCreate=true&fileName=${file:name}";
    }

    /**
     * Normaliza la ruta del directorio remoto configurado, igual que en AppA:
     * garantiza que empiece con "/" y no termine con "/" sobrante.
     */
    private static String normalizarDirectorioRemoto(String directorio) {
        if (directorio == null || directorio.isBlank() || "/".equals(directorio.trim())) {
            return "/";
        }

        String normalizado = directorio.trim();

        if (!normalizado.startsWith("/")) {
            normalizado = "/" + normalizado;
        }

        while (normalizado.endsWith("/") && normalizado.length() > 1) {
            normalizado = normalizado.substring(0, normalizado.length() - 1);
        }

        return normalizado;
    }

    /**
     * Codifica un valor (usuario o password) para que sea seguro incluirlo
     * dentro de una URI, escapando caracteres especiales según UTF-8.
     */
    private static String codificarParametro(String valor) {
        return URLEncoder.encode(valor, StandardCharsets.UTF_8);
    }

    /**
     * Callback que Camel ejecuta automáticamente después de cada transferencia
     * exitosa (paso .process(...) de la ruta). Aquí solo se usa para imprimir
     * en consola qué archivo se descargó, leyendo el nombre desde los headers
     * estándar que Camel agrega a todo mensaje proveniente de un endpoint de
     * archivos (Exchange.FILE_NAME / Exchange.FILE_NAME_ONLY).
     */
    private static void imprimirArchivoDescargado(Exchange exchange) {
        String archivo = exchange.getIn().getHeader(Exchange.FILE_NAME, String.class);

        if (archivo == null || archivo.isBlank()) {
            archivo = exchange.getIn().getHeader(Exchange.FILE_NAME_ONLY, String.class);
        }

        System.out.println("Descargado con Camel: " + archivo);
    }

    /**
     * Detiene el CamelContext de forma ordenada (cierra conexiones, libera
     * hilos internos). Se invoca desde el shutdown hook registrado en main().
     */
    private static void detenerContexto(CamelContext contexto) {
        try {
            contexto.stop();
        } catch (Exception e) {
            System.err.println("No se pudo detener Camel correctamente: " + e.getMessage());
        }
    }
}
