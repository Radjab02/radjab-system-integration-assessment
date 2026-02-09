# System Architecture Diagram

## Task 1: Mock API Setup (Current Implementation)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DOCKER COMPOSE ENVIRONMENT                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │                      MOCK APIS SERVICE                          │     │
│  │                    (Spring Boot :8081)                          │     │
│  ├────────────────────────────────────────────────────────────────┤     │
│  │                                                                 │     │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │     │
│  │  │   CRM API    │  │ Inventory API│  │Analytics API │        │     │
│  │  ├──────────────┤  ├──────────────┤  ├──────────────┤        │     │
│  │  │ GET /customers│  │ GET /products│  │ POST /data   │        │     │
│  │  │POST /customers│  │              │  │              │        │     │
│  │  │ (REST)       │  │ (REST)       │  │ (REST)       │        │     │
│  │  └──────────────┘  └──────────────┘  └──────────────┘        │     │
│  │                                                                 │     │
│  │  ┌──────────────┐                                              │     │
│  │  │  SOAP API    │                                              │     │
│  │  ├──────────────┤                                              │     │
│  │  │ AddCustomer  │                                              │     │
│  │  │ /ws/customers│                                              │     │
│  │  │ (SOAP/WSDL)  │                                              │     │
│  │  └──────────────┘                                              │     │
│  │                                                                 │     │
│  │  ┌──────────────────────────────────────────────────┐         │     │
│  │  │         H2 In-Memory Database                    │         │     │
│  │  ├──────────────────────────────────────────────────┤         │     │
│  │  │ • customers (5 sample records)                   │         │     │
│  │  │ • products  (7 sample records)                   │         │     │
│  │  └──────────────────────────────────────────────────┘         │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │                      KAFKA ECOSYSTEM                            │     │
│  ├────────────────────────────────────────────────────────────────┤     │
│  │                                                                 │     │
│  │  ┌──────────────┐                                              │     │
│  │  │  Zookeeper   │                                              │     │
│  │  │   :2181      │                                              │     │
│  │  └──────┬───────┘                                              │     │
│  │         │                                                       │     │
│  │  ┌──────▼───────┐       ┌─────────────────────┐              │     │
│  │  │    Kafka     │       │   Kafka UI          │              │     │
│  │  │ :9092, :9093 │◄──────┤   :8090             │              │     │
│  │  ├──────────────┤       │   (Monitoring)      │              │     │
│  │  │ Topics:      │       └─────────────────────┘              │     │
│  │  │• customer_data│                                             │     │
│  │  │• inventory_data│                                            │     │
│  │  └──────────────┘                                              │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │                      LOCALSTACK                                 │     │
│  │                      :4566, :4571                               │     │
│  ├────────────────────────────────────────────────────────────────┤     │
│  │ AWS Services Simulation: S3, SQS, SNS, DynamoDB                │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

## Future Architecture (Tasks 2-3)

```
┌─────────────┐                  ┌──────────────────┐
│   CRM API   │                  │ Java Producer #1 │
│ (REST/SOAP) │◄─────────────────┤  (Spring Boot)   │
│   :8081     │  Fetch Customers │                  │
└─────────────┘                  └────────┬─────────┘
                                          │ Publish
                                          │
┌─────────────┐                           ▼
│ Inventory   │                  ┌─────────────────┐
│    API      │                  │  Kafka Topics   │
│   :8081     │◄─────────┐       │ • customer_data │
└─────────────┘          │       │ • inventory_data│
                         │       └────────┬────────┘
              ┌──────────▼──────┐        │ Consume
              │ Java Producer #2│        │
              │  (Spring Boot)  │        ▼
              │ Fetch Products  │  ┌─────────────────┐
              └─────────────────┘  │ Python Consumer │
                                   │  • Merge data   │
                                   │  • Idempotency  │
┌─────────────┐                    │  • Retry logic  │
│ Analytics   │                    └────────┬────────┘
│    API      │◄────────────────────────────┘
│   :8081     │    Send merged data
└─────────────┘
```

## Data Flow

1. **Mock APIs** provide data endpoints (Task 1) ✅
2. **Java Producers** fetch and publish to Kafka (Task 2)
3. **Python Consumers** process and merge data (Task 3)
4. **Analytics API** receives merged data
5. **Monitoring** via Kafka UI and logs

## Technology Layers

```
┌─────────────────────────────────────────┐
│         Application Layer                │
├─────────────────────────────────────────┤
│ • Spring Boot REST Controllers          │
│ • Spring WS SOAP Endpoints               │
│ • Python Kafka Consumers                 │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         Service Layer                    │
├─────────────────────────────────────────┤
│ • Business Logic                         │
│ • Data Transformation                    │
│ • Validation                             │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         Integration Layer                │
├─────────────────────────────────────────┤
│ • Kafka Producers (Java)                 │
│ • Kafka Consumers (Python)               │
│ • REST Clients                           │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         Data Layer                       │
├─────────────────────────────────────────┤
│ • H2 Database (In-Memory)                │
│ • JPA Repositories                       │
│ • Entity Models                          │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         Infrastructure Layer             │
├─────────────────────────────────────────┤
│ • Docker Containers                      │
│ • Kafka Messaging                        │
│ • LocalStack (AWS Simulation)            │
└─────────────────────────────────────────┘
```

## Network Architecture

```
┌──────────────────────────────────────────────┐
│      integration-network (Docker Bridge)     │
├──────────────────────────────────────────────┤
│                                              │
│  mock-apis ◄──► kafka ◄──► zookeeper       │
│      ▲                                       │
│      │                                       │
│      └──────► localstack                    │
│                                              │
└──────────────────────────────────────────────┘
           │              │
           │              │
    ┌──────▼──────┐ ┌────▼──────┐
    │ Host :8081  │ │Host :9093 │
    │ (APIs)      │ │ (Kafka)   │
    └─────────────┘ └───────────┘
```

## Port Mapping

| Service      | Internal Port | External Port | Purpose                |
|--------------|---------------|---------------|------------------------|
| mock-apis    | 8081          | 8081          | REST/SOAP APIs         |
| kafka        | 9092          | 9092          | Internal communication |
| kafka        | 9093          | 9093          | External access        |
| zookeeper    | 2181          | 2181          | Coordination           |
| kafka-ui     | 8080          | 8090          | Monitoring UI          |
| localstack   | 4566          | 4566          | AWS services           |

## Security Considerations (Future)

- API authentication (JWT/OAuth2)
- Kafka SASL/SSL encryption
- Network isolation
- Secret management
- Rate limiting

---

*Diagram Version: 1.0*  
*Last Updated: Task 1 Complete*
