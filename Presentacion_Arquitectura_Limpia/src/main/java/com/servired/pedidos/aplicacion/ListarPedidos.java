package com.servired.pedidos.aplicacion;

import com.servired.pedidos.dominio.Pedido;

import java.util.List;

/** Caso de uso de consulta, independiente de la base de datos. */
public final class ListarPedidos {

    private final PedidoRepositorio repositorio;

    public ListarPedidos(PedidoRepositorio repositorio) {
        this.repositorio = repositorio;
    }

    public List<Pedido> ejecutar() {
        return repositorio.listar();
    }
}
