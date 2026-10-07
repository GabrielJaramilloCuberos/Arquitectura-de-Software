package com.servired.pedidos.adaptadores.sql;

import com.servired.pedidos.aplicacion.PedidoRepositorio;
import com.servired.pedidos.dominio.Pedido;
import org.springframework.jdbc.core.JdbcTemplate;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

/** Adaptador que implementa el puerto de persistencia mediante SQLite. */
public final class PedidoRepositorioSql implements PedidoRepositorio {

    private final JdbcTemplate jdbc;

    public PedidoRepositorioSql(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
        inicializarBaseDeDatos();
    }

    private void inicializarBaseDeDatos() {
        jdbc.execute("""
                CREATE TABLE IF NOT EXISTS pedidos (
                    id TEXT PRIMARY KEY,
                    cliente TEXT NOT NULL,
                    producto TEXT NOT NULL,
                    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
                    precio_unitario NUMERIC NOT NULL CHECK (precio_unitario >= 0),
                    total NUMERIC NOT NULL CHECK (total >= 0),
                    fecha_creacion TEXT NOT NULL
                )
                """);
    }

    @Override
    public void guardar(Pedido pedido) {
        jdbc.update("""
                        INSERT INTO pedidos
                            (id, cliente, producto, cantidad, precio_unitario, total, fecha_creacion)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                pedido.getId().toString(),
                pedido.getCliente(),
                pedido.getProducto(),
                pedido.getCantidad(),
                pedido.getPrecioUnitario(),
                pedido.getTotal(),
                pedido.getFechaCreacion().toString());
    }

    @Override
    public List<Pedido> listar() {
        return jdbc.query("""
                        SELECT id, cliente, producto, cantidad,
                               precio_unitario, total, fecha_creacion
                        FROM pedidos
                        ORDER BY fecha_creacion DESC
                        """,
                (resultado, numeroFila) -> Pedido.restaurar(
                        UUID.fromString(resultado.getString("id")),
                        resultado.getString("cliente"),
                        resultado.getString("producto"),
                        resultado.getInt("cantidad"),
                        new BigDecimal(resultado.getString("precio_unitario")),
                        new BigDecimal(resultado.getString("total")),
                        LocalDateTime.parse(resultado.getString("fecha_creacion"))));
    }
}
