#  Tests and pytest

Complete testing guide.

---

##  Overview

**11 pytest tests** validating essential features in demo mode.

```bash
tests/
 conftest.py      # pytest configuration
 test_app.py      # Complete suite (11 tests)
```

---

##  Run tests

### All tests

```bash
pytest tests/ -v
```

Result:
```
tests/test_app.py::TestBasicRoutes::test_index_responds_200 PASSED
tests/test_app.py::TestBasicRoutes::test_index_returns_html PASSED
tests/test_app.py::TestAnalyzeRoute::test_analyze_get_responds_200 PASSED
... (11 total)
============================= 11 passed in X.XXs ==============================
```

### Specific tests

```bash
# Entire class
pytest tests/test_app.py::TestBasicRoutes -v

# Single test
pytest tests/test_app.py::TestBasicRoutes::test_index_responds_200 -v

# With pattern
pytest tests/ -k "test_analyze" -v
```

### With coverage report

```bash
pytest tests/ --cov=app --cov-report=html
# Generates report in htmlcov/
```

### Verbose vs quiet

```bash
pytest tests/ -v      # Detailed
pytest tests/         # Normal
pytest tests/ -q      # Short
```

---

##  Test suite

### 1. **TestBasicRoutes** (2 tests)

Verify basic routes:

```python
def test_index_responds_200(client):
    """Test that / responds with 200."""
    response = client.get('/')
    assert response.status_code == 200
    
def test_index_returns_html(client):
    """Test that / returns HTML."""
    response = client.get('/')
    assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data
```

**What we test:**
-  Route `/` exists
-  No error (200)
-  Returns valid HTML

---

### 2. **TestAnalyzeRoute** (3 tests)

Verify analyze route:

```python
def test_analyze_get_responds_200(client):
    """Test that /analyze (GET) responds with 200."""
    response = client.get('/analyze')
    assert response.status_code == 200
    
def test_analyze_post_responds_200(client):
    """Test that /analyze (POST) responds with 200."""
    response = client.post('/analyze')
    assert response.status_code == 200
    
def test_analyze_returns_data(client):
    """Test that /analyze returns sample data."""
    response = client.get('/analyze')
    assert response.status_code == 200
    assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data
```

**What we test:**
-  GET and POST work
-  No errors
-  Returns content

---

### 3. **TestDomainDetailRoute** (2 tests)

Verify domain details view:

```python
def test_domain_detail_with_valid_domain(client):
    """Test domain route with valid domain."""
    client.get('/analyze')
    mock_data = load_mock_data()
    
    if mock_data:
        first_domain = list(mock_data.keys())[0]
        response = client.get(f'/domain/{first_domain}')
        assert response.status_code == 200
    
def test_domain_detail_with_invalid_domain(client):
    """Test domain route with invalid domain."""
    response = client.get('/domain/invalid_domain_that_does_not_exist')
    assert response.status_code in [200, 404]
```

**What we test:**
-  Valid domain → 200
-  Invalid domain → 200 or 404

---

### 4. **TestSafelistManagement** (2 tests)

Verify safelist management:

```python
def test_safelist_view_responds_200(client):
    """Test that /safelist (view) responds with 200."""
    response = client.get('/safelist')
    assert response.status_code == 200
    
def test_safelist_post_succeeds_in_demo(client):
    """Test that adding to safelist works in demo mode."""
    client.get('/analyze')
    mock_data = load_mock_data()
    
    if mock_data:
        first_domain = list(mock_data.keys())[0]
        response = client.post('/safelist', data={'domain': first_domain})
        assert response.status_code == 200
        assert b'safelist' in response.data.lower()
```

**What we test:**
-  Safelist view returns 200
-  POST add domain returns message

---

### 5. **TestMockDataLoading** (2 tests)

Verify sample data:

```python
def test_mock_data_loads(self):
    """Test that sample data loads."""
    mock_data = load_mock_data()
    
    assert isinstance(mock_data, dict)
    assert len(mock_data) > 0
    
def test_mock_data_has_required_fields(self):
    """Test that sample data has required fields."""
    mock_data = load_mock_data()
    
    for domain, data in mock_data.items():
        assert isinstance(domain, str)
        assert isinstance(data, dict)
        assert 'count' in data
```

**What we test:**
-  Mock data loads without error
-  Valid structure (dict)
-  Required fields present

---

##  pytest fixture

```python
@pytest.fixture
def client():
    """Configure Flask test client."""
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client
```

**What it does:**
- Creates Flask test client
- TESTING mode enabled
- No real server
- Reused for each test

---

##  Add tests

### Structure

```python
class TestMyFeature:
    """Tests for my feature."""
    
    def test_case_1(self, client):
        """First condition."""
        response = client.get('/my-route')
        assert response.status_code == 200
    
    def test_case_2(self, client):
        """Second condition."""
        response = client.post('/my-route', data={'key': 'value'})
        assert response.status_code in [200, 201]
```

### Add to tests/test_app.py

```python
class TestMyFeature:
    
    def test_new_route(self, client):
        """Test the new route."""
        response = client.get('/new-route')
        assert response.status_code == 200
        assert b'expected content' in response.data
```

Run:
```bash
pytest tests/test_app.py::TestMyFeature::test_new_route -v
```

---

##  Useful assertions

```python
# Status codes
assert response.status_code == 200
assert response.status_code in [200, 201]

# HTML content
assert b'text content' in response.data
assert b'<!DOCTYPE html>' in response.data

# Redirects
assert response.status_code == 302
assert response.location == '/expected-url'

# JSON
data = json.loads(response.data)
assert data['key'] == 'value'

# Exceptions
with pytest.raises(ValueError):
    do_something()
```

---

##  Debug tests

### Show stdout

```bash
pytest tests/ -v -s
# -s shows print() statements
```

### Stop at first failure

```bash
pytest tests/ -x
# Stops at first failed test
```

### Interactive debug

```bash
pytest tests/ --pdb
# Launches pdb on error
```

### Show logs

```bash
pytest tests/ -v --tb=short
# More detail on errors
```

---

##  CI/CD Jenkins

Tests run on every push:

```
Stage 1: Install Dependencies
         ↓
Stage 2: Run Tests (pytest) ← **YOU ARE HERE**
         ↓ (if ok)
Stage 3: Build Docker
    ...
```

### Command run

```bash
. venv/bin/activate
pytest tests/ -v --tb=short
```

**If pytest fails:**
- Exit code != 0
- Pipeline stops
- Error email sent
- Railway deploy cancelled

---

##  Tests checklist

- [ ] All tests pass locally
- [ ] `pytest tests/ -v` = 11 passed
- [ ] Code coverage if possible
- [ ] New tests for new features
- [ ] Tests in demo mode only
- [ ] pytest dependencies installed

---

##  Next steps

-  [Troubleshooting](./TROUBLESHOOTING_EN.md)
-  [Configuration](./CONFIGURATION_EN.md)
-  [Development](./DEVELOPMENT_EN.md)
