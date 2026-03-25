<!-- Sommaire bilingue -->
[🇫🇷 **Français**](#-inbox-debt---français) | [🇬🇧 **English**](#-inbox-debt---english)

---

# 🇫🇷 Inbox Debt - Français

## Vue d'ensemble

**Inbox Debt** est une application web automatisant le nettoyage de votre boîte mail Gmail. Elle détecte les newsletters et e-mails promotionnels, extrait les liens de désabonnement et vous permet de supprimer en masse les mails indésirables tout en protégeant votre safelist.

### [Essayer en ligne](https://inboxdebt-production.up.railway.app/)

**Mode démo** : Explorez l'application sans connecter votre compte Gmail avec des données fictives !

---

## Fonctionnalités

- **Authentification sécurisée** : Connexion Gmail via OAuth2
- **Analyse intelligente** : Détecte automatiquement newsletters et expéditeurs promotionnels
- **Extraction de liens** : Lit les en-têtes `List-Unsubscribe` pour identifier les désabonnements sûrs
- **Regroupement par domaine** : Résume les e-mails par expéditeur pour une décision rapide
- **/Safelist** : Protégez les expéditeurs de confiance (ne seront jamais supprimés)
- **Suppression en masse** : Supprimez les mails indésirables en volume tout en respectant la safelist
- **Interface web** : Interface Flask intuitive pour non-techniciens
- **Mode démo** : Testez l'application avec des données fictives sans connexion Gmail

---

## Mode Démo

Le **mode démo** vous permet de tester l'application complètement sans authentification Gmail.

### Comment utiliser le mode démo ?

1. **En ligne** : [inboxdebt-production.up.railway.app](https://inboxdebt-production.up.railway.app/)
2. **En local** :
   ```bash
   APP_MODE=demo python app/app.py
   ```

Le mode démo fournit un jeu de données fictives pour explorer :
- L'interface d'analyse des mails
- La gestion de la safelist
- La simulation de suppressions (sans affecter votre compte)

---

## Technologies

| Composant | Tech |
|-----------|------|
| **Backend** | Python 3.11+ |
| **Framework web** | Flask |
| **API** | Gmail API |
| **Serveur** | Gunicorn |
| **Containerisation** | Docker |
| **Déploiement** | Railway |
| **CI/CD** | Jenkins + pytest |

---

## Pipeline CI/CD

L'application utilise **Jenkins** pour un déploiement automatisé du mode démo sur Railway :

```
┌─────────────────────┐
│ Install Dependencies|
└────────┬────────────┘
         ↓
┌─────────────────────┐
│  Run Tests (pytest) | ← Gate automatique
└────────┬────────────┘
         ↓ (si tous les tests passent)
┌───────────────────┐
│ Build Docker Image|
└────────┬──────────┘
         ↓
┌───────────────────┐
│ Run Container Test|
└────────┬──────────┘
         ↓
┌─────────────────────┐
│  Health Check (curl)|
└────────┬────────────┘
         ↓ (si tout ok)
┌───────────────┐
│ Deploy Railway|
└───────────────┘
```

### Détails

- **Stage 1 - Install** : Création d'un venv et installation des dépendances (+pytest)
- **Stage 2 - Tests** : Exécution de la suite pytest - **si ça échoue, la pipeline s'arrête**
- **Stage 3 - Docker Build** : Création de l'image Docker (seulement si tests ok)
- **Stage 4 - Container Test** : Lancement du conteneur en mode démo
- **Stage 5 - Health Check** : Vérification que l'app répond (curl -f)
- **Stage 6 - Deploy Railway** : Déploiement vers Railway en détaché (--detach)

### Tests automatisés

Suite pytest avec 11 tests couvrant :
- Routes principales (`/` répond en 200)
- Route `/analyze` en mode démo
- Détails de domaine (`/domain/<domain>`)
- Gestion de la safelist
- Chargement des données fictives

---

## Installation locale

### Prérequis

- Python 3.11+
- pip / venv
- Docker (optionnel, pour tester le conteneur)

### Setup

```bash
# Cloner le repo
git clone <repo>
cd inbox_debt

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer en mode démo
export APP_MODE=demo
python app/app.py

# Ou en mode production avec OAuth Gmail
export FLASK_ENV=production
export FLASK_SECRET_KEY=votre_clé
python app/app.py
```

L'app démarre sur `http://localhost:5000`

---

## Tests

```bash
# Lancer la suite pytest
pytest tests/ -v

# Lancer un test spécifique
pytest tests/test_app.py::TestBasicRoutes::test_index_responds_200 -v

# Avec rapport de couverture
pytest tests/ --cov=app
```

---

## Docker

### Build

```bash
docker build -t inbox_debt .
```

### Run (mode démo)

```bash
docker run -p 8080:8080 -e APP_MODE=demo inbox_debt
```

### Run (production avec Railway)

```bash
docker run -p 8080:8080 \
  -e APP_MODE=local \
  -e FLASK_SECRET_KEY=votre_clé \
  -e FLASK_ENV=production \
  inbox_debt
```

---

## Structure du projet

```
inbox_debt/
├── app/
│   ├── app.py                 # Application Flask
│   ├── auth/
│   │   └── oauth_flow.py      # Authentification Gmail
│   ├── config/
│   │   ├── config.py          # Configuration
│   │   ├── settings.py        # APP_MODE
│   │   └── safelist_manager.py
│   ├── gmail_api/
│   │   ├── fetch_emails.py    # Récupération mails
│   │   ├── actions.py         # Suppressions
│   │   └── parsers.py         # Parsing en-têtes
│   ├── mock/
│   │   └── mock_analysis.json # Données démo
│   ├── static/                # CSS/JS
│   ├── templates/             # Templates HTML
│   └── ux/                    # Logique UI
├── tests/
│   ├── test_app.py           # Suite pytest
│   └── conftest.py           # Configuration pytest
├── Jenkinsfile               # Pipeline CI/CD
├── Dockerfile                # Image containerisée
├── requirements.txt          # Dépendances Python
└── README.md                 # Ce fichier
```

---

## Licence

Ce projet est sous licence **Creative Commons BY-NC 4.0**.

Vous pouvez : Étudier, modifier et réutiliser le code à titre personnel et éducatif

Interdit : Toute utilisation commerciale

---

## Support

Pour toute question ou problème, consultez la [documentation](./docs) ou ouvrez une issue.

---

---

# 🇬🇧 Inbox Debt - English

## Overview

**Inbox Debt** is a web application that automates Gmail inbox cleanup. It detects newsletters and promotional emails, extracts unsubscribe links, and lets you bulk-delete unwanted mail while protecting your whitelist.

### [Try it online](https://inboxdebt-production.up.railway.app/)

**Demo mode** : Explore the app without connecting your Gmail account using sample data!

---

## Features

- **Secure authentication** : Gmail login via OAuth2
- **Intelligent analysis** : Auto-detect newsletters and promotional senders
- **Link extraction** : Read `List-Unsubscribe` headers to identify safe opt-outs
- **Domain grouping** : Summarizes emails by sender for quick decisions
- **Whitelist/Safelist** : Protect trusted senders (never deleted)
- **Bulk deletion** : Delete unwanted emails in volume while respecting the safelist
- **Web interface** : Intuitive Flask interface for non-technical users
- **Demo mode** : Test the app with sample data without Gmail authentication

---

## Demo Mode

The **demo mode** lets you test the application completely without Gmail authentication.

### How to use demo mode?

1. **Online** : [inboxdebt-production.up.railway.app](https://inboxdebt-production.up.railway.app/)
2. **Locally** :
   ```bash
   APP_MODE=demo python app/app.py
   ```

Demo mode provides sample data to explore :
- Email analysis interface
- Safelist management
- Deletion simulation (without affecting your account)

---

## Technologies

| Component | Tech |
|-----------|------|
| **Backend** | Python 3.11+ |
| **Web Framework** | Flask |
| **API** | Gmail API |
| **Server** | Gunicorn |
| **Containerization** | Docker |
| **Deployment** | Railway |
| **CI/CD** | Jenkins + pytest |

---

## CI/CD Pipeline

The application uses **Jenkins** for automatic demo mode deployment to Railway :

```
┌─────────────────────┐
│ Install Dependencies|
└────────┬────────────┘
         ↓
┌────────────────────┐
│  Run Tests (pytest)|  ← Automatic gate
└────────┬───────────┘
         ↓ (if all tests pass)
┌───────────────────┐
│ Build Docker Image|
└────────┬──────────┘
         ↓
┌───────────────────┐
│ Run Container Test|
└────────┬──────────┘
         ↓
┌─────────────────────┐
│  Health Check (curl)|
└────────┬────────────┘
         ↓ (if all ok)
┌───────────────┐
│ Deploy Railway|
└───────────────┘
```

### Details

- **Stage 1 - Install** : venv creation and dependency installation (+pytest)
- **Stage 2 - Tests** : pytest suite - **if it fails, the pipeline stops**
- **Stage 3 - Docker Build** : Docker image creation (only if tests ok)
- **Stage 4 - Container Test** : Demo mode container startup
- **Stage 5 - Health Check** : Verify app responds (curl -f)
- **Stage 6 - Deploy Railway** : Deploy to Railway in detached mode (--detach)

### Automated Tests

pytest suite with 11 tests covering :
- Main routes (`/` responds 200)
- `/analyze` route in demo mode
- Domain details (`/domain/<domain>`)
- Safelist management
- Sample data loading

---

## Local Installation

### Prerequisites

- Python 3.11+
- pip / venv
- Docker (optional, to test the container)

### Setup

```bash
# Clone the repo
git clone <repo>
cd inbox_debt

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run in demo mode
export APP_MODE=demo
python app/app.py

# Or in production mode with Gmail OAuth
export FLASK_ENV=production
export FLASK_SECRET_KEY=your_secret_key
python app/app.py
```

App starts on `http://localhost:5000`

---

## Tests

```bash
# Run full pytest suite
pytest tests/ -v

# Run specific test
pytest tests/test_app.py::TestBasicRoutes::test_index_responds_200 -v

# With coverage report
pytest tests/ --cov=app
```

---

## Docker

### Build

```bash
docker build -t inbox_debt .
```

### Run (demo mode)

```bash
docker run -p 8080:8080 -e APP_MODE=demo inbox_debt
```

### Run (production with Railway)

```bash
docker run -p 8080:8080 \
  -e APP_MODE=local \
  -e FLASK_SECRET_KEY=your_secret_key \
  -e FLASK_ENV=production \
  inbox_debt
```

---

## Project Structure

```
inbox_debt/
├── app/
│   ├── app.py                 # Flask application
│   ├── auth/
│   │   └── oauth_flow.py      # Gmail authentication
│   ├── config/
│   │   ├── config.py          # Configuration
│   │   ├── settings.py        # APP_MODE
│   │   └── safelist_manager.py
│   ├── gmail_api/
│   │   ├── fetch_emails.py    # Email fetching
│   │   ├── actions.py         # Deletions
│   │   └── parsers.py         # Header parsing
│   ├── mock/
│   │   └── mock_analysis.json # Demo data
│   ├── static/                # CSS/JS
│   ├── templates/             # HTML templates
│   └── ux/                    # UI logic
├── tests/
│   ├── test_app.py           # pytest suite
│   └── conftest.py           # pytest configuration
├── Jenkinsfile               # CI/CD pipeline
├── Dockerfile                # Docker image
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## License

This project is licensed under **Creative Commons BY-NC 4.0**.

You can: Study, modify and reuse the code for personal and educational purposes

Prohibited: Any commercial use

---

## Support

For questions or issues, check the [documentation](./docs) or open an issue.

---