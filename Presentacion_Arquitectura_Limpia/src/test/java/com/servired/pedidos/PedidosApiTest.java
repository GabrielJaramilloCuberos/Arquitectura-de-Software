package com.servired.pedidos;

import com.servired.pedidos.infraestructura.AplicacionPedidos;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

@SpringBootTest(
        classes = AplicacionPedidos.class,
        webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
        properties = "app.database.url=jdbc:sqlite:target/pedidos-prueba.db")
class PedidosApiTest {

    @Autowired
    private TestRestTemplate cliente;

    @Test
    void registraYListaUnPedidoMedianteHttp() {
        Map<String, Object> solicitud = Map.of(
                "cliente", "Gabriel",
                "producto", "Libro",
                "cantidad", 2,
                "precioUnitario", 45000);

        ResponseEntity<Map> creacion = cliente.postForEntity("/api/pedidos", solicitud, Map.class);
        ResponseEntity<Object[]> listado = cliente.getForEntity("/api/pedidos", Object[].class);

        assertEquals(HttpStatus.CREATED, creacion.getStatusCode());
        assertEquals(90000.0, ((Number) creacion.getBody().get("total")).doubleValue());
        assertEquals(HttpStatus.OK, listado.getStatusCode());
        assertTrue(listado.getBody().length >= 1);
    }
}
