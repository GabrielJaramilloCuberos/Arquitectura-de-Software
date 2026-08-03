package com.arqui;

import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.nio.file.StandardWatchEventKinds;
import java.nio.file.WatchEvent;
import java.nio.file.WatchKey;
import java.nio.file.WatchService;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;

public class App {
    private static final Path ORIGEN = Paths.get("C:\\Users\\Bastian\\Documents\\Universidad\\ARQUITECTURA DE SOFTWARE\\Arquitectura-de-Software\\ServidorFTP\\ftp-data");
    private static final Path DESTINO = Paths.get("C:\\Users\\Bastian\\Desktop\\hola2");
    private static final long ESPERA_MS = 750;

    public static void main(String[] args) throws Exception {
        Files.createDirectories(DESTINO);

        try (WatchService watchService = FileSystems.getDefault().newWatchService();
                ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor()) {

            ORIGEN.register(
                    watchService,
                    StandardWatchEventKinds.ENTRY_CREATE,
                    StandardWatchEventKinds.ENTRY_DELETE,
                    StandardWatchEventKinds.ENTRY_MODIFY);

            Map<Path, ScheduledFuture<?>> tareasPendientes = new ConcurrentHashMap<>();

            System.out.println("Monitoreando carpeta: " + ORIGEN);
            System.out.println("Copiando cambios a: " + DESTINO);

            while (true) {
                WatchKey key = watchService.take();

                for (WatchEvent<?> event : key.pollEvents()) {
                    WatchEvent.Kind<?> tipo = event.kind();

                    if (tipo == StandardWatchEventKinds.OVERFLOW) {
                        continue;
                    }

                    Path archivoRelativo = (Path) event.context();
                    Path archivoOrigen = ORIGEN.resolve(archivoRelativo);
                    Path archivoDestino = DESTINO.resolve(archivoRelativo);

                    if (tipo == StandardWatchEventKinds.ENTRY_DELETE) {
                        eliminarPendiente(tareasPendientes, archivoOrigen);
                        System.out.println("ELIMINADO -> " + archivoRelativo);
                        continue;
                    }

                    if (Files.isDirectory(archivoOrigen)) {
                        continue;
                    }

                    reprogramarCopia(scheduler, tareasPendientes, archivoOrigen, archivoDestino, archivoRelativo);
                }

                if (!key.reset()) {
                    break;
                }
            }
        }
    }

    private static void reprogramarCopia(
            ScheduledExecutorService scheduler,
            Map<Path, ScheduledFuture<?>> tareasPendientes,
            Path archivoOrigen,
            Path archivoDestino,
            Path archivoRelativo) {

        eliminarPendiente(tareasPendientes, archivoOrigen);

        ScheduledFuture<?> tarea = scheduler.schedule(
                () -> copiarArchivo(archivoOrigen, archivoDestino, archivoRelativo), ESPERA_MS, TimeUnit.MILLISECONDS);
        tareasPendientes.put(archivoOrigen, tarea);
    }

    private static void eliminarPendiente(Map<Path, ScheduledFuture<?>> tareasPendientes, Path archivoOrigen) {
        ScheduledFuture<?> tareaAnterior = tareasPendientes.remove(archivoOrigen);
        if (tareaAnterior != null) {
            tareaAnterior.cancel(false);
        }
    }

    private static void copiarArchivo(Path archivoOrigen, Path archivoDestino, Path archivoRelativo) {
        try {
            if (!Files.exists(archivoOrigen) || !Files.isRegularFile(archivoOrigen)) {
                return;
            }

            Path carpetaDestino = archivoDestino.getParent();
            if (carpetaDestino != null) {
                Files.createDirectories(carpetaDestino);
            }

            Files.copy(archivoOrigen, archivoDestino, StandardCopyOption.REPLACE_EXISTING,
                    StandardCopyOption.COPY_ATTRIBUTES);
            System.out.println("COPIADO -> " + archivoRelativo + " -> " + archivoDestino);
        } catch (IOException ex) {
            System.err.println("No se pudo copiar " + archivoRelativo + ": " + ex.getMessage());
        }
    }
}
