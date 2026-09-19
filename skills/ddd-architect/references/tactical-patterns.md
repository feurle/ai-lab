# Tactical DDD Patterns — Java / Spring Templates

## Aggregate Root

```java
// domain layer — no Spring, no JPA annotations here
public class Order {                              // Aggregate Root

    private final OrderId id;                     // Value Object ID
    private CustomerId customerId;                // Reference by ID only — never @ManyToOne
    private List<OrderLine> lines;                // Entities within the aggregate
    private OrderStatus status;
    private final List<DomainEvent> domainEvents = new ArrayList<>();

    // Factory method — prefer over public constructor
    public static Order place(CustomerId customerId, List<OrderLine> lines) {
        if (lines.isEmpty()) throw new DomainException("Order must have at least one line");
        var order = new Order(OrderId.generate(), customerId, lines, OrderStatus.PLACED);
        order.domainEvents.add(new OrderPlaced(order.id, customerId, Instant.now()));
        return order;
    }

    public void confirm() {
        if (status != OrderStatus.PLACED) throw new DomainException("Only placed orders can be confirmed");
        this.status = OrderStatus.CONFIRMED;
        domainEvents.add(new OrderConfirmed(this.id, Instant.now()));
    }

    public List<DomainEvent> pullDomainEvents() {
        var events = List.copyOf(domainEvents);
        domainEvents.clear();
        return events;
    }
    // ... getters, no setters
}
```

---

## Value Object

```java
// Immutable — use Java record (Java 16+)
public record OrderId(UUID value) {
    public OrderId {
        Objects.requireNonNull(value, "OrderId must not be null");
    }
    public static OrderId generate() { return new OrderId(UUID.randomUUID()); }
    public static OrderId of(String raw) { return new OrderId(UUID.fromString(raw)); }
}

public record Money(BigDecimal amount, Currency currency) {
    public Money {
        if (amount.compareTo(BigDecimal.ZERO) < 0) throw new DomainException("Money cannot be negative");
        Objects.requireNonNull(currency);
    }
    public Money add(Money other) {
        if (!this.currency.equals(other.currency)) throw new DomainException("Currency mismatch");
        return new Money(this.amount.add(other.amount), this.currency);
    }
}
```

---

## Domain Event

```java
// Plain Java — immutable, past tense name, carries enough context
public record OrderPlaced(
    OrderId orderId,
    CustomerId customerId,
    Instant occurredOn
) implements DomainEvent {}

// Marker interface
public interface DomainEvent {
    Instant occurredOn();
}
```

---

## Repository Interface (Domain Layer)

```java
// Domain layer — zero infrastructure imports
public interface OrderRepository {
    void save(Order order);
    Optional<Order> findById(OrderId id);
    List<Order> findByCustomer(CustomerId customerId);
}
```

---

## Repository Implementation (Infrastructure Layer)

```java
// infrastructure layer — Spring Data JPA
@Repository
public class JpaOrderRepository implements OrderRepository {

    private final SpringDataOrderRepository springRepo;
    private final OrderMapper mapper;

    @Override
    public void save(Order order) {
        var entity = mapper.toEntity(order);
        springRepo.save(entity);
        // publish domain events after persistence
        order.pullDomainEvents().forEach(eventPublisher::publish);
    }

    @Override
    public Optional<Order> findById(OrderId id) {
        return springRepo.findById(id.value()).map(mapper::toDomain);
    }
}

// Spring Data interface — infrastructure only
interface SpringDataOrderRepository extends JpaRepository<OrderEntity, UUID> {}
```

---

## Application Service

```java
// Thin orchestration — no business logic here
@Service
@Transactional
public class OrderApplicationService {

    private final OrderRepository orderRepository;
    private final CustomerRepository customerRepository;

    public OrderId placeOrder(PlaceOrderCommand command) {
        var customer = customerRepository.findById(command.customerId())
            .orElseThrow(() -> new NotFoundException("Customer not found"));

        var lines = command.lines().stream()
            .map(l -> new OrderLine(ProductId.of(l.productId()), l.quantity(), l.unitPrice()))
            .toList();

        var order = Order.place(customer.getId(), lines);
        orderRepository.save(order);
        return order.getId();
    }
}

// Command — plain DTO, no domain types
public record PlaceOrderCommand(UUID customerId, List<OrderLineDto> lines) {}
```

---

## Domain Service

```java
// Use when logic doesn't naturally belong to one aggregate
public class PricingService {

    private final DiscountRepository discountRepository;

    public Money calculateTotal(Order order, CustomerId customerId) {
        var discounts = discountRepository.findApplicable(customerId, order.getLines());
        // pricing logic involving multiple aggregates / external rules
        return applyDiscounts(order.subtotal(), discounts);
    }
}
```

---

## Domain Exception

```java
public class DomainException extends RuntimeException {
    public DomainException(String message) { super(message); }
}

public class InvariantViolationException extends DomainException {
    public InvariantViolationException(String invariant) {
        super("Invariant violated: " + invariant);
    }
}
```

---

## JPA Entity (Infrastructure — separate from domain model)

```java
@Entity
@Table(name = "orders")
class OrderEntity {
    @Id UUID id;
    UUID customerId;
    String status;

    @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
    List<OrderLineEntity> lines;
}
```

> **Key rule**: Never annotate domain classes with `@Entity`. Keep domain and persistence models separate and use a mapper between them.
