# Sample API Request/Response Payloads

## 1. GET /api/customers (REST)

### Request
```bash
curl -X GET "http://localhost:8081/api/customers?page=0&size=100" \
  -H "Accept: application/json"
```

### Response (200 OK)
```json
{
  "data": [
    {
      "id": "CUST001",
      "name": "John Doe",
      "email": "john.doe@example.com",
      "phone": "+1234567890",
      "address": "123 Main St, New York, NY 10001",
      "createdDate": "2024-01-15T10:30:00Z",
      "status": "ACTIVE"
    },
    {
      "id": "CUST002",
      "name": "Jane Smith",
      "email": "jane.smith@example.com",
      "phone": "+1987654321",
      "address": "456 Oak Ave, Los Angeles, CA 90001",
      "createdDate": "2024-02-01T14:20:00Z",
      "status": "ACTIVE"
    }
  ],
  "page": 0,
  "size": 100,
  "total": 5
}
```

---

## 2. POST /api/customers (REST)

### Request
```bash
curl -X POST "http://localhost:8081/api/customers" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bob Johnson",
    "email": "bob.johnson@example.com",
    "phone": "+1555123456",
    "address": "789 Pine Rd, Chicago, IL 60601"
  }'
```

### Response (201 Created)
```json
{
  "id": "CUST8F3A2B1C",
  "name": "Bob Johnson",
  "email": "bob.johnson@example.com",
  "phone": "+1555123456",
  "address": "789 Pine Rd, Chicago, IL 60601",
  "createdDate": "2024-02-07T10:30:00Z",
  "status": "ACTIVE"
}
```

### Error Response (400 Bad Request)
```json
{
  "timestamp": "2024-02-07T10:30:00Z",
  "status": 400,
  "error": "Validation Failed",
  "message": "Email should be valid",
  "path": "/api/customers"
}
```

---

## 3. GET /api/products (REST)

### Request - All Products
```bash
curl -X GET "http://localhost:8081/api/products?page=0&size=100" \
  -H "Accept: application/json"
```

### Request - In-Stock Only
```bash
curl -X GET "http://localhost:8081/api/products?page=0&size=100&inStock=true" \
  -H "Accept: application/json"
```

### Response (200 OK)
```json
{
  "data": [
    {
      "id": "PROD001",
      "productName": "Laptop Pro 15",
      "sku": "LPT-PRO-15-BLK",
      "stockQuantity": 45,
      "price": 1299.99,
      "category": "Electronics",
      "lastUpdated": "2024-02-05T09:15:00Z"
    },
    {
      "id": "PROD002",
      "productName": "Wireless Mouse",
      "sku": "MSE-WRL-BLU",
      "stockQuantity": 150,
      "price": 29.99,
      "category": "Accessories",
      "lastUpdated": "2024-02-06T11:30:00Z"
    },
    {
      "id": "PROD003",
      "productName": "USB-C Cable 2m",
      "sku": "CBL-USBC-2M",
      "stockQuantity": 0,
      "price": 15.99,
      "category": "Accessories",
      "lastUpdated": "2024-02-04T16:45:00Z"
    }
  ],
  "page": 0,
  "size": 100,
  "total": 7
}
```

---

## 4. POST /api/analytics/data (REST)

### Request
```bash
curl -X POST "http://localhost:8081/api/analytics/data" \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "EVT-20240207-001",
    "timestamp": "2024-02-07T10:00:00Z",
    "customers": [
      {
        "id": "CUST001",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "address": "123 Main St, New York, NY 10001",
        "createdDate": "2024-01-15T10:30:00Z",
        "status": "ACTIVE"
      }
    ],
    "products": [
      {
        "id": "PROD001",
        "productName": "Laptop Pro 15",
        "sku": "LPT-PRO-15-BLK",
        "stockQuantity": 45,
        "price": 1299.99,
        "category": "Electronics",
        "lastUpdated": "2024-02-05T09:15:00Z"
      }
    ],
    "metadata": {
      "source": "integration-pipeline",
      "version": "1.0"
    }
  }'
```

### Response (200 OK)
```json
{
  "status": "SUCCESS",
  "message": "Data processed successfully",
  "recordsProcessed": 2
}
```

---

## 5. AddCustomer (SOAP)

### SOAP Request
```xml
POST http://localhost:8081/ws/customers
Content-Type: text/xml; charset=utf-8
SOAPAction: "http://ecommerce.com/crm/soap/AddCustomer"

<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope 
    xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:crm="http://ecommerce.com/crm/soap">
   <soapenv:Header/>
   <soapenv:Body>
      <crm:AddCustomerRequest>
         <crm:name>Alice Cooper</crm:name>
         <crm:email>alice.cooper@example.com</crm:email>
         <crm:phone>+1222333444</crm:phone>
         <crm:address>999 Rock Ave, Nashville, TN 37201</crm:address>
      </crm:AddCustomerRequest>
   </soapenv:Body>
</soapenv:Envelope>
```

### SOAP Response
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope 
    xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:crm="http://ecommerce.com/crm/soap">
   <soapenv:Body>
      <crm:AddCustomerResponse>
         <crm:customer>
            <crm:id>CUSTF7E9A2B3</crm:id>
            <crm:name>Alice Cooper</crm:name>
            <crm:email>alice.cooper@example.com</crm:email>
            <crm:phone>+1222333444</crm:phone>
            <crm:address>999 Rock Ave, Nashville, TN 37201</crm:address>
            <crm:createdDate>2024-02-07T10:30:00</crm:createdDate>
            <crm:status>ACTIVE</crm:status>
         </crm:customer>
         <crm:status>SUCCESS</crm:status>
         <crm:message>Customer created successfully</crm:message>
      </crm:AddCustomerResponse>
   </soapenv:Body>
</soapenv:Envelope>
```

### SOAP Fault Response
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope 
    xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:crm="http://ecommerce.com/crm/soap">
   <soapenv:Body>
      <soapenv:Fault>
         <faultcode>soapenv:Server</faultcode>
         <faultstring>Customer with email alice.cooper@example.com already exists</faultstring>
         <detail>
            <crm:ServiceFault>
               <crm:faultCode>DUPLICATE_EMAIL</crm:faultCode>
               <crm:faultMessage>Customer with email alice.cooper@example.com already exists</crm:faultMessage>
            </crm:ServiceFault>
         </detail>
      </soapenv:Fault>
   </soapenv:Body>
</soapenv:Envelope>
```
