#  Troubleshooting - FAQ & Solutions

Frequently asked questions and solutions.

---

##  Installation and startup

###  `ModuleNotFoundError: No module named 'flask'`

**Symptom:** Error at runtime

**Cause:** Dependencies not installed or virtual env not activated

**Solution:**

```bash
# Verify venv is activated (you should see (venv))
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\Activate.ps1  # Windows

# Reinstall dependencies
pip install -r requirements.txt

# Verify
python -c "import flask; print('OK')"
```

---

###  `python: command not found`

**Symptom:** Terminal doesn't recognize python

**Cause:** Python not installed or not in PATH

**Solution:**

```bash
# Install Python 3.11+
# https://python.org

# On macOS
brew install python3

# On Linux (Ubuntu)
sudo apt-get install python3.11

# Verify
python3 --version
```

---

###  `Permission denied` on startup

**Symptom:** `Permission denied` on venv/bin/activate

**Cause:** Incorrect file permissions

**Solution:**

```bash
# Linux/macOS
chmod +x venv/bin/activate
source venv/bin/activate

# Windows: use PowerShell as admin
.\venv\Scripts\Activate.ps1
```

---

##  Running the app

###  `Address already in use`

**Symptom:** App refuses to start, port 5000 is busy

**Cause:** Another service/app on port 5000

**Solution:**

```bash
# Use different port
PORT=3000 python app/app.py

# Or kill existing process
# Linux/macOS
lsof -i :5000
kill -9 <PID>

# Windows (PowerShell admin)
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

---

###  `Blank page / error 500`

**Symptom:** `http://localhost:5000/` blank or 500 error

**Cause:** Error in app or missing templates

**Solution:**

```bash
# Verify templates exist
ls app/templates/

# Verify mock data
cat app/mock/mock_analysis.json

# Run with logs
python app/app.py
# Watch for errors in terminal
```

---

###  `APP_MODE` not recognized

**Symptom:** App in "local" mode instead of "demo"

**Cause:** Environment variable not correctly set

**Solution:**

```bash
# Verify variable
echo $APP_MODE  # Linux/macOS
echo %APP_MODE%  # Windows

# Set correctly
export APP_MODE=demo  # Linux/macOS
set APP_MODE=demo     # Windows CMD
$env:APP_MODE="demo"  # Windows PowerShell

# Verify
echo $APP_MODE
python app/app.py

# Production mode (without "local")
export FLASK_ENV=production
python app/app.py
```

---

##  Demo mode

###  No sample data

**Symptom:** `/analyze` returns empty list

**Cause:** `mock_analysis.json` empty or invalid

**Solution:**

```bash
# Check file
cat app/mock/mock_analysis.json

# Validate JSON
python -c "import json; json.load(open('app/mock/mock_analysis.json')); print('Valid')"

# If JSON error, fix commas/brackets
# Valid format:
# {
#   "domain.com": {
#     "count": 10,
#     ...
#   }
# }
```

---

###  Demo mode not detected

**Symptom:** App tries to access Gmail even in demo mode

**Cause:** APP_MODE not really set

**Solution:**

```bash
# Force demo mode
APP_MODE=demo python app/app.py

# No spaces around =
#  WRONG: APP_MODE = demo
#  RIGHT: APP_MODE=demo

# Verify in app (terminal)
# You should see "Mode: DEMO"
```

---

##  Pytest tests

###  `pytest: command not found`

**Symptom:** pytest doesn't exist

**Cause:** pytest not installed

**Solution:**

```bash
# Verify venv is activated
source venv/bin/activate

# Install pytest
pip install pytest pytest-flask

# Verify
pip list | grep pytest

# Run
pytest tests/ -v
```

---

###  Tests fail (AssertionError)

**Symptom:** `FAILED test_app.py::... AssertionError`

**Cause:** Incorrect app logic or test

**Solution:**

```bash
# See more details
pytest tests/ -v --tb=long

# Run specific test
pytest tests/test_app.py::TestBasicRoutes::test_index_responds_200 -v

# With logs
pytest tests/ -v -s

# Debug
pytest tests/ --pdb
# Enter pdb to inspect
```

---

###  `ERROR collecting` / `SyntaxError`

**Symptom:** Error in test collection

**Cause:** Python syntax error

**Solution:**

```bash
# Check syntax
python -m py_compile tests/test_app.py

# Check imports
python -c "import tests.test_app"

# See full error
pytest tests/ -v --tb=short
```

---

##  Docker

###  `docker: command not found`

**Symptom:** Docker not found

**Cause:** Docker not installed

**Solution:**

```bash
# Install Docker
https://docker.com/products/docker-desktop

# Verify
docker --version
docker run hello-world
```

---

###  Build fails `No such file or directory`

**Symptom:** `docker build` fails

**Cause:** Missing Dockerfile or files

**Solution:**

```bash
# Verify Dockerfile exists
ls Dockerfile

# Verify you're in right directory
pwd  # Should be at project root
ls -la | grep Dockerfile

# Build with verbose
docker build -v -t inbox_debt .
```

---

###  Container crashes immediately

**Symptom:** `docker run` stops after startup

**Cause:** Error in app or missing env

**Solution:**

```bash
# See logs
docker logs inbox_debt_test

# Run interactive to debug
docker run -it \
  -e APP_MODE=demo \
  -e PORT=8080 \
  inbox_debt:latest bash

# Or test locally first
python app/app.py

# Then in docker
docker run -p 8080:8080 -e APP_MODE=demo inbox_debt:latest
```

---

##  Jenkins / CI/CD

###  Pipeline fails at install

**Symptom:** `Install Dependencies` stage red

**Cause:** Python unavailable or bad requirements

**Solution:**

```bash
# Verify requirements.txt syntax locally
pip install -r requirements.txt

# Check file
cat requirements.txt

# May be encoding issue
# Restart Jenkins
```

---

###  Tests fail in Jenkins

**Symptom:** `Run Tests` stage red

**Cause:** Same as local

**Solution:**

```bash
# Simulate Jenkins locally
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v --tb=short

# Then commit/push
# Jenkins will restart build
```

---

###  Railway deployment fails

**Symptom:** `Deploy Railway` stage red

**Cause:** Invalid token or project not configured

**Solution:**

```bash
# Verify Jenkins token
# Jenkins → Manage → Credentials
# Look for "railway-project-token"

# Verify Railway
railway login
railway link  # Link to project

# Test locally
railway up --ci

# If ok, Jenkins can restart
```

---

##  Gmail Authentication

###  `credentials.json not found`

**Symptom:** Error on startup in local mode

**Cause:** OAuth not configured

**Solution:**

```bash
# Demo mode: not required
export APP_MODE=demo

# Local mode: create OAuth
# 1. https://console.cloud.google.com/
# 2. Create project
# 3. Enable Gmail API
# 4. Create OAuth2 "Desktop"
# 5. Download JSON → app/credentials.json
# 6. Run app → OAuth pop-up
```

---

###  `Invalid OAuth token`

**Symptom:** Gmail authentication error

**Cause:** Token expired or revoked

**Solution:**

```bash
# Delete tokens
rm app/token.json

# Restart
python app/app.py

# Should open browser for re-auth
```

---

##  Troubleshooting checklist

1.  Venv activated? (`(venv)` in terminal)
2.  Dependencies installed? (`pip install -r requirements.txt`)
3.  Python 3.11+? (`python --version`)
4.  APP_MODE correct? (`export APP_MODE=demo`)
5.  Port free? (`PORT=8080`)
6.  Files exist? (templates, mock data)
7.  JSON valid? (`python -m json.tool app/mock/mock_analysis.json`)

---

##  More help

-  [Installation](./INSTALLATION_EN.md)
-  [Development](./DEVELOPMENT_EN.md)
-  [Demo Mode](./DEMO_MODE_EN.md)
-  [Configuration](./CONFIGURATION_EN.md)
-  [Tests](./TESTING_EN.md)

**Always:**
1. Read the logs (terminal output)
2. Verify versions (`python --version`, `pip list`)
3. Test in demo first
4. Search this FAQ
