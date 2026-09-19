package com.feurle.ai.mcp;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;

/**
 * Main entry point for the MCP OpenHab Server application. This Spring Boot application provides a
 * Model Context Protocol (MCP) server that exposes OpenHab smart home controls as tools callable by
 * AI/LLM clients.
 */
@SpringBootApplication
@EnableConfigurationProperties
public class McpOpenhabServer {

    /**
     * Starts the MCP OpenHab Server.
     *
     * @param args command line arguments
     */
    public static void main(String[] args) {
        SpringApplication.run(McpOpenhabServer.class, args);
    }
}
