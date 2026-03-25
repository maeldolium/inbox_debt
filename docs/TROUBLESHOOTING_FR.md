#  Troubleshooting - FAQ et solutions

Questions fréquentes et solutions.

---

##  Installation et démarrage

###  `ModuleNotFoundError: No module named 'flask'`

**Symptôme :** Erreur à l'exécution

**Cause :** Dépendances non installées ou virtual env pas activé

**Solution :**

```bash
# Vérifier que le venv est activé (vous voyez (venv))
source venv/bin/activate  # Linux/macOS
# ou
.\venv\Scripts\Activate.ps1  # Windows

# Réinstaller les dépendances
pip install -r requirements.txt

# Vérifier
python -c "import flask; print('OK')"
```

---

###  `python: command not found`

**Symptôme :** Terminal ne reconnaît pas python

**Cause :** Python pas installé ou pas dans PATH

**Solution :**

```bash
# Installer Python 3.11+
# https://python.org

# Sur macOS
brew install python3

# Sur Linux (Ubuntu)
sudo apt-get install python3.11

# Vérifier
python3 --version
```

---

###  `Permission denied` au démarrage

**Symptôme :** `Permission denied` sur venv/bin/activate

**Cause :** Permissions fichier incorrectes

**Solution :**

```bash
# Linux/macOS
chmod +x venv/bin/activate
source venv/bin/activate

# Windows : utilisez powershell en admin
.\venv\Scripts\Activate.ps1
```

---

##  Lancement de l'app

###  `Address already in use`

**Symptôme :** App refuse de démarrer, port 5000 occupé

**Cause :** Autre service/app sur le port 5000

**Solution :**

```bash
# Utiliser un autre port
PORT=3000 python app/app.py

# Ou tuer le processus existant
# Linux/macOS
lsof -i :5000
kill -9 <PID>

# Windows (PowerShell admin)
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

---

###  `Page blanche / erreur 500`

**Symptôme :** `http://localhost:5000/` blank ou erreur 500

**Cause :** Erreur dans l'app ou templates manquants

**Solution :**

```bash
# Vérifier les templates existent
ls app/templates/

# Vérifier mock data
cat app/mock/mock_analysis.json

# Lancer avec logs
python app/app.py
# Voir les erreurs dans le terminal
```

---

###  `APP_MODE non reconnu`

**Symptôme :** App en mode "local" au lieu de "demo"

**Cause :** Variable d'env non correctement définie

**Solution :**

```bash
# Vérifier la variable
echo $APP_MODE  # Linux/macOS
echo %APP_MODE%  # Windows

# Définir correctement
export APP_MODE=demo  # Linux/macOS
set APP_MODE=demo     # Windows CMD
$env:APP_MODE="demo"  # Windows PowerShell

# Vérifier
echo $APP_MODE
python app/app.py

# Mode production (sans "local")
export FLASK_ENV=production
python app/app.py
```

---

##  Mode démo

###  Pas de données fictives

**Symptôme :** `/analyze` retourne une liste vide

**Cause :** `mock_analysis.json` vide ou invalide

**Solution :**

```bash
# Vérifier le fichier
cat app/mock/mock_analysis.json

# Valider le JSON
python -c "import json; json.load(open('app/mock/mock_analysis.json')); print('Valid')"

# Si erreur JSON, corriger les virgules/crochets
# Format valide :
# {
#   "domaine.com": {
#     "count": 10,
#     ...
#   }
# }
```

---

###  Mode démo détecte pas

**Symptôme :** App essaie d'accéder Gmail même en mode démo

**Cause :** APP_MODE non vraiment défini

**Solution :**

```bash
# Forcer le mode démo
APP_MODE=demo python app/app.py

# Pas d'espace autour du =
#  MAUVAIS : APP_MODE = demo
#  BON : APP_MODE=demo

# Vérifier dans l'app (terminal)
# Vous devriez voir "Mode : DEMO"
```

---

##  Tests pytest

###  `pytest: command not found`

**Symptôme :** pytest n'existe pas

**Cause :** pytest pas installé

**Solution :**

```bash
# Vérifier que venv est activé
source venv/bin/activate

# Installer pytest
pip install pytest pytest-flask

# Vérifier
pip list | grep pytest

# Lancer
pytest tests/ -v
```

---

###  Tests échouent (AssertionError)

**Symptôme :** `FAILED test_app.py::... AssertionError`

**Cause :** Logique d'app ou test incorrecte

**Solution :**

```bash
# Voir plus de détails
pytest tests/ -v --tb=long

# Lancer un test spécifique
pytest tests/test_app.py::TestBasicRoutes::test_index_responds_200 -v

# Avec logs
pytest tests/ -v -s

# Déboguer
pytest tests/ --pdb
# Entrée dans pdb pour inspecter
```

---

###  `ERROR collecting` / `SyntaxError`

**Symptôme :** Erreur dans la collection des tests

**Cause :** Erreur syntaxe en Python

**Solution :**

```bash
# Vérifier syntax
python -m py_compile tests/test_app.py

# Vérifier imports
python -c "import tests.test_app"

# Voir l'erreur complète
pytest tests/ -v --tb=short
```

---

##  Docker

###  `docker: command not found`

**Symptôme :** Docker pas trouvé

**Cause :** Docker pas installé

**Solution :**

```bash
# Installer Docker
https://docker.com/products/docker-desktop

# Vérifier
docker --version
docker run hello-world
```

---

###  Build échoue `No such file or directory`

**Symptôme :** `docker build` échoue

**Cause :** Chemin dockerfile ou fichiers manquants

**Solution :**

```bash
# Vérifier Dockerfile existe
ls Dockerfile

# Vérifier depuis bonne dir
pwd  # Vous une à la racine du projet
ls -la | grep Dockerfile

# Build avec verbeux
docker build -v -t inbox_debt .
```

---

###  Conteneur crash immédiatement

**Symptôme :** `docker run` s'arrête après démarrage

**Cause :** Erreur dans l'app ou env manquante

**Solution :**

```bash
# Voir les logs
docker logs inbox_debt_test

# Run interactif pour déboguer
docker run -it \
  -e APP_MODE=demo \
  -e PORT=8080 \
  inbox_debt:latest bash

# Ou essayer en local d'abord
python app/app.py

# Puis dans docker
docker run -p 8080:8080 -e APP_MODE=demo inbox_debt:latest
```

---

##  Jenkins / CI/CD

###  Pipeline échoue à l'installation

**Symptôme :** Stage `Install Dependencies` rouge

**Cause :** Python pas dispo ou requirements bad

**Solution :**

```bash
# Vérifier requirements.txt syntax
pip install -r requirements.txt  # Local

# Vérifier fichier
cat requirements.txt

# Peut-être problème encodage
# Relancer Jenkins
```

---

###  Tests échouent dans Jenkins

**Symptôme :** Stage `Run Tests` rouge

**Cause :** Même qu'en local

**Solution :**

```bash
# Simuler Jenkins localement
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v --tb=short

# Puis commit/push
# Jenkins redémarrera le build
```

---

###  Deploy Railway échoue

**Symptôme :** Stage `Deploy Railway` rouge

**Cause :** Token invalide ou projet pas configuré

**Solution :**

```bash
# Vérifier token Jenkins
# Jenkins → Manage → Credentials
# Chercher "railway-project-token"

# Vérifier Railway
railway login
railway link  # Lier au projet

# Tester localement
railway up --ci

# Si ok, Jenkins peut redémarrer
```

---

##  Authentification Gmail

###  `credentials.json not found`

**Symptôme :** Erreur lors du démarrage en mode local

**Cause :** Pas configuré OAuth

**Solution :**

```bash
# Mode démo : pas requiert
export APP_MODE=demo

# Mode local : créer OAuth
# 1. https://console.cloud.google.com/
# 2. Créer projet
# 3. Activer Gmail API
# 4. Créer OAuth2 "Desktop"
# 5. Télécharger JSON → app/credentials.json
# 6. Lancer app → OAuth pop-up
```

---

###  `Invalid OAuth token`

**Symptôme :** Erreur authentification Gmail

**Cause :** Token expiré ou revoké

**Solution :**

```bash
# Supprimer les tokens
rm app/token.json

# Relancer
python app/app.py

# Devrait ouvrir navigateur pour ré-auth
```

---

##  Checklist dépannage

1.  Venv activé ? (`(venv)` au terminal)
2.  Dépendances installées ? (`pip install -r requirements.txt`)
3.  Python 3.11+ ? (`python --version`)
4.  APP_MODE correct ? (`export APP_MODE=demo`)
5.  Port libre ? (`PORT=8080`)
6.  Fichiers existent ? (templates, mock data)
7.  JSON valide ? (`python -m json.tool app/mock/mock_analysis.json`)

---

##  Aide supplémentaire

-  [Installation](./INSTALLATION_FR.md)
-  [Développement](./DEVELOPMENT_FR.md)
-  [Mode démo](./DEMO_MODE_FR.md)
-  [Configuration](./CONFIGURATION_FR.md)
-  [Tests](./TESTING_FR.md)

**Toujours :**
1. Lire les logs (`terminal output`)
2. Vérifier versions (`python --version`, `pip list`)
3. Tester en démo d'abord
4. Chercher dans cette FAQ
