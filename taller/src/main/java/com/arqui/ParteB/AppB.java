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

public class AppB {

    public static void main(String[] args) throws Exception {
        Properties config = cargarConfiguracion();

        Path destino = Paths.get(config.getProperty("local.destination"), "ParteB", "CopiasB");
        Files.createDirectories(destino);

        CamelContext contexto = new DefaultCamelContext();
        contexto.addRoutes(new RouteBuilder() {
            @Override
            public void configure() {
                from(crearEndpointFtp(config))
                        .routeId("ftp-a-directorio-local")
                        .to(crearEndpointDestino(destino))
                        .process(exchange -> imprimirArchivoDescargado(exchange));
            }
        });

        Runtime.getRuntime().addShutdownHook(new Thread(() -> detenerContexto(contexto)));

        contexto.start();
        System.out.println("Apache Camel monitoreando el FTP ");

        new CountDownLatch(1).await();
    }

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

    private static String crearEndpointFtp(Properties config) {
        String host = config.getProperty("ftp.host");
        String puerto = config.getProperty("ftp.port");
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

    private static String crearEndpointDestino(Path destino) {
        String rutaDestino = destino.toString().replace("\\", "/");
        return "file:" + rutaDestino + "?autoCreate=true&fileName=${file:name}";
    }

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

    private static String codificarParametro(String valor) {
        return URLEncoder.encode(valor, StandardCharsets.UTF_8);
    }

    private static void imprimirArchivoDescargado(Exchange exchange) {
        String archivo = exchange.getIn().getHeader(Exchange.FILE_NAME, String.class);

        if (archivo == null || archivo.isBlank()) {
            archivo = exchange.getIn().getHeader(Exchange.FILE_NAME_ONLY, String.class);
        }

        System.out.println("Descargado con Camel: " + archivo);
    }

    private static void detenerContexto(CamelContext contexto) {
        try {
            contexto.stop();
        } catch (Exception e) {
            System.err.println("No se pudo detener Camel correctamente: " + e.getMessage());
        }
    }
}
