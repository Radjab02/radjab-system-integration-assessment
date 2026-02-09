## 🧪 How to Run Tests

This project includes both **Java producer tests** and **Python consumer tests**, each with coverage reports.

---

### ▶️ Run All Tests

Execute the helper script from the project root:

```bash
chmod +x run-tests.sh
./run-tests.sh
```

This will run both Java and Python tests sequentially.

---

### ☕ Run Java Tests Only

```bash
cd java-producers
./gradlew test jacocoTestReport
```

Open the coverage report:

```bash
open build/reports/jacoco/test/html/index.html
```

**What this does**

* Runs all JUnit tests
* Generates JaCoCo coverage report
* Outputs HTML report for detailed coverage analysis

---

### 🐍 Run Python Tests Only

```bash
cd python-consumers
pytest tests/ --cov=src --cov-report=html -v
```

Open the coverage report:

```bash
open htmlcov/index.html
```

**What this does**

* Runs all pytest tests
* Generates coverage report using `coverage.py`
* Produces detailed HTML coverage output

---

### 📊 Coverage Reports

| Component        | Tool        | Report Location                                            |
| ---------------- | ----------- | ---------------------------------------------------------- |
| Java Producers   | JaCoCo      | `java-producers/build/reports/jacoco/test/html/index.html` |
| Python Consumers | coverage.py | `python-consumers/htmlcov/index.html`                      |

---

### ✅ Tips

* Ensure **Java 21** is installed for Java tests.
* Ensure **Python 3.10+** and dependencies are installed for Python tests.
* If `open` does not work on your OS:

    * Linux: `xdg-open <file>`
    * Windows: open file manually in browser

---
