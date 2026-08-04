package com.arqui;
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

public class App {

    private static final Set<String> archivosDescargados = new HashSet<>();

    public static void main(String[] args) throws Exception {

        Properties config = cargarConfiguracion();

        String host = config.getProperty("ftp.host");
        int puerto = Integer.parseInt(config.getProperty("ftp.port"));
        String usuario = config.getProperty("ftp.user");
        String password = config.getProperty("ftp.password");
        String directorioFTP = config.getProperty("ftp.remote.directory");
        Path destino = Paths.get(config.getProperty("local.destination"));
        int intervalo = Integer.parseInt(config.getProperty("poll.interval.seconds"));

        FTPClient ftp = conectarFTP(host, puerto, usuario, password);

        monitorearServidor(ftp, directorioFTP, destino, intervalo);
    }

    private static Properties cargarConfiguracion() throws IOException {

        Properties config = new Properties();

        try (InputStream input = App.class.getClassLoader()
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

            FTPFile[] radicados = ftp.listDirectories(directorioFTP);

            for (FTPFile carpeta : radicados) {

                procesarRadicado(ftp, carpeta, directorioFTP, destino);

            }

            Thread.sleep(intervalo * 1000L);
        }
    }

    private static void procesarRadicado(FTPClient ftp, FTPFile carpeta, String directorioFTP, Path destino) throws IOException {

        String nombreRadicado = carpeta.getName();

        String rutaRadicado = directorioFTP.endsWith("/")
                ? directorioFTP + nombreRadicado
                : directorioFTP + "/" + nombreRadicado;

        Files.createDirectories(destino.resolve(nombreRadicado));

        FTPFile[] archivos = ftp.listFiles(rutaRadicado);

        for (FTPFile archivo : archivos) {

            if (!archivo.isFile()) {
                continue;
            }

            if (archivosDescargados.contains(archivo.getName())) {
                continue;
            }

            descargarArchivo(ftp, rutaRadicado, archivo, destino.resolve(nombreRadicado));

            archivosDescargados.add(archivo.getName());
        }
    }

    private static void descargarArchivo(FTPClient ftp, String rutaRadicado, FTPFile archivo, Path carpetaDestino) throws IOException {

        Path destino = carpetaDestino.resolve(archivo.getName());

        Files.createDirectories(destino.getParent());

        try (OutputStream out = Files.newOutputStream(destino)) {

            ftp.retrieveFile(
                    rutaRadicado + "/" + archivo.getName(),
                    out);
        }

        System.out.println("Descargado: " + archivo.getName());
    }
}