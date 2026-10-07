package com.servired.pedidos.infraestructura;

import com.servired.pedidos.adaptadores.sql.PedidoRepositorioSql;
import com.servired.pedidos.aplicacion.ListarPedidos;
import com.servired.pedidos.aplicacion.PedidoRepositorio;
import com.servired.pedidos.aplicacion.RegistrarPedido;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.jdbc.core.JdbcTemplate;
import org.sqlite.SQLiteDataSource;

import javax.sql.DataSource;

/**
 * Esta es la capa externa que conecta los casos de uso con Spring y SQLite.
 */
@Configuration
public class ConfiguracionSpring {

    @Bean
    DataSource dataSource(@Value("${app.database.url}") String url) {
        SQLiteDataSource dataSource = new SQLiteDataSource();
        dataSource.setUrl(url);
        return dataSource;
    }

    @Bean
    JdbcTemplate jdbcTemplate(DataSource dataSource) {
        return new JdbcTemplate(dataSource);
    }

    @Bean
    PedidoRepositorio pedidoRepositorio(JdbcTemplate jdbcTemplate) {
        return new PedidoRepositorioSql(jdbcTemplate);
    }

    @Bean
    RegistrarPedido registrarPedido(PedidoRepositorio repositorio) {
        return new RegistrarPedido(repositorio);
    }

    @Bean
    ListarPedidos listarPedidos(PedidoRepositorio repositorio) {
        return new ListarPedidos(repositorio);
    }
}
