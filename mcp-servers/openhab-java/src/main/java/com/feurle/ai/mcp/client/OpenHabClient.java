package com.feurle.ai.mcp.client;

import com.feurle.ai.mcp.config.OpenHabConfig;
import java.util.List;
import java.util.Map;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;

/**
 * HTTP client for communicating with the OpenHab REST API. Provides methods to query item states,
 * list all items, and send commands to devices. Uses Spring's reactive WebClient for non-blocking
 * HTTP communication.
 */
@Slf4j
@Component
public class OpenHabClient {

    private final WebClient webClient;

    /**
     * Creates an OpenHabClient with the given configuration. Initializes a WebClient with the
     * OpenHab base URL and Bearer token authentication.
     *
     * @param config the OpenHab configuration containing base URL and API token
     */
    public OpenHabClient(OpenHabConfig config) {
        // Accept/Content-Type are set per request below: the /state endpoint returns
        // text/plain and OpenHAB answers 400 if a JSON response is requested there.
        this.webClient =
                WebClient.builder()
                        .baseUrl(config.getBaseUrl())
                        .defaultHeader("Authorization", "Bearer " + config.getApiToken())
                        .build();
    }

    /**
     * Retrieves the current state of an OpenHab item.
     *
     * @param itemName the name of the item
     * @return the current state of the item (e.g., "ON", "OFF") or an error message
     */
    public String getItemState(String itemName) {
        log.info("Fetching state for item: {}", itemName);
        try {
            return webClient
                    .get()
                    .uri("/rest/items/{itemName}/state", itemName)
                    .accept(MediaType.TEXT_PLAIN)
                    .retrieve()
                    .bodyToMono(String.class)
                    .block();
        } catch (WebClientResponseException e) {
            log.error(
                    "Error fetching state for {}: {} {}",
                    itemName,
                    e.getStatusCode(),
                    e.getResponseBodyAsString());
            return "ERROR: " + e.getStatusCode() + " - " + e.getResponseBodyAsString();
        }
    }

    /**
     * Retrieves all available items from OpenHab.
     *
     * @return a list of maps containing item name, label, type, and state
     */
    public List<Map<String, Object>> getAllItems() {
        log.info("Fetching all items");
        try {
            return webClient
                    .get()
                    .uri("/rest/items?fields=name,label,type,state")
                    .accept(MediaType.APPLICATION_JSON)
                    .retrieve()
                    .bodyToFlux(Map.class)
                    .cast(Map.class)
                    .map(m -> (Map<String, Object>) m)
                    .collectList()
                    .block();
        } catch (WebClientResponseException e) {
            log.error("Error fetching all items: {}", e.getResponseBodyAsString());
            return List.of(Map.of("error", e.getResponseBodyAsString()));
        }
    }

    /**
     * Sends a command to an OpenHab item.
     *
     * @param itemName the name of the item to command
     * @param command the command to send (e.g., "ON", "OFF")
     * @return a confirmation message or error message
     */
    public String sendCommand(String itemName, String command) {
        log.info("Sending command '{}' to item: {}", command, itemName);
        try {
            webClient
                    .post()
                    .uri("/rest/items/{itemName}", itemName)
                    .contentType(MediaType.TEXT_PLAIN)
                    .bodyValue(command)
                    .retrieve()
                    .toBodilessEntity()
                    .block();
            return "OK: Command '" + command + "' sent to " + itemName;
        } catch (WebClientResponseException e) {
            log.error(
                    "Error sending command to {}: {} {}",
                    itemName,
                    e.getStatusCode(),
                    e.getResponseBodyAsString());
            return "ERROR: " + e.getStatusCode() + " - " + e.getResponseBodyAsString();
        }
    }
}
