package com.servired.pedidos.dominio;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.util.Objects;
import java.util.UUID;

/**
 * Entidad de dominio. No conoce Spring, HTTP, JDBC ni SQLite.
 */
public final class Pedido {

    private final UUID id;
    private final String cliente;
    private final String producto;
    private final int cantidad;
    private final BigDecimal precioUnitario;
    private final BigDecimal total;
    private final LocalDateTime fechaCreacion;

    private Pedido(
            UUID id,
            String cliente,
            String producto,
            int cantidad,
            BigDecimal precioUnitario,
            BigDecimal total,
            LocalDateTime fechaCreacion) {
        this.id = Objects.requireNonNull(id);
        this.cliente = validarTexto(cliente, "El cliente es obligatorio");
        this.producto = validarTexto(producto, "El producto es obligatorio");

        if (cantidad <= 0) {
            throw new IllegalArgumentException("La cantidad debe ser mayor que cero");
        }
        if (precioUnitario == null || precioUnitario.signum() < 0) {
            throw new IllegalArgumentException("El precio unitario no puede ser negativo");
        }

        this.cantidad = cantidad;
        this.precioUnitario = precioUnitario.setScale(2, RoundingMode.HALF_UP);
        this.total = Objects.requireNonNull(total).setScale(2, RoundingMode.HALF_UP);
        this.fechaCreacion = Objects.requireNonNull(fechaCreacion);
    }

    public static Pedido crear(
            String cliente,
            String producto,
            int cantidad,
            BigDecimal precioUnitario) {
        BigDecimal precioNormalizado = precioUnitario == null
                ? null
                : precioUnitario.setScale(2, RoundingMode.HALF_UP);

        if (precioNormalizado == null || precioNormalizado.signum() < 0) {
            throw new IllegalArgumentException("El precio unitario no puede ser negativo");
        }

        return new Pedido(
                UUID.randomUUID(),
                cliente,
                producto,
                cantidad,
                precioNormalizado,
                precioNormalizado.multiply(BigDecimal.valueOf(cantidad)),
                LocalDateTime.now());
    }

    /** Reconstruye una entidad previamente guardada, sin generar otro id. */
    public static Pedido restaurar(
            UUID id,
            String cliente,
            String producto,
            int cantidad,
            BigDecimal precioUnitario,
            BigDecimal total,
            LocalDateTime fechaCreacion) {
        return new Pedido(id, cliente, producto, cantidad, precioUnitario, total, fechaCreacion);
    }

    private static String validarTexto(String valor, String mensaje) {
        if (valor == null || valor.isBlank()) {
            throw new IllegalArgumentException(mensaje);
        }
        return valor.trim();
    }

    public UUID getId() {
        return id;
    }

    public String getCliente() {
        return cliente;
    }

    public String getProducto() {
        return producto;
    }

    public int getCantidad() {
        return cantidad;
    }

    public BigDecimal getPrecioUnitario() {
        return precioUnitario;
    }

    public BigDecimal getTotal() {
        return total;
    }

    public LocalDateTime getFechaCreacion() {
        return fechaCreacion;
    }
}
