# MCP OpenHab Server

A Spring Boot application that provides a **Model Context Protocol (MCP) Server** for controlling OpenHab smart home devices through AI/LLM clients.

## Prerequisites

- **Java 21** or later
- An **OpenHab** instance that is reachable (local or over network)
- **API Token** for OpenHab (create one in OpenHab settings under Users)

## Quick Start

### 1. Configure

Either export environment variables:

```bash
export OPENHAB_API_TOKEN="your-api-token-here"
export OPENHAB_BASE_URL="http://your-openhab-url"   # optional, defaults to http://openhab.feurle.com
```

or copy `.env.example` to `.env` and fill in your values — Spring Boot loads it automatically on
startup, no `export`/sourcing needed (`.env` is git-ignored):

```bash
cp .env.example .env
# edit .env
```

### 2. Start the Server

```bash
./gradlew bootRun
```

The server will run on `http://localhost:8081`

### 3. Done!

The MCP server is ready and waiting for SSE connections at `http://localhost:8081/sse`

## Configuration

Both settings are read from the environment (see [Set Environment Variable](#1-configure) above) and
resolved in `src/main/resources/application.yaml`:

```yaml
openhab:
  base-url: ${OPENHAB_BASE_URL:http://openhab.feurle.com}
  api-token: ${OPENHAB_API_TOKEN}
```

| Variable            | Default                     | Description                           |
|---------------------|------------------------------|----------------------------------------|
| `OPENHAB_API_TOKEN` | *(required)*                 | Bearer token for the OpenHAB REST API |
| `OPENHAB_BASE_URL`  | `http://openhab.feurle.com`  | Base URL of your OpenHAB instance     |

**Change OpenHab URL:**

If your OpenHab instance runs on a different host:

```bash
OPENHAB_API_TOKEN="your-token" OPENHAB_BASE_URL="http://192.168.1.100:8080" ./gradlew bootRun
```

## MCP Client Configuration

To use this server with Claude Desktop or other MCP clients:

**Claude Desktop (`claude_desktop_config.json`):**
```json
{
  "mcpServers": {
    "openhab": {
      "url": "http://localhost:8081/sse"
    }
  }
}
```

## Available Tools

The server exposes the following AI tools:

- **getItemState** — Get the current state of a device (e.g., "ON", "OFF")
- **getAllItems** — List all available devices and their current state
- **turnSwitch** — Turn a device ON or OFF
- **toggleSwitch** — Toggle a device (if ON, turn OFF and vice versa)

## Troubleshooting

### "Session not found" Error

If you see a "Session not found" error:

1. **Restart your MCP client** — The client needs to re-establish the SSE connection
2. **Restart the server** — Sessions are in-memory and will be lost

### Invalid API Token

- Verify the token in OpenHab settings
- Check the environment variable: `echo $OPENHAB_API_TOKEN`

### Failed to Connect to OpenHab

- Verify OpenHab is reachable: `curl http://your-openhab-url:8080`
- Use the correct URL in `application.yaml`
- Check firewall rules

## Build & Deployment

**Create executable JAR:**
```bash
./gradlew bootJar
```

The JAR will be in `build/libs/` and can be run with `java -jar`.

**Build Docker image:**
```bash
./gradlew bootBuildImage
```

## Resources

- [Spring Boot Documentation](https://spring.io/projects/spring-boot)
- [Spring AI MCP](https://github.com/spring-projects-experimental/spring-ai-mcp)
- [OpenHab REST API](https://www.openhab.org/docs/configuration/restdocs.html)
- [Model Context Protocol](https://modelcontextprotocol.io/)