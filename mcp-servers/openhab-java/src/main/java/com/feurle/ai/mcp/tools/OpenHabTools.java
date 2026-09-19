package com.feurle.ai.mcp.tools;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.feurle.ai.mcp.client.OpenHabClient;
import java.util.List;
import java.util.Map;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Service;

/**
 * MCP tools for controlling OpenHab smart home devices. These methods are exposed as callable tools
 * to AI/LLM clients and handle item state queries, discovery, and command execution.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class OpenHabTools {

    private final OpenHabClient openHabClient;
    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Gets the current state of an OpenHab item.
     *
     * @param itemName the name of the item (case-sensitive)
     * @return a formatted string showing the item name and its current state
     */
    @Tool(
            description =
                    """
            Get the current state of an OpenHAB item by its name.
            Returns the current state as a string (e.g. "ON", "OFF").
            Use this before sending a command to check the current state.
            Example item names: 'LivingRoom_Light', 'Kitchen_Switch'.
            """)
    public String getItemState(
            @ToolParam(description = "The exact name of the OpenHAB item (case-sensitive)")
                    String itemName) {
        String state = openHabClient.getItemState(itemName);
        log.info(">>> Tool getItemState({}) = {}", itemName, state);
        return String.format("Item '%s' is currently: %s", itemName, state);
    }

    /**
     * Lists all available items from OpenHab with their current state.
     *
     * @return a JSON string containing all items with their properties
     */
    @Tool(
            description =
                    """
            List all available OpenHAB items with their name, label, type and current state.
            Use this tool first when the user asks about their smart home devices,
            to discover which items exist and what their names are.
            """)
    public String getAllItems() {
        List<Map<String, Object>> items = openHabClient.getAllItems();
        log.info(">>> Tool getAllItems() returned {} items", items.size());
        try {
            return objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(items);
        } catch (Exception e) {
            return items.toString();
        }
    }

    /**
     * Sends a command to turn an OpenHab switch ON or OFF.
     *
     * @param itemName the name of the switch item
     * @param command the command to send ("ON" or "OFF")
     * @return a confirmation or error message
     */
    @Tool(
            description =
                    """
            Send a command to an OpenHAB Switch item to turn it ON or OFF.
            Use 'ON' to turn the switch on and 'OFF' to turn it off.
            Always use getAllItems first if you don't know the exact item name.
            """)
    public String turnSwitch(
            @ToolParam(description = "The exact name of the Switch item (case-sensitive)")
                    String itemName,
            @ToolParam(description = "The command to send: must be exactly 'ON' or 'OFF'")
                    String command) {
        // Validation — only ON/OFF is allowed for switches
        String normalizedCommand = command.trim().toUpperCase();
        if (!normalizedCommand.equals("ON") && !normalizedCommand.equals("OFF")) {
            return "ERROR: Invalid command '"
                    + command
                    + "'. Only 'ON' or 'OFF' are allowed for Switch items.";
        }

        String result = openHabClient.sendCommand(itemName, normalizedCommand);
        log.info(">>> Tool turnSwitch({}, {}) = {}", itemName, normalizedCommand, result);
        return result;
    }

    /**
     * Toggles an OpenHab switch: if it's ON, turns it OFF; if it's OFF, turns it ON.
     *
     * @param itemName the name of the switch item
     * @return a confirmation message showing the state change
     */
    @Tool(
            description =
                    """
            Toggle an OpenHAB Switch item: if it's ON turn it OFF, if it's OFF turn it ON.
            Use this when the user says 'toggle', 'flip', or 'switch' without specifying on or off.
            """)
    public String toggleSwitch(
            @ToolParam(description = "The exact name of the Switch item (case-sensitive)")
                    String itemName) {
        // fetch actual state
        String currentState = openHabClient.getItemState(itemName);

        if (currentState.contains("ERROR")) {
            return "Could not toggle: " + currentState;
        }

        // send the opposite
        String newCommand = currentState.trim().equals("ON") ? "OFF" : "ON";
        String result = openHabClient.sendCommand(itemName, newCommand);
        log.info(">>> Tool toggleSwitch({}) {} -> {}", itemName, currentState, newCommand);
        return String.format(
                "Toggled '%s' from %s to %s. Result: %s",
                itemName, currentState.trim(), newCommand, result);
    }
}
