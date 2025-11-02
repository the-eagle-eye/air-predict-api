# 🧪 Testing Guide - CR310 Datalogger API

Complete guide for running and understanding the test suite.

---

## 🚀 Quick Start

### Run All Tests
```bash
./run_tests.sh
```

### Run with Coverage
```bash
./run_tests.sh coverage
```

---

## 📋 Test Suite Overview

The test suite includes **25 comprehensive tests** organized into 6 test classes:

### 1. TestHealthEndpoints (2 tests)
- ✅ Root endpoint (`/`)
- ✅ Health check endpoint (`/health`)

### 2. TestPostReadings (8 tests)
- ✅ Valid reading for T101
- ✅ Valid reading for T102
- ✅ Duplicate detection
- ✅ Missing required fields
- ✅ Out of range values
- ✅ Invalid timestamp format
- ✅ Empty equipment ID
- ✅ Null values

### 3. TestGetReadings (7 tests)
- ✅ Get all readings
- ✅ Filter by equipment
- ✅ Pagination support
- ✅ Date range filtering
- ✅ Combined filters
- ✅ Invalid parameters
- ✅ Non-existent equipment

### 4. TestDataValidation (2 tests)
- ✅ Equipment ID normalization (lowercase → uppercase)
- ✅ Numeric precision (rounding to 2 decimals)

### 5. TestResponseTime (2 tests)
- ✅ POST response < 1 second
- ✅ GET response < 1 second

### 6. TestErrorHandling (3 tests)
- ✅ Invalid JSON structure
- ✅ Wrong data types
- ✅ Invalid query parameters

---

## 🎯 Running Tests

### Basic Commands

```bash
# Run all tests with verbose output
pytest test_api.py -v

# Run with test runner script
./run_tests.sh

# Run specific test class
pytest test_api.py::TestPostReadings -v

# Run specific test
pytest test_api.py::TestPostReadings::test_post_valid_reading_t101 -v

# Run tests matching pattern
pytest test_api.py -k "post" -v
```

### Advanced Options

```bash
# Coverage report
./run_tests.sh coverage
# Or directly:
pytest test_api.py -v --cov=. --cov-report=html --cov-report=term-missing

# Fast mode (less verbose)
./run_tests.sh fast

# Verbose mode (detailed output)
./run_tests.sh verbose

# Stop on first failure
pytest test_api.py -x

# Show local variables on failure
pytest test_api.py -l

# Run last failed tests only
pytest test_api.py --lf
```

---

## 📊 Understanding Test Output

### Successful Test
```
test_api.py::TestPostReadings::test_post_valid_reading_t101 PASSED [10%]
```

### Failed Test
```
test_api.py::TestPostReadings::test_post_duplicate_reading FAILED [20%]
```

### Test Summary
```
==================== 25 passed in 2.45s ====================
```

---

## 🔍 Test Details

### Fixtures Used

**`valid_reading_t101`** - Valid CR310 reading for equipment T101
**`valid_reading_t102`** - Valid CR310 reading for equipment T102
**`reading_missing_fields`** - Reading with missing required fields
**`reading_out_of_range`** - Reading with values outside valid ranges
**`cleanup_test_data`** - Automatic cleanup before/after tests

### Test Database Cleanup

Tests automatically clean up data for equipment T101, T102, T103:
- **Before tests**: Removes any existing test data
- **After tests**: Removes all test data created during testing

This ensures tests are:
- ✅ Isolated (don't affect each other)
- ✅ Repeatable (same results every time)
- ✅ Clean (no leftover data)

---

## 🛠️ Troubleshooting

### MongoDB Not Running

**Error**: Database connection unavailable

**Solution**:
```bash
# Start MongoDB
brew services start mongodb-community

# Or with Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### Import Errors

**Error**: ModuleNotFoundError

**Solution**:
```bash
# Make sure virtual environment is activated
source bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Tests Failing Due to Existing Data

**Error**: Duplicate reading detected

**Solution**:
```bash
# Clean test data manually
mongosh
use datalogger_db
db.cr310_readings.deleteMany({"equipo": {$in: ["T101", "T102", "T103"]}})
```

---

## 📈 Coverage Reports

### Generate HTML Coverage Report

```bash
./run_tests.sh coverage
```

This creates:
- `htmlcov/index.html` - Interactive HTML report
- Terminal output with coverage percentage

### View Coverage Report

```bash
# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html
```

---

## ✅ Best Practices

### Writing New Tests

1. **Use descriptive names**: `test_post_valid_reading_succeeds`
2. **One assertion per test** (when possible)
3. **Use fixtures** for common test data
4. **Clean up** after tests
5. **Test edge cases** and error conditions

### Example New Test

```python
def test_post_reading_with_special_characters(self):
    """Test POST reading with special characters in equipo"""
    reading = {
        "equipo": "T-101-A",  # Special characters
        "SO2_ppb": 25.43,
        # ... rest of fields
        "timestamp": "2025-10-28 10:00:00"
    }
    
    response = client.post("/api/v1/readings", json=reading)
    assert response.status_code == 200
```

---

## 🎓 Test Organization

Tests are organized by functionality:

```
test_api.py
├── TestHealthEndpoints      # Basic health checks
├── TestPostReadings         # POST endpoint validation
├── TestGetReadings          # GET endpoint functionality
├── TestDataValidation       # Data preprocessing
├── TestResponseTime         # Performance requirements
└── TestErrorHandling        # Error scenarios
```

---

## 📝 Continuous Integration

### GitHub Actions (Example)

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      mongodb:
        image: mongo:latest
        ports:
          - 27017:27017
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest test_api.py -v --cov=.
```

---

## 💡 Tips

1. **Run tests frequently** during development
2. **Check coverage** to identify untested code
3. **Use `-k` flag** to run specific test patterns
4. **Add tests** when fixing bugs
5. **Keep tests fast** by mocking external dependencies

---

## 🔗 Resources

- **Pytest Documentation**: https://docs.pytest.org/
- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **Coverage.py**: https://coverage.readthedocs.io/

---

**Need help?** Check the main [README.md](README.md) for project documentation.

