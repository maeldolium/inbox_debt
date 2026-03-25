#  Configuration & Environment Variables

All configuration parameters for Inbox Debt.

---

##  Environment Variables

### Essential

| Variable | Value | Example | Required? |
|----------|-------|---------|-----------|
| `APP_MODE` | `demo` or `local` | `demo` |  Yes |
| `FLASK_ENV` | `development` / `production` / `testing` | `production` |  Yes |
| `FLASK_SECRET_KEY` | Complex secret key | `abc123xyz...` |  In prod |
| `PORT` | Listen port | `8080` |  Optional |

### Optional

| Variable | Value | Example | Default |
|----------|-------|---------|---------|
| `LOG_LEVEL` | `DEBUG` / `INFO` / `ERROR` | `DEBUG` | `INFO` |
| `SESSION_TIMEOUT` | Minutes before expiry | `60` | `30` |

---

##  Configuration by environment

### Demo mode (no Gmail auth)

```bash
export APP_MODE=demo
export FLASK_ENV=development
export PORT=5000

python app/app.py
```

**Access:** http://localhost:5000

---

### Development mode (Gmail OAuth required)

```bash
export APP_MODE=local
export FLASK_ENV=development
export FLASK_SECRET_KEY=dev-key-insecure
export PORT=5000

python app/app.py
```

**Required:** OAuth files (`credentials.json`, `token.json`)

---

### Production mode (Gmail OAuth + secure)

```bash
export APP_MODE=local
export FLASK_ENV=production
export FLASK_SECRET_KEY=very_long_complex_key_minimum_32_chars
export PORT=8080

python app/app.py
```

**Required:**
-  Robust `FLASK_SECRET_KEY` (min 32 random chars)
-  OAuth credentials
-  HTTPS enabled
-  Secure environment variables

---

##  .env file (Development)

Create a `.env` at project root:

```bash
# Mode
APP_MODE=demo
FLASK_ENV=development
PORT=5000

# Secret (dev only!)
FLASK_SECRET_KEY=dev-temporary-key-not-secure

# Logging
LOG_LEVEL=DEBUG
```

Auto-loaded via `python-dotenv` in `app/config/config.py`

 **Never commit `.env` in production!** Use Docker/Kubernetes secrets.

---

##  Generate Flask secret key

### Bash/Linux/macOS

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### PowerShell (Windows)

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Example output:
```
a3f9e8b7c2d4e1f6a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e
```

---

##  Docker Configuration

### Variables in `docker run`

```bash
docker run -d \
  --name inbox_debt \
  -p 8080:8080 \
  -e APP_MODE=demo \
  -e FLASK_ENV=development \
  -e PORT=8080 \
  inbox_debt:latest
```

### Via `.env.docker` file

```bash
docker run -d \
  --name inbox_debt \
  -p 8080:8080 \
  --env-file .env.docker \
  inbox_debt:latest
```

Content `.env.docker`:
```
APP_MODE=local
FLASK_ENV=production
FLASK_SECRET_KEY=your_production_key
PORT=8080
```

---

##  Railway Deployment

Environment variables on Railway:

1. Dashboard Railway
2. Project → Service → Variables
3. Add:

```
APP_MODE=local
FLASK_ENV=production
FLASK_SECRET_KEY=<robust key>
PORT=8080
```

Railway automatically injects service-to-service dependencies.

---

##  Internal Flask Configuration

File: `app/config/config.py`

```python
class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    APP_MODE = os.getenv("APP_MODE", "local").lower()
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = FLASK_ENV == "development"
    SESSION_COOKIE_SECURE = FLASK_ENV == "production"

class ProductionConfig(Config):
    DEBUG = False
    FLASK_ENV = "production"
    # Mandatory SECRET_KEY validation
```

---

##  Gmail OAuth Configuration

### Required files

```
app/
 credentials.json    # Downloaded from Google Cloud Console
 token.json          # Auto-generated at first auth
```

### Get credentials.json

1. https://console.cloud.google.com/
2. Create a project
3. Enable Gmail API
4. Create OAuth2 "Desktop App"
5. Download JSON → `app/credentials.json`

### Auto-generated token

At first OAuth login:
- App creates `app/token.json`
- Contains access tokens
- Auto-refreshed

---

##  pytest Configuration

File: `pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

File: `tests/conftest.py`

```python
os.environ['APP_MODE'] = 'demo'
os.environ['FLASK_ENV'] = 'testing'
```

Tests run in demo mode automatically.

---

##  Configuration troubleshooting

###  Secret key required in production

**Error:**
```
ConfigError: FLASK_SECRET_KEY must be set in production!
```

**Solution:**
```bash
export FLASK_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
python app/app.py
```

---

###  Invalid `APP_MODE`

**Error:**
```
APP_MODE must be "local" or "demo"
```

**Solution:**
```bash
export APP_MODE=demo  # valid
# or
export APP_MODE=local  # valid

# Wrong:
export APP_MODE=prod  # 
```

---

###  Port already in use

**Error:**
```
Address already in use
```

**Solution:**
```bash
# Use different port
PORT=3000 python app/app.py

# Or kill existing process
lsof -i :5000  # Linux/macOS
# Find PID and kill
kill -9 <PID>
```

---

##  Next steps

-  [Development](./DEVELOPMENT_EN.md) - Setup dev environment
-  [Architecture](./ARCHITECTURE_EN.md) - Code structure
-  [Troubleshooting](./TROUBLESHOOTING_EN.md) - FAQ
