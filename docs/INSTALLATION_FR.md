#  Installation - Guide détaillé

## Prérequis

Avant de commencer, vérifiez que vous avez :

- **Python 3.11+** → [Télécharger](https://python.org)
- **pip** (livré avec Python)
- **Git** (optionnel, pour cloner le repo) → [Télécharger](https://git-scm.com)
- **Docker** (optionnel, pour containeriser) → [Télécharger](https://docker.com)

### Vérifier votre Python

```bash
python --version
# ou
python3 --version
```

---

##  Installation locale

### Étape 1 : Cloner le repository

```bash
git clone https://github.com/votre-usernameINCBOX_DEBT
cd inbox_debt
```

Ou téléchargez le ZIP depuis GitHub.

### Étape 2 : Créer un environnement virtuel

**Sur Linux/macOS :**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Sur Windows (PowerShell) :**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Sur Windows (CMD) :**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

 Vous devriez voir `(venv)` au début de votre terminal.

### Étape 3 : Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

##  Lancer l'application

### Mode démo (aucune authent Gmail requise)

```bash
export APP_MODE=demo
python app/app.py
```

**Windows :**
```powershell
$env:APP_MODE="demo"
python app/app.py
```

Ouvrez http://localhost:5000 dans votre navigateur.

### Mode production (avec Gmail OAuth)

```bash
export FLASK_ENV=production
export FLASK_SECRET_KEY=votre_cle_secrete_complexe
export APP_MODE=local
python app/app.py
```

---

##  Installation avec Docker

### Build l'image

```bash
docker build -t inbox_debt:latest .
```

### Lancer en mode démo

```bash
docker run -d \
  --name inbox_debt_demo \
  -p 8080:8080 \
  -e APP_MODE=demo \
  -e PORT=8080 \
  inbox_debt:latest
```

Vérifiez : http://localhost:8080

### Arrêter le conteneur

```bash
docker stop inbox_debt_demo
docker rm inbox_debt_demo
```

---

##  Installer les outils de développement

Si vous voulez **développer** ou **tester** :

```bash
# Les tests sont déjà dans requirements.txt
# Mais vous pouvez les installer séparément :
pip install pytest pytest-flask

# Lancer les tests
pytest tests/ -v
```

---

##  Vérifier l'installation

```bash
# 1. Vérifier Python
python --version

# 2. Vérifier le venv activé
which python  # (Linux/macOS)
# ou
where python  # (Windows)

# 3. Vérifier pip
pip list | grep Flask

# 4. Lancer l'app en démo
python app/app.py

# 5. Ouvrir http://localhost:5000
```

---

##  Dépannage d'installation

###  `ModuleNotFoundError: No module named 'flask'`

**Solution :**
- Vérifiez que le venv est activé (vous devez voir `(venv)` dans le terminal)
- Réinstallez les dépendances : `pip install -r requirements.txt`

###  `python: command not found`

**Solution :**
- Vous n'avez pas Python installé
- Téléchargez depuis https://python.org
- Sur macOS/Linux : `brew install python3`

###  `Permission denied` (Linux/macOS)

**Solution :**
```bash
chmod +x venv/bin/activate
source venv/bin/activate
```

---

##  Checklist post-installation

- [ ] Python 3.11+ installé
- [ ] Virtual environment créé et activé
- [ ] Dépendances installées (pip install -r requirements.txt)
- [ ] App lance en démo (python app/app.py)
- [ ] Interface accessible sur http://localhost:5000
- [ ] Tests passent (pytest tests/ -v)

---

##  Secrets et clés de configuration

### Variables d'environnement importantes

```bash
# Mode démo (pas de Gmail)
APP_MODE=demo

# Secret key Flask (développement)
FLASK_SECRET_KEY=dev-key-123

# Production
FLASK_ENV=production
FLASK_SECRET_KEY=clé_très_complexe_et_sécurisée

# Port custom
PORT=3000  # au lieu de 5000
```

 Voir [CONFIGURATION.md](./CONFIGURATION_FR.md) pour plus de détails

---

##  Prochaines étapes

- Lisez le [Guide démarrage rapide](./QUICK_START_FR.md)
- Explorez le [Mode démo](./DEMO_MODE_FR.md)
- Consultez le [Guide utilisateur](./USAGE_FR.md)
