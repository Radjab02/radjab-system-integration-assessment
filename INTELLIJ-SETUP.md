# IntelliJ IDEA Setup Checklist

## ✅ Step-by-Step Setup Guide

### 1. Prerequisites
- [ ] IntelliJ IDEA installed (Community or Ultimate)
- [ ] Java 21 SDK installed
- [ ] Internet connection (for downloading dependencies)

### 2. Open Project in IntelliJ

- [ ] Extract `systems-integration-assignment.zip`
- [ ] Open IntelliJ IDEA
- [ ] Click `File` → `Open`
- [ ] Navigate to: `systems-integration-assignment/mock-apis/`
- [ ] Select `build.gradle` file
- [ ] Click `Open` → Choose "Open as Project"
- [ ] Wait for Gradle sync to complete (bottom right progress bar)

### 3. Configure Java SDK

- [ ] Go to `File` → `Project Structure` → `Project`
- [ ] Set SDK to **Java 21**
  - If not available, click `Add SDK` → `Download JDK...`
  - Select version 21 (Eclipse Temurin recommended)
- [ ] Set Language level to **21**
- [ ] Click `Apply` and `OK`

### 4. Install Required Plugins

- [ ] Go to `File` → `Settings` → `Plugins`
- [ ] Search and install:
  - [x] **Lombok** (Required!)
  - [ ] Spring Boot (helpful but optional)
  - [ ] Gradle (should be pre-installed)

### 5. Enable Annotation Processing (CRITICAL!)

- [ ] Go to `File` → `Settings` (or `Preferences` on Mac)
- [ ] Navigate to: `Build, Execution, Deployment` → `Compiler` → `Annotation Processors`
- [ ] ✅ Check **"Enable annotation processing"**
- [ ] ✅ Check **"Obtain processors from project classpath"**
- [ ] Click `Apply` and `OK`

### 6. Build the Project

- [ ] Click `Build` → `Rebuild Project`
- [ ] Wait for build to complete
- [ ] Check for errors in the Build output window
- [ ] **If errors:** See TROUBLESHOOTING.md

### 7. Verify Setup

- [ ] No red underlines in Java files
- [ ] Lombok annotations (@Data, @Builder, etc.) are recognized
- [ ] Gradle build successful (see bottom status bar)

### 8. Run the Application

**Method 1: Using IntelliJ Run Button**
- [ ] Navigate to: `src/main/java/com/ecommerce/mock/MockApisApplication.java`
- [ ] Right-click on the file
- [ ] Select `Run 'MockApisApplication'`
- [ ] Check console for "Started MockApisApplication"

**Method 2: Using Gradle Task**
- [ ] Open Gradle tool window (right sidebar)
- [ ] Expand: `mock-apis` → `Tasks` → `application`
- [ ] Double-click `bootRun`
- [ ] Check console for "Started MockApisApplication"

### 9. Test the Application

- [ ] Open browser to: `http://localhost:8081/swagger-ui.html`
- [ ] You should see Swagger UI with API documentation
- [ ] **If error:** See TROUBLESHOOTING.md

### 10. Test Individual Endpoints

```bash
# In terminal (or use IntelliJ HTTP Client)
curl http://localhost:8081/api/customers
curl http://localhost:8081/api/products
curl http://localhost:8081/actuator/health
```

- [ ] All endpoints return valid JSON responses
- [ ] Sample data is present (5 customers, 7 products)

---

## Common First-Time Issues

### ❌ "Cannot resolve symbol" errors
**Fix:** 
1. `File` → `Invalidate Caches...` → `Invalidate and Restart`
2. After restart: `Build` → `Rebuild Project`

### ❌ Swagger shows "Failed to load API definition"
**Fix:**
1. Enable annotation processing (Step 5)
2. Install Lombok plugin (Step 4)
3. `Build` → `Rebuild Project`
4. Restart application

### ❌ "Port 8081 already in use"
**Fix:**
```bash
# Mac/Linux
lsof -ti:8081 | xargs kill -9

# Windows (find PID first)
netstat -ano | findstr :8081
taskkill /PID <PID> /F
```

### ❌ Gradle sync fails
**Fix:**
1. Check internet connection
2. Click the Gradle refresh icon in Gradle tool window
3. Or run: `./gradlew clean build --refresh-dependencies`

---

## Verification Checklist

### Application Running Successfully:
- [ ] Console shows: `Started MockApisApplication in X.XX seconds`
- [ ] No error stack traces in console
- [ ] Port 8081 is bound

### Swagger UI Working:
- [ ] `http://localhost:8081/swagger-ui.html` loads
- [ ] Shows 3 API groups: CRM, Inventory, Analytics
- [ ] Can expand and see endpoints
- [ ] "Try it out" button is available

### Data Initialization:
- [ ] Console shows: "Initialized 5 customers"
- [ ] Console shows: "Initialized 7 products"
- [ ] GET /api/customers returns 5 customers
- [ ] GET /api/products returns 7 products

### H2 Console (Optional):
- [ ] `http://localhost:8081/h2-console` accessible
- [ ] Can connect with:
  - JDBC URL: `jdbc:h2:mem:mockdb`
  - Username: `sa`
  - Password: (empty)
- [ ] Can query: `SELECT * FROM CUSTOMERS;`

---

## Next Steps After Setup

1. **Explore the code:**
   - Controllers in: `src/main/java/com/ecommerce/mock/controller/`
   - Services in: `src/main/java/com/ecommerce/mock/service/`
   - Models in: `src/main/java/com/ecommerce/mock/model/`

2. **Test the APIs:**
   - Use Swagger UI's "Try it out" feature
   - Or import Postman collection from `docs/api-specs/`

3. **Review documentation:**
   - Main README: `../README.md`
   - Task 1 Details: `../docs/TASK1-README.md`
   - Architecture: `../docs/diagrams/architecture.md`

4. **Start Task 2:**
   - Create Java producers in `../java-producers/`
   - Connect to these mock APIs
   - Publish to Kafka topics

---

## Need Help?

- [ ] Check `TROUBLESHOOTING.md` in project root
- [ ] Review error messages carefully
- [ ] Check console logs
- [ ] Verify all steps in this checklist completed

**Most issues are solved by:**
1. Enabling annotation processing
2. Installing Lombok plugin
3. Rebuilding the project
4. Restarting IntelliJ

---

**✅ All checkboxes checked?** You're ready to proceed with Task 2!
