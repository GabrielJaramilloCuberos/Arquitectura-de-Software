package com.arqui.ParteA;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import java.io.InputStream;
import java.util.Properties;
import java.util.HashSet;
import java.util.Set;

import org.apache.commons.net.ftp.FTPClient;
import org.apache.commons.net.ftp.FTPFile;
import org.apache.commons.net.ftp.FTP;

/**
 * ParteA - Monitor FTP implementado "a mano" usando Apache Commons Net.
 *
 * Estrategia general:
 * 1. Se conecta una sola vez a un servidor FTP origen.
 * 2. Cada cierto intervalo (poll.interval.seconds) recorre recursivamente
 *    un directorio remoto buscando archivos.
 * 3. Cada archivo nuevo que encuentra lo descarga a una carpeta local
 *    y lo recuerda en memoria para no volver a descargarlo (evita duplicados).
 *
 * Nota: como "archivosDescargados" vive solo en memoria (un HashSet), la
 * prevención de duplicados NO sobrevive si el programa se reinicia — es una
 * limitación consciente de esta versión simple frente a la que usa una base
 * de datos persistente (H2) en el proyecto principal.
 */
public class AppA {

    // Guarda las rutas remotas de archivos ya descargados en esta ejecución,
    // para no procesarlas de nuevo en el siguiente ciclo de polling.
    private static final Set<String> archivosDescargados = new HashSet<>();

    public static void main(String[] args) throws Exception {

        // Carga todos los parámetros configurables (host, credenciales, rutas,
        // intervalo) desde un archivo externo config.properties, en vez de
        // tenerlos escritos directamente en el código (buena práctica de
        // configuración externa / separación de config y lógica).
        Properties config = cargarConfiguracion();

        String host = config.getProperty("ftp.host");
        int puerto = Integer.parseInt(config.getProperty("ftp.port"));
        String usuario = config.getProperty("ftp.user");
        String password = config.getProperty("ftp.password");
        String directorioFTP = config.getProperty("ftp.remote.directory");

        // Carpeta local donde se van a guardar las copias descargadas.
        // Se arma como <local.destination>/ParteA/CopiasA
        Path destino = Paths.get(config.getProperty("local.destination"), "ParteA", "CopiasA");

        // Cada cuántos segundos se vuelve a revisar el FTP en busca de archivos nuevos.
        int intervalo = Integer.parseInt(config.getProperty("poll.interval.seconds"));

        // Abre la conexión FTP una única vez; esa misma conexión se reutiliza
        // en todos los ciclos de polling posteriores.
        FTPClient ftp = conectarFTP(host, puerto, usuario, password);

        System.out.println("Monitoreando el FTP en " + host + ":" + puerto);

        // Arranca el bucle infinito de monitoreo.
        monitorearServidor(ftp, directorioFTP, destino, intervalo);
    }

    /**
     * Lee config.properties desde el classpath (normalmente ubicado en
     * src/main/resources) y lo carga como un objeto Properties.
     */
    private static Properties cargarConfiguracion() throws IOException {

        Properties config = new Properties();

        try (InputStream input = AppA.class.getClassLoader()
                .getResourceAsStream("config.properties")) {

            if (input == null) {
                throw new RuntimeException("No se encontró config.properties");
            }

            config.load(input);
        }

        return config;
    }

    /**
     * Crea y configura el cliente FTP:
     * - connect(): abre el socket TCP con el servidor.
     * - login(): autentica con usuario/clave.
     * - enterLocalPassiveMode(): usa modo pasivo (necesario detrás de NAT/Docker,
     *   donde el cliente no puede aceptar conexiones entrantes para el canal de datos).
     * - setFileType(BINARY_FILE_TYPE): fuerza transferencia binaria, para que
     *   PDFs/imágenes/Excel no se corrompan (el modo texto por defecto puede
     *   alterar saltos de línea en archivos binarios).
     */
    private static FTPClient conectarFTP(String host, int puerto, String usuario, String password) throws IOException {

        FTPClient ftp = new FTPClient();

        ftp.connect(host, puerto);
        ftp.login(usuario, password);
        ftp.enterLocalPassiveMode();
        ftp.setFileType(FTP.BINARY_FILE_TYPE);

        return ftp;
    }

    /**
     * Bucle principal de monitoreo: repite indefinidamente el ciclo de
     * "revisar directorio -> esperar intervalo -> revisar de nuevo".
     * Esto es polling manual, equivalente a lo que en la versión Camel
     * se logra con la opción "delay" del endpoint FTP.
     */
    private static void monitorearServidor(FTPClient ftp, String directorioFTP, Path destino, int intervalo) throws Exception {

        while (true) {

            procesarDirectorio(ftp, normalizarDirectorioFTP(directorioFTP), destino);

            // Pausa el hilo el número de segundos configurado antes del
            // siguiente ciclo de revisión.
            Thread.sleep(intervalo * 1000L);
        }
    }

    /**
     * Recorre recursivamente un directorio remoto del FTP:
     * - Si encuentra una subcarpeta, se llama a sí misma para bajar un nivel más.
     * - Si encuentra un archivo, lo manda a descargar.
     * Refleja la misma estructura de carpetas del origen en el destino local.
     */
    private static void procesarDirectorio(FTPClient ftp, String directorioFTP, Path destino) throws IOException {

        // Asegura que la carpeta local de destino exista antes de escribir en ella.
        Files.createDirectories(destino);

        // Lista todo lo que hay en el directorio remoto actual (archivos y carpetas).
        FTPFile[] entradas = ftp.listFiles(directorioFTP);

        for (FTPFile entrada : entradas) {

            // Ignora las entradas especiales "." (directorio actual) y ".."
            // (directorio padre) que algunos servidores FTP incluyen en el listado.
            if (esDirectorioEspecial(entrada)) {
                continue;
            }

            String rutaRemota = construirRutaRemota(directorioFTP, entrada.getName());

            if (entrada.isDirectory()) {
                // Recursión: baja un nivel más, y en el destino local crea
                // una subcarpeta con el mismo nombre para mantener la estructura.
                procesarDirectorio(ftp, rutaRemota, destino.resolve(entrada.getName()));
            } else if (entrada.isFile()) {
                descargarArchivo(ftp, rutaRemota, entrada.getName(), destino);
            }
        }
    }

    /**
     * Descarga un archivo remoto al destino local, solo si no fue descargado
     * antes en esta misma ejecución (control de duplicados en memoria).
     */
    private static void descargarArchivo(FTPClient ftp, String rutaRemota, String nombreArchivo, Path carpetaDestino) throws IOException {

        // Si la ruta remota ya está en el set de descargados, se omite —
        // esto es la prevención de duplicados de esta versión simple.
        if (archivosDescargados.contains(rutaRemota)) {
            return;
        }

        Path destino = carpetaDestino.resolve(nombreArchivo);

        // Crea la carpeta padre local si no existe (por si la estructura de
        // subcarpetas del FTP todavía no fue replicada localmente).
        Files.createDirectories(destino.getParent());

        // Abre un flujo de escritura local y le pide al cliente FTP que
        // descargue el contenido del archivo remoto directamente sobre ese flujo.
        try (OutputStream out = Files.newOutputStream(destino)) {

            ftp.retrieveFile(rutaRemota, out);
        }

        // Marca la ruta como ya procesada para no repetirla en próximos ciclos.
        archivosDescargados.add(rutaRemota);

        System.out.println("Descargado: " + rutaRemota);
    }

    /**
     * Normaliza la ruta del directorio FTP configurado:
     * - Si viene vacía, usa la raíz "/".
     * - Se asegura de que empiece con "/".
     * - Quita cualquier "/" sobrante al final (excepto si la ruta es solo "/").
     * Esto evita bugs por rutas mal formateadas en la configuración externa.
     */
    private static String normalizarDirectorioFTP(String directorioFTP) {

        if (directorioFTP == null || directorioFTP.isBlank()) {
            return "/";
        }

        String directorio = directorioFTP.trim();

        if (!directorio.startsWith("/")) {
            directorio = "/" + directorio;
        }

        while (directorio.endsWith("/") && directorio.length() > 1) {
            directorio = directorio.substring(0, directorio.length() - 1);
        }

        return directorio;
    }

    /**
     * Concatena el directorio actual con el nombre de una entrada (archivo o
     * carpeta) para formar la ruta remota completa, cuidando de no duplicar
     * la barra "/" cuando el directorio ya es la raíz.
     */
    private static String construirRutaRemota(String directorio, String nombre) {

        if ("/".equals(directorio)) {
            return "/" + nombre;
        }

        return directorio + "/" + nombre;
    }

    /**
     * Detecta si una entrada del listado FTP es una de las carpetas
     * especiales "." o ".." que no se deben procesar (evitan bucles infinitos
     * de recursión sobre sí mismas o el directorio padre).
     */
    private static boolean esDirectorioEspecial(FTPFile entrada) {

        String nombre = entrada.getName();

        return entrada.isDirectory() && (".".equals(nombre) || "..".equals(nombre));
    }
}
