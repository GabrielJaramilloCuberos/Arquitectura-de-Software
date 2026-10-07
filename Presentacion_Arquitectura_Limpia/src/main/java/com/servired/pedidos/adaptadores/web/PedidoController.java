package com.servired.pedidos.adaptadores.web;

import com.servired.pedidos.aplicacion.DatosPedido;
import com.servired.pedidos.aplicacion.ListarPedidos;
import com.servired.pedidos.aplicacion.RegistrarPedido;
import com.servired.pedidos.dominio.Pedido;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

/** Adaptador de entrada HTTP. Traduce JSON a los datos del caso de uso. */
@RestController
@RequestMapping("/api/pedidos")
public final class PedidoController {

    private final RegistrarPedido registrarPedido;
    private final ListarPedidos listarPedidos;

    public PedidoController(RegistrarPedido registrarPedido, ListarPedidos listarPedidos) {
        this.registrarPedido = registrarPedido;
        this.listarPedidos = listarPedidos;
    }

    @PostMapping
    public ResponseEntity<Pedido> registrar(@RequestBody CrearPedidoRequest request) {
        Pedido pedido = registrarPedido.ejecutar(new DatosPedido(
                request.cliente(),
                request.producto(),
                request.cantidad(),
                request.precioUnitario()));
        return ResponseEntity.status(HttpStatus.CREATED).body(pedido);
    }

    @GetMapping
    public List<Pedido> listar() {
        return listarPedidos.ejecutar();
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<Map<String, String>> manejarDatosInvalidos(IllegalArgumentException error) {
        return ResponseEntity.badRequest().body(Map.of("error", error.getMessage()));
    }

    public record CrearPedidoRequest(
            String cliente,
            String producto,
            int cantidad,
            BigDecimal precioUnitario) {
    }
}
