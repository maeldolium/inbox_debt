#  Guide de développement

Comment contribuer et développer pour Inbox Debt.

---

##  Setup environnement de développement

### 1. Cloner le repo

```bash
git clone https://github.com/votre-username/inbox_debt
cd inbox_debt
```

### 2. Créer l'env virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
.\venv\Scripts\Activate.ps1  # Windows
```

### 3. Installer avec extras de développement

```bash
pip install -r requirements.txt

# Optionnel : outils supplémentaires
pip install black flake8 pylint  # Linting/formatting
pip install ipython  # REPL amélioré
```

### 4. Lancer en mode dev

```bash
export APP_MODE=demo
export FLASK_ENV=development
python app/app.py
```

App redémarre automatiquement après changements ! 

---

##  Structure du code

```
app/
 app.py                          # Point d'entrée Flask
 auth/
    oauth_flow.py              # Authentification Gmail
 config/
    config.py                  # Classes de config
    settings.py                # APP_MODE
    safelist_manager.py        # Gestion whitelist
    safelist.json              # Données safelist
 gmail_api/
    fetch_emails.py            # Récupération mails
    actions.py                 # Suppressions
    parsers.py                 # Parsing en-têtes
 mock/
    mock_analysis.json         # Données démo
 static/
    css/
        app.css                # Styles principaux
        tokens.css             # Variables CSS
 templates/
    base.html                  # Template de base
    index.html                 # Accueil
    results.html               # Résultats analyse
    domain.html                # Détails domaine
    safelist.html              # Gestion safelist
 ux/
     ux.py                      # Logique UI
```

---

##  Workflow de développement

### 1. Créer une branche

```bash
git checkout -b feature/ma-feature
# ou
git checkout -b fix/mon-bug
```

### 2. Faire les changements

Modifiez les fichiers nécessaires.

### 3. Tester localement

```bash
# Lancer l'app
python app/app.py

# Dans une autre fenêtre, lancer les tests
pytest tests/ -v

# Vérifier la qualité du code
flake8 app/
black --check app/
```

### 4. Committer

```bash
git add .
git commit -m "feat: ajouter nouvelle fonctionnalité"
```

**Format commit :** [conventional commits](https://www.conventionalcommits.org/)
- `feat:` nouvelle fonctionnalité
- `fix:` correction de bug
- `refactor:` restructuration
- `docs:` documentation
- `test:` tests

### 5. Push et Pull Request

```bash
git push origin feature/ma-feature
```

Ouvrez une **Pull Request** sur GitHub.

---

##  Tester son code

### Lancer pytest

```bash
# Tous les tests
pytest tests/ -v

# Un fichier spécifique
pytest tests/test_app.py -v

# Un test spécifique
pytest tests/test_app.py::TestBasicRoutes::test_index_responds_200 -v

# Avec couverture
pytest --cov=app tests/
```

### Ajouter des tests

Fichier : `tests/test_app.py`

```python
def test_ma_nouvelle_route(client):
    """Test que ma nouvelle route fonctionne."""
    response = client.get('/ma-route')
    assert response.status_code == 200
    assert b'expected text' in response.data
```

Relancer : `pytest tests/ -v`

---

##  Bonnes pratiques

###  Code clean

```python
#  BON
def fetch_emails_by_domain(service, domain):
    """Récupère les emails d'un domaine spécifique."""
    query = f'from:{domain}'
    return service.users().messages().list(q=query).execute()

#  MAUVAIS
def fetch(s, d):
    q = f'from:{d}'
    return s.users().messages().list(q=q).execute()
```

###  Nommage clair

```python
#  BON
is_valid_email = True
total_emails_count = 42
unsubscribe_links = []

#  MAUVAIS
valid = True
count = 42
links = []
```

###  Docstrings

```python
def analyze_emails(service):
    """
    Analyse les emails et retourne groupage par domaine.
    
    Args:
        service: Client Gmail API
        
    Returns:
        dict: { domaine: { count, unsubscribe_links, ... } }
    """
```

###  Gestion d'erreurs

```python
try:
    emails = service.users().messages().list().execute()
except HttpError as error:
    logger.error(f"Gmail API error: {error}")
    return None
```

---

##  Outils de qualité de code

### Linting (flake8)

```bash
flake8 app/
# Signale violations PEP8
```

### Formatting (black)

```bash
black app/
# Formate automatiquement le code
```

### Type checking (mypy)

```bash
mypy app/
# Vérifie les types Python
```

Installez si besoin :
```bash
pip install black flake8 mypy
```

---

##  Développement avec Docker

### Build l'image localement

```bash
docker build -t inbox_debt:dev .
```

### Lancer avec volume (hot-reload)

```bash
docker run -d \
  --name inbox_debt_dev \
  -p 8080:8080 \
  -v $(pwd)/app:/app/app \
  -e APP_MODE=demo \
  inbox_debt:dev
```

Modifications locales = changements immédiat dans le conteneur ! 

---

##  Ajouter une dépendance

### Installer

```bash
pip install package_name
```

### Ajouter à requirements.txt

```bash
pip freeze > requirements.txt
```

### Ou manuellement

```bash
echo "package_name>=version" >> requirements.txt
```

### Commit

```bash
git add requirements.txt
git commit -m "deps: add package_name"
```

---

##  Variables d'env en développement

Créez `.env` à la racine :

```bash
APP_MODE=demo
FLASK_ENV=development
FLASK_SECRET_KEY=dev-key
DEBUG=True
```

Chargé automatiquement via `python-dotenv`.

---

##  Architecture interne

### Points d'entrée principaux

**`app/app.py`** : Routeurs Flask
```python
@app.route("/")
def index():
    """Route accueil"""
    
@app.route("/analyze")
def analyze():
    """Route analyse"""
```

**`app/gmail_api/fetch_emails.py`** : Logique Gmail
```python
def get_sorted_results():
    """Retourne emails groupés et triés"""
```

**`app/config/settings.py`** : Variables APP_MODE
```python
APP_MODE = os.getenv("APP_MODE", "local")
```

---

##  Pipeline CI/CD pour devs

À chaque push, Jenkins :

1.  Installe dépendances
2.  Lance tests
3.  Build Docker
4.  Teste conteneur
5.  Deploy si OK

Si test échoue → **pipeline s'arrête** (pas de déploiement) 

---

##  Prochaines étapes

-  [Architecture détaillée](./ARCHITECTURE_FR.md)
-  [Tests et pytest](./TESTING_FR.md)
-  [Troubleshooting](./TROUBLESHOOTING_FR.md)
