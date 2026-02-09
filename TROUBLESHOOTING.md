# Troubleshooting Guide

## Issue: Swagger UI Shows "Failed to load API definition" (500 Error)

### Quick Fix Steps:

1. **Stop the application** (if running)

2. **Clean and rebuild in IntelliJ:**
   ```
   In terminal or IntelliJ Terminal:
   cd mock-apis
   ./gradlew clean build
   ```
   
   Or on Windows:
   ```
   gradlew.bat clean build
   ```

3. **Invalidate IntelliJ caches:**
   - `File` → `Invalidate Caches...` → `Invalidate and Restart`

4. **Reimport Gradle project:**
   - Right-click on `build.gradle`
   - Select `Gradle` → `Reload Gradle Project`

5. **Run the application again**

### Root Causes:

#### 1. Missing Lombok Configuration
**Solution:** Enable annotation processing in IntelliJ
- `File` → `Settings` (or `Preferences` on Mac)
- Navigate to: `Build, Execution, Deployment` → `Compiler` → `Annotation Processors`
- ✅ Check "Enable annotation processing"
- Click `Apply` and `OK`
- Rebuild project

#### 2. Lombok Plugin Not Installed
**Solution:** Install Lombok plugin
- `File` → `Settings` → `Plugins`
- Search for "Lombok"
- Click `Install`
- Restart IntelliJ

#### 3. Java Version Mismatch
**Solution:** Ensure Java 21 is configured
- `File` → `Project Structure` → `Project`
- Set `SDK` to Java 21
- Set `Language level` to 21
- Click `Apply`

#### 4. Gradle Build Failed
**Solution:** Check console for errors
```bash
./gradlew build --stacktrace
```
Look for specific error messages and resolve dependencies.

## Issue: Application Won't Start

### Error: "Port 8081 is already in use"

**Solution 1:** Kill the process using port 8081
```bash
# Mac/Linux
lsof -ti:8081 | xargs kill -9

# Windows
netstat -ano | findstr :8081
taskkill /PID <PID> /F
```

**Solution 2:** Change the port in `application.yml`
```yaml
server:
  port: 8082  # Change to any available port
```

### Error: "Cannot resolve symbol" for Lombok annotations

**Cause:** Lombok not processed correctly

**Solution:**
1. Install Lombok plugin (see above)
2. Enable annotation processing (see above)
3. Rebuild: `Build` → `Rebuild Project`

### Error: Database initialization failed

**Solution:** Delete H2 database files (if any exist)
```bash
rm -rf ~/mockdb*
```
Then restart the application.

## Issue: Endpoints Return 404

### Check Application Context Path
The APIs should be available at:
- `http://localhost:8081/api/customers`
- `http://localhost:8081/api/products`
- `http://localhost:8081/swagger-ui.html`

### Verify Application Started Successfully
Check IntelliJ console for:
```
Started MockApisApplication in X seconds
```

If you see errors, read them carefully for clues.

## Issue: No Sample Data Loaded

### Check DataInitializer Logs
Look for in console:
```
Initializing sample data...
Initialized 5 customers
Initialized 7 products
Sample data initialization complete
```

### Manually Verify Data
Access H2 Console:
1. Go to: `http://localhost:8081/h2-console`
2. JDBC URL: `jdbc:h2:mem:mockdb`
3. Username: `sa`
4. Password: (leave empty)
5. Click `Connect`
6. Run query: `SELECT * FROM CUSTOMERS;`

## Issue: Gradle Build Errors

### "Could not resolve dependencies"
**Solution:** Check internet connection, then:
```bash
./gradlew build --refresh-dependencies
```

### "Java heap space" error
**Solution:** Increase Gradle memory in `gradle.properties`:
```properties
org.gradle.jvmargs=-Xmx2048m
```

## Issue: SOAP Endpoint Not Working

### WSDL Not Accessible
**URL:** `http://localhost:8081/ws/customers?wsdl`

**If 404:**
1. Check `WebServiceConfig.java` is present
2. Verify `@EnableWs` annotation exists
3. Check console for errors during startup

### SOAP Request Fails
**Common issue:** Wrong namespace

**Correct namespace:** `http://ecommerce.com/crm/soap`

Example request in the docs: `sample-payloads.md`

## Testing the Application

### Quick Health Check
```bash
# Check if application is running
curl http://localhost:8081/actuator/health

# Expected response:
# {"status":"UP"}
```

### Test REST Endpoints
```bash
# Get customers
curl http://localhost:8081/api/customers

# Get products
curl http://localhost:8081/api/products

# Should return JSON with sample data
```

### Access Swagger UI
1. Navigate to: `http://localhost:8081/swagger-ui.html`
2. You should see 3 sections: CRM, Inventory, Analytics
3. Try the "Try it out" feature

## IntelliJ Specific Issues

### "Cannot find symbol" errors even after build success
1. `File` → `Invalidate Caches...` → `Invalidate and Restart`
2. After restart: `Build` → `Rebuild Project`

### Gradle sync keeps failing
1. Delete `.gradle` folder in project
2. Delete `.idea` folder in project
3. Reimport project fresh

### Application runs but no output in console
1. Check Run Configuration
2. Ensure "Show console when program outputs" is enabled
3. Try running from terminal: `./gradlew bootRun`

## Still Having Issues?

### Get Detailed Logs
Run with debug logging:
```bash
./gradlew bootRun --debug
```

### Check Application Logs
Enable DEBUG level in `application.yml`:
```yaml
logging:
  level:
    root: DEBUG
```

### Verify All Files Present
Key files checklist:
- ✅ `MockApisApplication.java`
- ✅ `application.yml`
- ✅ All controller classes
- ✅ All service classes
- ✅ All repository interfaces
- ✅ All model classes
- ✅ `DataInitializer.java`
- ✅ `GlobalExceptionHandler.java`

### Contact Support
If still stuck, provide:
1. Error message from console
2. IntelliJ version
3. Java version: `java -version`
4. OS: Windows/Mac/Linux
5. Steps you've already tried

---

**Most Common Fix:** Clean build + Invalidate caches + Enable annotation processing!
