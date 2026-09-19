package com.feurle.ai.mcp.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * Configuration properties for connecting to an OpenHab instance. Properties are prefixed with
 * "openhab" and typically configured in application.yaml.
 */
@Data
@Configuration
@ConfigurationProperties(prefix = "openhab")
public class OpenHabConfig {
    /** Base URL of the OpenHab instance */
    private String baseUrl;

    /** API token for authentication with OpenHab */
    private String apiToken;
}
