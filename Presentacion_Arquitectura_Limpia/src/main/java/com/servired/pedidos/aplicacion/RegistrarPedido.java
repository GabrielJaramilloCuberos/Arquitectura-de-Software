package com.servired.pedidos.aplicacion;

import com.servired.pedidos.dominio.Pedido;

/** Caso de uso para crear y persistir un pedido. */
public final class RegistrarPedido {

    private final PedidoRepositorio repositorio;

    public RegistrarPedido(PedidoRepositorio repositorio) {
        this.repositorio = repositorio;
    }

    public Pedido ejecutar(DatosPedido datos) {
        Pedido pedido = Pedido.crear(
                datos.cliente(),
                datos.producto(),
                datos.cantidad(),
                datos.precioUnitario());
        repositorio.guardar(pedido);
        return pedido;
    }
}
