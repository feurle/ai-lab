# Context Integration Patterns

## Anti-Corruption Layer (ACL)

Use when you must consume an upstream context's model without letting it pollute yours.

```java
// Translator in the downstream context's infrastructure layer
@Component
public class LegacyOrderAcl {

    private final LegacyOrderClient legacyClient; // external HTTP/SOAP client

    public Optional<Order> findOrder(OrderId id) {
        LegacyOrderDto dto = legacyClient.getOrder(id.value().toString());
        if (dto == null) return Optional.empty();
        return Optional.of(translate(dto));
    }

    private Order translate(LegacyOrderDto dto) {
        // Map legacy concepts → your ubiquitous language
        return Order.reconstitute(
            OrderId.of(dto.getOrderNumber()),
            CustomerId.of(dto.getClientRef()),
            mapStatus(dto.getState()),
            mapLines(dto.getItems())
        );
    }

    private OrderStatus mapStatus(String legacyState) {
        return switch (legacyState) {
            case "OPEN"       -> OrderStatus.PLACED;
            case "PROCESSING" -> OrderStatus.CONFIRMED;
            case "SHIPPED"    -> OrderStatus.FULFILLED;
            default -> throw new DomainException("Unknown legacy state: " + legacyState);
        };
    }
}
```

---

## Open Host Service (OHS) + Published Language

Use when you are the upstream and want to offer a stable API to consumers.

```java
// Published Language — versioned event schema (infrastructure / API module)
public record OrderPlacedV1(
    String orderId,          // primitive types for portability
    String customerId,
    List<OrderLineV1> lines,
    String currency,
    BigDecimal totalAmount,
    String occurredOn        // ISO-8601 string
) {
    public static final String EVENT_TYPE = "order.placed.v1";
}

// Publisher — infrastructure layer
@Component
public class OrderEventPublisher {

    private final KafkaTemplate<String, Object> kafka;
    private static final String TOPIC = "orders";

    public void publish(OrderPlaced domainEvent) {
        var payload = toPublishedLanguage(domainEvent);
        kafka.send(TOPIC, domainEvent.orderId().value().toString(), payload);
    }

    private OrderPlacedV1 toPublishedLanguage(OrderPlaced e) {
        return new OrderPlacedV1(...);
    }
}
```

---

## Asynchronous Integration via Domain Events

Preferred integration style for loosely-coupled contexts:

```
Ordering Context ──[OrderPlaced event]──► Message Broker ──► Inventory Context
                                                         ──► Notification Context
```

```java
// Consumer side — infrastructure layer of receiving context
@Component
public class OrderPlacedConsumer {

    private final ReserveStockApplicationService reserveStockService;

    @KafkaListener(topics = "orders", groupId = "inventory-service")
    public void handle(OrderPlacedV1 event) {
        // Translate Published Language → command in this context
        var command = new ReserveStockCommand(
            event.orderId(),
            event.lines().stream()
                .map(l -> new StockReservation(l.productId(), l.quantity()))
                .toList()
        );
        reserveStockService.reserve(command);
    }
}
```

---

## Synchronous Integration (use sparingly)

When you need a real-time response (e.g., credit check before confirming an order):

```java
// Port in the domain layer (interface)
public interface CreditCheckService {
    CreditDecision check(CustomerId customerId, Money amount);
}

// Adapter in infrastructure layer
@Component
public class HttpCreditCheckAdapter implements CreditCheckService {

    private final CreditCheckApiClient client;

    @Override
    public CreditDecision check(CustomerId customerId, Money amount) {
        var response = client.evaluate(customerId.value().toString(), amount.amount());
        return response.isApproved() ? CreditDecision.APPROVED : CreditDecision.DECLINED;
    }
}
```

---

## CQRS (Command Query Responsibility Segregation)

Use when read and write models diverge significantly:

```java
// Write side — goes through domain model (normal flow)
orderApplicationService.placeOrder(command);

// Read side — bypasses domain, queries directly from projection/read model
@Repository
public interface OrderSummaryProjection {
    // Spring Data JPA interface projection — fine on the read side
    @Query("SELECT o FROM OrderReadModel o WHERE o.customerId = :customerId")
    List<OrderSummaryView> findByCustomer(@Param("customerId") UUID customerId);
}

// Read model — separate @Entity, updated by event listeners
@Entity
@Table(name = "order_summary")
public class OrderReadModel {
    @Id UUID orderId;
    UUID customerId;
    String status;
    BigDecimal total;
    // denormalized for query performance
}

// Projector — updates the read model when domain events are published
@Component
public class OrderSummaryProjector {

    @EventListener
    @Transactional
    public void on(OrderPlaced event) { /* insert read model row */ }

    @EventListener
    @Transactional
    public void on(OrderConfirmed event) { /* update status */ }
}
```

---

## Integration Pattern Decision Guide

| Situation | Recommended Pattern |
|-----------|-------------------|
| Consuming a legacy / external system | ACL |
| You own the upstream, many consumers | OHS + Published Language |
| Contexts evolve independently, eventual consistency OK | Async Domain Events |
| Real-time response required | Synchronous + ACL |
| Read performance >> write complexity | CQRS |
| Two teams tightly aligned, small shared model | Shared Kernel (use sparingly) |
| No meaningful integration value | Separate Ways |
