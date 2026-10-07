package com.servired.pedidos.aplicacion;

import com.servired.pedidos.dominio.Pedido;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

class RegistrarPedidoTest {

    @Test
    void registraElPedidoSinNecesitarSpringNiSqlite() {
        RepositorioEnMemoria repositorio = new RepositorioEnMemoria();
        RegistrarPedido casoDeUso = new RegistrarPedido(repositorio);

        casoDeUso.ejecutar(new DatosPedido("Luis", "Pan", 2, new BigDecimal("3000")));

        assertEquals(1, repositorio.listar().size());
        assertEquals(new BigDecimal("6000.00"), repositorio.listar().get(0).getTotal());
    }

    private static final class RepositorioEnMemoria implements PedidoRepositorio {
        private final List<Pedido> pedidos = new ArrayList<>();

        @Override
        public void guardar(Pedido pedido) {
            pedidos.add(pedido);
        }

        @Override
        public List<Pedido> listar() {
            return List.copyOf(pedidos);
        }
    }
}
