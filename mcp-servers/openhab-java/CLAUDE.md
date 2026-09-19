# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Spring Boot MCP (Model Context Protocol) server that exposes OpenHab smart home controls as tools callable by AI/LLM clients. It bridges AI models to an OpenHab hub via its REST API using Server-Sent Events (SSE) for the MCP transport layer.

## Commands

```bash
# Build
./gradlew build

# Run the application (requires OPENHAB_API_TOKEN; see Configuration below)
OPENHAB_API_TOKEN=<token> ./gradlew bootRun

# Run tests
./gradlew test

# Format code (Spotless with Google Java Format)
./gradlew spotlessApply

# Check code formatting without modifying
./gradlew spotlessCheck

# Build executable JAR
./gradlew bootJar

# Build Docker/OCI image
./gradlew bootBuildImage

# Clean
./gradlew clean
```

Java 21 is required. Code is formatted with Spotless using Google Java Format (AOSP style).

## Architecture

```
AI/LLM Client
    ↓  SSE (MCP Protocol) on port 8081
Spring Boot MCP Server
    ↓
OpenHabTools  →  OpenHabClient  →  OpenHab REST API  →  Smart Home Devices
```

**Key source files under `src/main/java/com/feurle/ai/mcp/`:**

- `McpOpenhabServer.java` — Spring Boot entry point
- `config/OpenHabConfig.java` — `@ConfigurationProperties` for `openhab.base-url` and `openhab.api-token`
- `config/McpServerConfig.java` — Registers `OpenHabTools` methods as MCP `ToolCallbackProvider`
- `client/OpenHabClient.java` — Reactive `WebClient` wrapper for the OpenHab REST API (get state, list items, send commands)
- `tools/OpenHabTools.java` — `@Tool`-annotated methods exposed to LLM clients: `getItemState`, `getAllItems`, `turnSwitch`, `toggleSwitch`

## Configuration

Runtime config is in `src/main/resources/application.yaml`. The MCP SSE endpoint is `/mcp/message` on port `8081`.

Both settings are read from environment variables (`application.yaml` uses `${OPENHAB_API_TOKEN}` /
`${OPENHAB_BASE_URL:http://openhab.feurle.com}`), so no code or property-file changes are needed to
point at a different OpenHAB instance:

- `OPENHAB_API_TOKEN` — **required**, no default. Create it in OpenHAB under Settings → Users.
- `OPENHAB_BASE_URL` — optional, defaults to `http://openhab.feurle.com`.

Set them either as real environment variables (shell `export`, IDE run configuration, systemd unit,
container env, ...) or via a `.env` file in the project root (copy `.env.example` to `.env`; it is
git-ignored). `spring.config.import=optional:file:.env[.properties]` in `application.yaml` makes Spring
Boot load `.env` automatically on startup — no manual `export`/sourcing required. A real environment
variable of the same name still takes precedence over `.env`.

## Technology Stack

- Spring Boot 4.0.3 with Spring WebFlux (reactive/non-blocking)
- Spring AI MCP Server 2.0.0-M2 (`spring-ai-starter-mcp-server-webflux`)
- Lombok for boilerplate reduction
- Spotless with Google Java Format for code formatting
- Gradle 9.3.1 wrapper (use `./gradlew`)