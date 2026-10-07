package com.servired.pedidos.aplicacion;

import com.servired.pedidos.dominio.Pedido;

import java.util.List;

/**
 * Puerto de salida. La aplicación define lo que necesita, pero no sabe
 * si la implementación utiliza SQLite, memoria u otra tecnología.
 */
public interface PedidoRepositorio {

    void guardar(Pedido pedido);

    List<Pedido> listar();
}
