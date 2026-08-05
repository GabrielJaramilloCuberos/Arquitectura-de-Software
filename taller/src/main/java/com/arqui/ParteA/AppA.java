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

public class AppA {

    private static final Set<String> archivosDescargados = new HashSet<>();

    public static void main(String[] args) throws Exception {

        Properties config = cargarConfiguracion();

        String host = config.getProperty("ftp.host");
        int puerto = Integer.parseInt(config.getProperty("ftp.port"));
        String usuario = config.getProperty("ftp.user");
        String password = config.getProperty("ftp.password");
        String directorioFTP = config.getProperty("ftp.remote.directory");
        Path destino = Paths.get(config.getProperty("local.destination"), "ParteA", "CopiasA");
        int intervalo = Integer.parseInt(config.getProperty("poll.interval.seconds"));

        FTPClient ftp = conectarFTP(host, puerto, usuario, password);

        System.out.println("Monitoreando el FTP en " + host + ":" + puerto);

        monitorearServidor(ftp, directorioFTP, destino, intervalo);
    }

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

    private static FTPClient conectarFTP(String host, int puerto, String usuario, String password) throws IOException {

        FTPClient ftp = new FTPClient();

        ftp.connect(host, puerto);
        ftp.login(usuario, password);
        ftp.enterLocalPassiveMode();
        ftp.setFileType(FTP.BINARY_FILE_TYPE);

        return ftp;
    }

    private static void monitorearServidor(FTPClient ftp, String directorioFTP, Path destino, int intervalo) throws Exception {

        while (true) {

            procesarDirectorio(ftp, normalizarDirectorioFTP(directorioFTP), destino);

            Thread.sleep(intervalo * 1000L);
        }
    }

    private static void procesarDirectorio(FTPClient ftp, String directorioFTP, Path destino) throws IOException {

        Files.createDirectories(destino);

        FTPFile[] entradas = ftp.listFiles(directorioFTP);

        for (FTPFile entrada : entradas) {

            if (esDirectorioEspecial(entrada)) {
                continue;
            }

            String rutaRemota = construirRutaRemota(directorioFTP, entrada.getName());

            if (entrada.isDirectory()) {
                procesarDirectorio(ftp, rutaRemota, destino.resolve(entrada.getName()));
            } else if (entrada.isFile()) {
                descargarArchivo(ftp, rutaRemota, entrada.getName(), destino);
            }
        }
    }

    private static void descargarArchivo(FTPClient ftp, String rutaRemota, String nombreArchivo, Path carpetaDestino) throws IOException {

        if (archivosDescargados.contains(rutaRemota)) {
            return;
        }

        Path destino = carpetaDestino.resolve(nombreArchivo);

        Files.createDirectories(destino.getParent());

        try (OutputStream out = Files.newOutputStream(destino)) {

            ftp.retrieveFile(rutaRemota, out);
        }

        archivosDescargados.add(rutaRemota);

        System.out.println("Descargado: " + rutaRemota);
    }

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

    private static String construirRutaRemota(String directorio, String nombre) {

        if ("/".equals(directorio)) {
            return "/" + nombre;
        }

        return directorio + "/" + nombre;
    }

    private static boolean esDirectorioEspecial(FTPFile entrada) {

        String nombre = entrada.getName();

        return entrada.isDirectory() && (".".equals(nombre) || "..".equals(nombre));
    }
}
