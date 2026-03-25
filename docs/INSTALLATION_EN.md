#  Installation - Detailed Guide

## Prerequisites

Before starting, make sure you have:

- **Python 3.11+** → [Download](https://python.org)
- **pip** (comes with Python)
- **Git** (optional, to clone repo) → [Download](https://git-scm.com)
- **Docker** (optional, for containerization) → [Download](https://docker.com)

### Verify Python

```bash
python --version
# or
python3 --version
```

---

##  Local Installation

### Step 1: Clone the repository

```bash
git clone https://github.com/your-username/inbox_debt
cd inbox_debt
```

Or download the ZIP from GitHub.

### Step 2: Create virtual environment

**On Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

 You should see `(venv)` at the start of your terminal.

### Step 3: Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

##  Run the application

### Demo mode (no Gmail auth required)

```bash
export APP_MODE=demo
python app/app.py
```

**Windows:**
```powershell
$env:APP_MODE="demo"
python app/app.py
```

Open http://localhost:5000 in your browser.

### Production mode (with Gmail OAuth)

```bash
export FLASK_ENV=production
export FLASK_SECRET_KEY=your_complex_secret_key
export APP_MODE=local
python app/app.py
```

---

##  Installation with Docker

### Build the image

```bash
docker build -t inbox_debt:latest .
```

### Run in demo mode

```bash
docker run -d \
  --name inbox_debt_demo \
  -p 8080:8080 \
  -e APP_MODE=demo \
  -e PORT=8080 \
  inbox_debt:latest
```

Check: http://localhost:8080

### Stop the container

```bash
docker stop inbox_debt_demo
docker rm inbox_debt_demo
```

---

##  Install development tools

If you want to **develop** or **test**:

```bash
# Tests are already in requirements.txt
# But you can install them separately:
pip install pytest pytest-flask

# Run tests
pytest tests/ -v
```

---

##  Verify installation

```bash
# 1. Check Python
python --version

# 2. Check venv activated
which python  # (Linux/macOS)
# or
where python  # (Windows)

# 3. Check pip
pip list | grep Flask

# 4. Run app in demo
python app/app.py

# 5. Open http://localhost:5000
```

---

##  Installation troubleshooting

###  `ModuleNotFoundError: No module named 'flask'`

**Solution:**
- Verify venv is activated (you should see `(venv)` in terminal)
- Reinstall dependencies: `pip install -r requirements.txt`

###  `python: command not found`

**Solution:**
- You don't have Python installed
- Download from https://python.org
- On macOS/Linux: `brew install python3`

###  `Permission denied` (Linux/macOS)

**Solution:**
```bash
chmod +x venv/bin/activate
source venv/bin/activate
```

---

##  Post-installation checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (pip install -r requirements.txt)
- [ ] App runs in demo (python app/app.py)
- [ ] Interface accessible on http://localhost:5000
- [ ] Tests pass (pytest tests/ -v)

---

##  Secrets and configuration keys

### Important environment variables

```bash
# Demo mode (no Gmail)
APP_MODE=demo

# Flask secret key (development)
FLASK_SECRET_KEY=dev-key-123

# Production
FLASK_ENV=production
FLASK_SECRET_KEY=very_complex_and_secure_key

# Custom port
PORT=3000  # instead of 5000
```

 See [CONFIGURATION_EN.md](./CONFIGURATION_EN.md) for more details

---

##  Next steps

- Read the [Quick Start Guide](./QUICK_START_EN.md)
- Explore [Demo Mode](./DEMO_MODE_EN.md)
- Check [User Guide](./USAGE_EN.md)
