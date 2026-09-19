# Mermaid Diagram Templates for DDD

## Context Map

```mermaid
graph LR
  subgraph Core["Core Domain"]
    OC["🛒 Ordering Context"]
    IC["📦 Inventory Context"]
  end

  subgraph Supporting["Supporting Subdomains"]
    PC["💳 Payment Context"]
    NC["📧 Notification Context"]
  end

  subgraph Generic["Generic Subdomains"]
    IAM["🔐 Identity & Access"]
  end

  OC -- "Customer/Supplier\n(OC upstream)" --> IC
  OC -- "ACL" --> PC
  OC -- "OHS / Events" --> NC
  IAM -- "Conformist" --> OC
  IAM -- "Conformist" --> IC
```

### Integration Pattern Labels to use on arrows:
- `Partnership` — teams collaborate, evolve together
- `Shared Kernel` — shared code, agreed by both teams
- `Customer/Supplier` — upstream/downstream with negotiated API
- `Conformist` — downstream conforms to upstream model as-is
- `ACL` — Anti-Corruption Layer (downstream translates upstream model)
- `OHS` — Open Host Service (upstream publishes formal API)
- `Published Language` — formal interchange format (e.g. events schema)
- `Separate Ways` — no integration, duplicate if needed

---

## Aggregate Diagram

```mermaid
classDiagram
  class Order {
    <<AggregateRoot>>
    +OrderId id
    +CustomerId customerId
    +OrderStatus status
    +place(customerId, lines) Order$
    +confirm()
    +cancel(reason)
    +pullDomainEvents() DomainEvent[]
  }

  class OrderLine {
    <<Entity>>
    +OrderLineId id
    +ProductId productId
    +Quantity quantity
    +Money unitPrice
    +subtotal() Money
  }

  class Money {
    <<ValueObject>>
    +BigDecimal amount
    +Currency currency
    +add(Money) Money
  }

  class OrderId {
    <<ValueObject>>
    +UUID value
  }

  class OrderPlaced {
    <<DomainEvent>>
    +OrderId orderId
    +CustomerId customerId
    +Instant occurredOn
  }

  Order "1" *-- "1..*" OrderLine : contains
  Order ..> OrderPlaced : emits
  OrderLine --> Money : uses
```

---

## Hexagonal Architecture (per context)

```mermaid
graph TB
  subgraph Driving["Driving Adapters (inbound)"]
    REST["REST Controller"]
    CLI["CLI / Batch"]
    MSG_IN["Message Consumer"]
  end

  subgraph App["Application Layer"]
    AS["Application Service\n(Use Cases)"]
  end

  subgraph Domain["Domain Layer"]
    AGG["Aggregates"]
    DS["Domain Services"]
    REPO_IF["Repository Interfaces"]
    EVT["Domain Events"]
  end

  subgraph Driven["Driven Adapters (outbound)"]
    JPA["JPA Repository\nImpl"]
    MSG_OUT["Event Publisher\n(Kafka / RabbitMQ)"]
    EXT["External System\nClient (ACL)"]
  end

  REST --> AS
  CLI --> AS
  MSG_IN --> AS
  AS --> AGG
  AS --> DS
  AGG --> EVT
  AGG --> REPO_IF
  REPO_IF -.implements.-> JPA
  EVT -.published via.-> MSG_OUT
  DS -.calls.-> EXT
```

---

## EventStorming Timeline (simplified)

```mermaid
sequenceDiagram
  actor Customer
  participant Cart as Cart Context
  participant Inventory as Inventory Context
  participant Payment as Payment Context
  participant Notification as Notification Context

  Customer->>Cart: Place Order (Command)
  Cart-->>Cart: OrderPlaced (Event)
  Cart->>Inventory: Reserve Stock (Command via Policy)
  Inventory-->>Inventory: StockReserved (Event)
  Inventory->>Payment: Initiate Payment (Command via Policy)
  Payment-->>Payment: PaymentAuthorised (Event)
  Payment->>Cart: Confirm Order (Command via Policy)
  Cart-->>Cart: OrderConfirmed (Event)
  Cart->>Notification: Send Confirmation (Command via Policy)
```
