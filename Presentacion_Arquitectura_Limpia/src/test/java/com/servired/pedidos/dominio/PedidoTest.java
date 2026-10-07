package com.servired.pedidos.dominio;

import org.junit.jupiter.api.Test;

import java.math.BigDecimal;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class PedidoTest {

    @Test
    void calculaElTotalAlCrearUnPedido() {
        Pedido pedido = Pedido.crear("Ana", "Café", 3, new BigDecimal("12500"));

        assertEquals(new BigDecimal("37500.00"), pedido.getTotal());
    }

    @Test
    void rechazaUnaCantidadInvalida() {
        assertThrows(IllegalArgumentException.class,
                () -> Pedido.crear("Ana", "Café", 0, new BigDecimal("12500")));
    }
}
