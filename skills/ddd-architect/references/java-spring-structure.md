# Java / Spring Package Structure for DDD

## Recommended Layout — Package by Component (Hexagonal / Clean)

```
com.company.{app}/
│
├── {context}/                          ← one package per Bounded Context
│   ├── domain/                         ← PURE JAVA — zero framework dependencies
│   │   ├── model/
│   │   │   ├── {Aggregate}.java        ← Aggregate Root
│   │   │   ├── {Entity}.java
│   │   │   ├── {ValueObject}.java      ← records preferred
│   │   │   └── {AggregateId}.java      ← typed ID value object
│   │   ├── event/
│   │   │   └── {DomainEvent}.java      ← records, immutable
│   │   ├── service/
│   │   │   └── {DomainService}.java    ← stateless, domain logic only
│   │   ├── repository/
│   │   │   └── {Aggregate}Repository.java  ← interface only
│   │   └── exception/
│   │       └── DomainException.java
│   │
│   ├── application/                    ← orchestration, thin
│   │   ├── {UseCase}ApplicationService.java
│   │   ├── command/
│   │   │   └── {Action}Command.java    ← plain DTOs (records)
│   │   └── query/
│   │       └── {View}Query.java        ← CQRS read side (optional)
│   │
│   └── infrastructure/                 ← Spring, JPA, messaging, HTTP clients
│       ├── persistence/
│       │   ├── {Aggregate}Entity.java       ← @Entity classes
│       │   ├── Spring{Aggregate}Repository.java  ← JpaRepository
│       │   ├── Jpa{Aggregate}Repository.java     ← implements domain interface
│       │   └── {Aggregate}Mapper.java            ← domain ↔ entity
│       ├── messaging/
│       │   └── {Event}Publisher.java        ← publishes domain events
│       └── rest/                            ← inbound adapter (optional per context)
│           └── {Resource}Controller.java
│
└── shared/                             ← truly shared kernel (keep tiny!)
    ├── domain/
    │   └── DomainEvent.java            ← marker interface
    └── infrastructure/
        └── EventPublisher.java
```

---

## Dependency Rule

```
infrastructure → application → domain
                                ↑
                         no outward deps
```

The domain layer must never import from application or infrastructure.
Use **dependency inversion**: domain defines interfaces, infrastructure implements them.

---

## Spring Configuration Tips

### Separate Spring config per context
```java
@Configuration
@ComponentScan("com.company.app.ordering")
public class OrderingContextConfig {}
```

### Transactional boundary = Application Service
```java
@Service
@Transactional          // on the application service, NOT on the domain
public class OrderApplicationService { ... }
```

### Event publishing after commit
```java
@Component
public class DomainEventPublisher {

    private final ApplicationEventPublisher spring;

    @TransactionalEventListener(phase = AFTER_COMMIT)
    public void handle(DomainEventWrapper wrapper) {
        // safe to publish to message broker here
    }
}
```

### Testing — slice per layer
```java
// Domain: plain JUnit, no Spring context needed
// Application: @SpringBootTest with mocked repositories
// Infrastructure: @DataJpaTest for persistence, @WebMvcTest for REST
```

---

## Multi-Module Maven Layout (for larger projects)

```
parent-pom/
├── ordering-domain/        ← pom with zero Spring deps
├── ordering-application/   ← depends on domain
├── ordering-infrastructure/← depends on application, Spring Boot
└── ordering-api/           ← REST DTOs / OpenAPI spec (shared with consumers)
```

This enforces the dependency rule at compile time.
