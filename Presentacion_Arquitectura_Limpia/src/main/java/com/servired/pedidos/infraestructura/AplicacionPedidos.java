package com.servired.pedidos.infraestructura;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication(scanBasePackages = "com.servired.pedidos")
public class AplicacionPedidos {

    public static void main(String[] args) {
        SpringApplication.run(AplicacionPedidos.class, args);
    }
}
