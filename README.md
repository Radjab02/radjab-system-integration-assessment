# Systems Integration Specialist Assignment
## Scalable E-Commerce Integration Pipeline (Java + Python)

[![Java](https://img.shields.io/badge/Java-21-orange.svg)](https://openjdk.java.net/)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.4.1-brightgreen.svg)](https://spring.io/projects/spring-boot)
[![Kafka](https://img.shields.io/badge/Kafka-7.6.0-black.svg)](https://kafka.apache.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)

## 📋 Assignment Overview

This project implements a **scalable system integration pipeline** for an e-commerce platform that:
- Fetches data from CRM and Inventory systems using **Java/Spring Boot producers**
- Publishes data to **Kafka** message queue
- Processes and merges data using **Python consumers**
- Sends analytics data to downstream systems
- Ensures **reliability, idempotency, and retry logic**

**Estimated Completion**: 5 days  
**Target Throughput**: 10,000 records/hour  
**Completion**: 5 minutes for inventory export

---

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   CRM API   │────────▶│  Java Producer   │────────▶│  Kafka Topics   │
│ (REST/SOAP) │         │  (Spring Boot)   │         │ - customer_data │
└─────────────┘         └──────────────────┘         │ - inventory_data│
                                                      └────────┬────────┘
┌─────────────┐         ┌──────────────────┐                 │
│ Inventory   │────────▶│  Java Producer   │─────────────────┘
│   API       │         │  (Spring Boot)   │
│   (REST)    │         └──────────────────┘
└─────────────┘                                               │
                                                              ▼
                        ┌──────────────────┐         ┌─────────────────┐
                        │ Python Consumer  │◀────────│  Kafka Topics   │
                        │  - Merge Data    │         └─────────────────┘
                        │  - Idempotency   │
                        │  - Retry Logic   │
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  Analytics API  │
                        │  (REST/CSV)     │
                        └─────────────────┘
```

---

## 📁 Project Structure

```
systems-integration-assignment/
├── mock-apis/                    # Task 1: Mock API implementation
│   ├── src/main/java/            # Spring Boot application
│   ├── build.gradle              # Gradle build configuration
│   └── Dockerfile                # Container definition
│
├── java-producers/               # Task 2: Java producers (TBD)
│   ├── src/main/java/            # Producer implementation
│   └── build.gradle
│
├── python-consumers/             # Task 3: Python consumers (TBD)
│   ├── src/                      # Consumer implementation
│   └── requirements.txt
│
├── infrastructure/               # Infrastructure configs
│   ├── kafka/                    # Kafka configurations
│   └── localstack/               # LocalStack configs
│
├── docs/                         # Documentation
│   ├── api-specs/                # OpenAPI, WSDL, samples
│   ├── diagrams/                 # Architecture diagrams
│   ├── TASK1-README.md           # Task 1 documentation
│   └── [TASK2-7 READMEs]         # Future task docs
│
├── docker-compose.yml            # Full stack orchestration
└── README.md                     # This file
```

---

## 🚀 Quick Start

### Prerequisites
- **Docker** and **Docker Compose**
- **Java 21** (for local development)
- **Python 3.11+** (for consumers - Task 3)
- **curl** or **Postman** (for testing)

### Start the System

```bash
# Clone or navigate to project directory
cd systems-integration-assignment

# Start all services (Kafka, LocalStack, Mock APIs)
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f mock-apis
```

### Verify Installation

1. **Swagger UI**: http://localhost:8081/swagger-ui.html
2. **Kafka UI**: http://localhost:8090
3. **H2 Console**: http://localhost:8081/h2-console (if enabled)

### Test the APIs

```bash
# Test CRM API
curl http://localhost:8081/api/customers

# Test Inventory API
curl http://localhost:8081/api/products

# Test SOAP endpoint
curl -X POST http://localhost:8081/ws/customers?wsdl
```

---

## 📊 Task Progress

| Task | Description | Status | Documentation |
|------|-------------|--------|---------------|
| **Task 1** | Mock API Setup | ✅ Complete | [TASK1-README.md](docs/TASK1-README.md) |
| **Task 2** | Java Producers | ✅ Complete | [TASK2-README.md](docs/TASK2-README.md) |
| **Task 3** | Python Consumers | ✅ Complete | [TASK3-README.md](docs/TASK3-README.md) |
| **Task 4** | Scalability & Performance | 🔜 Pending | TBD |
| **Task 5** | Integration Concept | 🔜 Pending | TBD |
| **Task 6** | Testing & Reliability | 🔜 Pending | TBD |
| **Task 7** | Bonus Features | 🔜 Pending | TBD |

---

## 🎯 Task 1: Mock API Setup ✅

### Implemented Features

- ✅ **REST APIs**: CRM, Inventory, Analytics endpoints
- ✅ **SOAP API**: AddCustomer operation with WSDL
- ✅ **OpenAPI Spec**: Complete API documentation
- ✅ **Sample Data**: 5 customers, 7 products pre-loaded
- ✅ **Docker Support**: Containerized deployment
- ✅ **Kafka Integration**: Ready for message queue
- ✅ **LocalStack**: AWS services simulation

### API Endpoints

#### REST Endpoints
- `GET /api/customers` - Fetch customer data (paginated)
- `POST /api/customers` - Create new customer
- `GET /api/products` - Fetch inventory data (paginated, filterable)
- `POST /api/analytics/data` - Ingest analytics data

#### SOAP Endpoint
- `POST /ws/customers` - AddCustomer operation
- `GET /ws/customers?wsdl` - WSDL definition

### Sample Data Preview

**Customers**: CUST001-CUST005 (John Doe, Jane Smith, etc.)  
**Products**: PROD001-PROD007 (Laptop Pro, Mouse, Monitor, etc.)

See [TASK1-README.md](docs/TASK1-README.md) for complete details.

---

## 🔧 Technology Stack

### Backend (Task 1 & 2)
- **Java 21**
- **Spring Boot 3.4.1**
- **Spring Data JPA**
- **Spring Web Services** (SOAP)
- **Spring Kafka**
- **Gradle**

### Consumers (Task 3)
- **Python 3.11+**
- **kafka-python**
- **requests**
- **pandas** (for CSV)

### Infrastructure
- **Apache Kafka 7.6.0**
- **Zookeeper**
- **LocalStack** (AWS simulation)
- **Docker Compose**

### Documentation
- **OpenAPI 3.0**
- **WSDL 1.1**
- **Swagger UI**

---

## 📚 Documentation

### API Documentation
- [OpenAPI Specification](docs/api-specs/openapi-spec.yaml)
- [WSDL Definition](mock-apis/src/main/resources/wsdl/customer-service.wsdl)
- [Sample Payloads](docs/api-specs/sample-payloads.md)
- [Postman Collection](docs/api-specs/Postman-Collection.json)

### Task Documentation
- [Task 1: Mock API Setup](docs/TASK1-README.md)
- [Task 2: Java Producers](docs/TASK2-README.md)
- [Task 3: Python Consumers](docs/TASK3-README.md)
- Task 4-7: Coming soon...

---

## 🧪 Testing

### Manual Testing
```bash
# Import Postman collection
docs/api-specs/Postman-Collection.json

# Or use curl
curl http://localhost:8081/api/customers
curl http://localhost:8081/api/products?inStock=true
```

### Automated Tests
```bash
# Unit tests (Task 6)
cd mock-apis
./gradlew test

# Integration tests (Task 6)
./gradlew integrationTest
```

---

## 🎓 Learning Objectives Demonstrated

### Task 1 (Current)
- ✅ REST API design and implementation
- ✅ SOAP web service integration
- ✅ OpenAPI documentation
- ✅ Docker containerization
- ✅ Sample data management
- ✅ Kafka infrastructure setup

### Upcoming Tasks
- 🔜 Kafka producer implementation (Java)
- 🔜 Kafka consumer implementation (Python)
- 🔜 Data transformation and merging
- 🔜 Idempotency and retry logic
- 🔜 Scalability strategies
- 🔜 Monitoring and observability

---

## 🚧 Next Steps

1. **Task 2**: Implement Java producers
   - Fetch from CRM and Inventory APIs
   - Publish to Kafka topics
   - Implement retry logic

2. **Task 3**: Implement Python consumers
   - Consume from Kafka
   - Merge customer + inventory data
   - Send to Analytics API

3. **Task 4**: Performance testing
   - 10,000 records/hour
   - 5-minute inventory export

---

## 🔧 Challenges Encountered - Task 1

### 1. Spring Boot & SpringDoc Version Compatibility
**Challenge:** Initial implementation used `springdoc-openapi-starter-webmvc-ui:2.3.0` which caused a `NoSuchMethodError: ControllerAdviceBean.<init>` when accessing the Swagger UI.

**Root Cause:** Spring Boot 3.4.1 introduced breaking changes in the `ControllerAdviceBean` class constructor that weren't compatible with older SpringDoc versions.

**Solution:** Upgraded to `springdoc-openapi-starter-webmvc-ui:2.8.0` (latest version) which has full compatibility with Spring Boot 3.4.x.

**Learning:** Always verify library compatibility with major Spring Boot versions, especially for documentation tools that rely heavily on Spring's internal APIs.

### 2. Lombok Annotation Processing
**Challenge:** When opening the project in IntelliJ IDEA, developers encountered "Cannot resolve symbol" errors for Lombok-generated methods (getters, setters, builders) even though the project compiled successfully via Gradle.

**Root Cause:** IntelliJ's annotation processing was disabled by default, preventing Lombok from generating code during the IDE's compilation phase.

**Solution:** 
- Enabled annotation processing: `Settings → Compiler → Annotation Processors → Enable annotation processing`
- Installed Lombok plugin for IntelliJ
- Invalidated caches and rebuilt project

**Learning:** Lombok requires explicit IDE configuration beyond just adding the dependency. This is a common gotcha for new developers.

### 3. JAXB Code Generation Complexity
**Challenge:** Initial implementation included a Gradle task to auto-generate Java classes from WSDL using JAXB XJC, which added build complexity and potential failure points.

**Root Cause:** JAXB code generation required additional classpath configuration and could fail silently, making debugging difficult.

**Solution:** Simplified by removing auto-generation and manually creating SOAP endpoint handlers using Spring's DOM-based approach (`Element` handling). This made the build more reliable and the code easier to understand.

**Learning:** For mock/demo projects, manual SOAP handling is often more maintainable than code generation, especially when you only need a few operations.

### 4. Favicon 404 Errors in Logs
**Challenge:** Console logs showed repeated `NoResourceFoundException: No static resource favicon.ico` errors when accessing any endpoint via browser.

**Root Cause:** Browsers automatically request `/favicon.ico` for every page, but the application didn't have a favicon configured.

**Solution:** Recognized this as harmless browser behavior. Could be suppressed by:
- Adding a favicon to `src/main/resources/static/`
- Or filtering the log level for `ResourceHttpRequestHandler`

**Learning:** Not all errors need fixing - understanding what's cosmetic vs. critical is important. This error doesn't affect functionality.

### 5. SOAP vs REST Architecture Decision
**Challenge:** Determining the right balance between REST and SOAP for a modern integration project while still demonstrating enterprise integration skills.

**Decision:** Implemented hybrid approach:
- Primary REST endpoints for CRM, Inventory, and Analytics (modern, lightweight)
- Single SOAP endpoint (AddCustomer) to demonstrate WSDL-based integration

**Rationale:**
- REST is standard for new microservices
- SOAP demonstrates ability to work with legacy enterprise systems
- Provides architectural talking points without overcomplicating the implementation

**Learning:** Architecture decisions should balance technical requirements, demonstration value, and maintainability.

### 6. Docker Compose Networking
**Challenge:** Ensuring services could communicate within Docker network while remaining accessible from host machine for testing.

**Solution:** 
- Created custom bridge network (`integration-network`)
- Configured dual Kafka listeners (internal and external)
- Proper port mapping for all services

**Learning:** Container networking requires understanding both internal (container-to-container) and external (host-to-container) communication patterns.

### 7. H2 Database Initialization Timing
**Challenge:** Ensuring sample data was loaded after JPA schema creation but before the application started serving requests.

**Solution:** Used `CommandLineRunner` interface in `DataInitializer.java` which runs after the application context is fully initialized but before accepting traffic.

**Learning:** Spring Boot provides several initialization hooks - choosing the right one (CommandLineRunner, ApplicationRunner, @PostConstruct) depends on when dependencies need to be ready.

### 8. Alpine Linux and Snappy Compression Compatibility (Task 2)
**Challenge:** When building Docker images for Java Producers, using Alpine Linux base image (`eclipse-temurin:21-jre-alpine`) resulted in `UnsatisfiedLinkError: Error loading shared library ld-linux-x86-64.so.2` when Kafka tried to use Snappy compression.

**Root Cause:** Alpine Linux uses `musl` libc instead of `glibc`. Kafka's Snappy compression library (native binary) requires `glibc`, specifically the `ld-linux-x86-64.so.2` shared library which doesn't exist in Alpine.

**Solution:** Switched from Alpine-based image to Debian-based image (`eclipse-temurin:21-jre`). This increased image size by ~50MB but provided full `glibc` compatibility out of the box.

**Alternative Considered:** Installing `gcompat` package in Alpine to provide glibc compatibility layer, but this adds complexity and potential runtime issues.

**Learning:** Alpine Linux is great for minimal images, but native libraries (JNI, compression codecs, database drivers) often require `glibc`. For Java applications with native dependencies, Debian-based images are more reliable despite being slightly larger. The tradeoff between image size (~50MB) and compatibility/stability usually favors stability in production.

---

## 🤝 Contributing

This is an assessment project, but follows best practices:
- Clear commit messages
- Modular code structure
- Comprehensive documentation
- Test coverage (Task 6)

---

## 📝 License

This is an assessment project for demonstration purposes.

---

## 📧 Contact

For questions about this implementation, please refer to the assessment documentation.

---

**Status**: Tasks 1-3 Complete ✅ | Ready for Task 4  
**Last Updated**: February 8, 2024
