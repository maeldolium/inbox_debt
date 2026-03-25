#  Configuration & Variables d'environnement

Tous les paramètres de configuration pour Inbox Debt.

---

##  Variables d'environnement

### Essentielles

| Variable | Valeur | Ex. | Obligatoire ? |
|----------|--------|-----|---|
| `APP_MODE` | `demo` ou `local` | `demo` |  Oui |
| `FLASK_ENV` | `development` / `production` / `testing` | `production` |  Oui |
| `FLASK_SECRET_KEY` | Clé secrète complexe | `abc123xyz...` |  En prod |
| `PORT` | Port écoute | `8080` |  Optionnel |

### Optionnelles

| Variable | Valeur | Ex. | Défaut |
|----------|--------|-----|--------|
| `LOG_LEVEL` | `DEBUG` / `INFO` / `ERROR` | `DEBUG` | `INFO` |
| `SESSION_TIMEOUT` | Minutes avant expiration | `60` | `30` |

---

##  Configuration par environnement

### Mode démo (aucune authent Gmail)

```bash
export APP_MODE=demo
export FLASK_ENV=development
export PORT=5000

python app/app.py
```

**Accès :** http://localhost:5000

---

### Mode développement (Gmail OAuth requis)

```bash
export APP_MODE=local
export FLASK_ENV=development
export FLASK_SECRET_KEY=dev-key-insecure
export PORT=5000

python app/app.py
```

**Requis :** Fichiers OAuth (`credentials.json`, `token.json`)

---

### Mode production (Gmail OAuth + sécurisé)

```bash
export APP_MODE=local
export FLASK_ENV=production
export FLASK_SECRET_KEY=clé_très_longue_et_complexe_minimum_32_caractères
export PORT=8080

python app/app.py
```

**Requis :**
-  `FLASK_SECRET_KEY` robuste (min 32 caractères aléatoires)
-  OAuth credentials
-  HTTPS activé
-  Variables d'env sécurisées

---

##  Fichier `.env` (Développement)

Créez un `.env` à la racine du projet :

```bash
# Mode
APP_MODE=demo
FLASK_ENV=development
PORT=5000

# Secret (dev seulement !)
FLASK_SECRET_KEY=dev-temporary-key-not-secure

# Logging
LOG_LEVEL=DEBUG
```

Chargement automatique via `python-dotenv` dans `app/config/config.py`

 **Ne committez JAMAIS `.env` en production !** Utilisez les secrets Docker/Kubernetes.

---

##  Générer une clé secrète Flask

### Bash/Linux/macOS

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### PowerShell (Windows)

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Exemple résultat :
```
a3f9e8b7c2d4e1f6a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e
```

---

##  Configuration Docker

### Variables dans `docker run`

```bash
docker run -d \
  --name inbox_debt \
  -p 8080:8080 \
  -e APP_MODE=demo \
  -e FLASK_ENV=development \
  -e PORT=8080 \
  inbox_debt:latest
```

### Via fichier `.env.docker`

```bash
docker run -d \
  --name inbox_debt \
  -p 8080:8080 \
  --env-file .env.docker \
  inbox_debt:latest
```

Contenu `.env.docker` :
```
APP_MODE=local
FLASK_ENV=production
FLASK_SECRET_KEY=votre_clé_production
PORT=8080
```

---

##  Déploiement Railway

Variables d'environnement sur Railway :

1. Dashbord Railway
2. Project → Service → Variables
3. Ajouter :

```
APP_MODE=local
FLASK_ENV=production
FLASK_SECRET_KEY=<clé robuste>
PORT=8080
```

Railway injecte automatiquement les dépendances service-to-service.

---

##  Configuration Flask interne

Fichier : `app/config/config.py`

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
    # Validation obligatoire de SECRET_KEY
```

---

##  OAuth Gmail Configuration

### Fichiers requis

```
app/
 credentials.json    # Téléchargé depuis Google Cloud Console
 token.json          # Auto-généré à la 1ère authentification
```

### Obtenir credentials.json

1. https://console.cloud.google.com/
2. Créer un projet
3. Activer Gmail API
4. Créer un OAuth2 "Desktop App"
5. Télécharger JSON → `app/credentials.json`

### Token auto-généré

À la première connexion OAuth :
- L'app crée `app/token.json`
- Contient les tokens d'accès
- Rafraîchi automatiquement

---

##  Configuration pytest

Fichier : `pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

Fichier : `tests/conftest.py`

```python
os.environ['APP_MODE'] = 'demo'
os.environ['FLASK_ENV'] = 'testing'
```

Tests tournent en mode démo automatiquement.

---

##  Configuration dépannage

###  Secret key requise en production

**Erreur :**
```
ConfigError: FLASK_SECRET_KEY must be set in production!
```

**Solution :**
```bash
export FLASK_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
python app/app.py
```

---

###  `APP_MODE` invalide

**Erreur :**
```
APP_MODE doit être "local" ou "demo"
```

**Solution :**
```bash
export APP_MODE=demo  # valide
# ou
export APP_MODE=local  # valide

# Mauvais :
export APP_MODE=prod  # 
```

---

###  Port déjà utilisé

**Erreur :**
```
Address already in use
```

**Solution :**
```bash
# Utiliser un autre port
PORT=3000 python app/app.py

# Ou tuer le processus
lsof -i :5000  # Linux/macOS
# Trouver le PID et tuer
kill -9 <PID>
```

---

##  Prochaines étapes

-  [Développement](./DEVELOPMENT_FR.md) - Setup environnement dev
-  [Architecture](./ARCHITECTURE_FR.md) - Structure du code
-  [Troubleshooting](./TROUBLESHOOTING_FR.md) - FAQ
