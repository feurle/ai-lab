package com.feurle.ai.mcp.config;

import com.feurle.ai.mcp.tools.OpenHabTools;
import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.ai.tool.method.MethodToolCallbackProvider;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Configuration for the MCP server that registers OpenHab tools. Exposes OpenHabTools methods as
 * callable tools for MCP clients.
 */
@Configuration
public class McpServerConfig {

    /**
     * Creates a ToolCallbackProvider that registers all @Tool-annotated methods in OpenHabTools.
     *
     * @param tools the OpenHabTools service containing the tool methods
     * @return a ToolCallbackProvider for the MCP framework
     */
    @Bean
    public ToolCallbackProvider openHabToolCallbackProvider(OpenHabTools tools) {
        return MethodToolCallbackProvider.builder().toolObjects(tools).build();
    }
}
