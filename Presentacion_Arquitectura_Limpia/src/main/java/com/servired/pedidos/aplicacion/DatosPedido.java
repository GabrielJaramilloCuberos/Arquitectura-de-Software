package com.servired.pedidos.aplicacion;

import java.math.BigDecimal;

/** Datos que necesita el caso de uso para registrar un pedido. */
public record DatosPedido(
        String cliente,
        String producto,
        int cantidad,
        BigDecimal precioUnitario) {
}
