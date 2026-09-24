package com.personalfinance;

import static org.assertj.core.api.Assertions.assertThat;

import tools.jackson.databind.JsonNode;
import tools.jackson.databind.ObjectMapper;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

/**
 * Prova a ligação entre aplicação e banco: o endpoint só responde "no ar" com um Postgres
 * de verdade atendendo (ADR-0014).
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class HealthEndpointTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:18-alpine");

    @LocalServerPort
    int porta;

    @Test
    void reportaAplicacaoEBancoNoAr() throws Exception {
        HttpResponse<String> resposta = HttpClient.newHttpClient()
                .send(HttpRequest.newBuilder(URI.create("http://localhost:" + porta + "/api/health")).build(),
                        HttpResponse.BodyHandlers.ofString());

        assertThat(resposta.statusCode()).isEqualTo(200);
        JsonNode corpo = new ObjectMapper().readTree(resposta.body());
        assertThat(corpo.get("status").asText()).isEqualTo("UP");
        assertThat(corpo.path("components").path("db").path("status").asText()).isEqualTo("UP");
    }
}
