#  Architecture du projet

Vue d'ensemble de l'architecture et du flux de données.

---

##  Flux général

```

                      Navigation Web                          
  User → Browser → HTTP Requests → Flask Routes             

                       ↓

               Flask Application (app.py)                     
  Routes:                                                     
  - GET /              → index()                             
  - GET /analyze       → analyze()                           
  - GET /domain/<d>    → view_domain()                       
  - GET/POST /safelist → manage_safelist()                   
  - POST /delete       → delete_emails()                     

                       ↓
            
              APP_MODE check      
            
                   ↓      ↓
           
          APP_MODE =     APP_MODE =      
            \"demo\"          \"local\"      
           
                ↓                   ↓
        
       Load Mock Data     Google OAuth 2.0       
       (JSON Static)      (credentials.json)     
                          ↓                      
       mock_analysis      Gmail API Service      
         .json                                   
        
               ↓                     ↓
      
         fetch_emails()                         
         - Récupère emails de Gmail ou mock     
         - Extrait List-Unsubscribe headers    
         - Groupe par domaine                   
         - Trie par count                       
      
                   ↓
      
         Appliquer Safelist                    
         - Charge safelist.json                
         - Filtre domaines whitelistés         
         - Retourne résultats filtrés          
      
                   ↓
      
         Retourner via Template                
         - Rendre HTML avec Jinja2             
         - CSS + assets statiques              
         - JavaScript interactif               
      
                   ↓
      
         User voit interface web               
         - Analyse des domaines                
         - Gestion safelist                    
         - Actions (voir, supprimer)           
      
```

---

##  Modules principaux

### 1. **app.py** - Point d'entrée

```python
# Initialisation Flask
app = Flask(__name__)

# Routes principales
@app.route("/")                    # Accueil
@app.route("/analyze")             # Analyse Gmail
@app.route("/domain/<domain>")     # Détails domaine
@app.route("/delete", methods=["POST"])       # Supprimer
@app.route("/safelist", methods=["GET", "POST"]) # Gestion
```

**Responsabilités :**
- Configuration de l'app Flask
- Définition des routes
- Gestion des sessions
- Rendu des templates

---

### 2. **auth/oauth_flow.py** - Authentification

```python
def auth():
    """Retourne credentials Gmail"""
    # Charge credentials.json
    # Gère token OAuth2
    # Rafraîchit token si expiré
    return credentials
```

**Responsabilités :**
- Gestion OAuth2 Google
- Stockage/refresh tokens
- Gestion erreurs auth

---

### 3. **gmail_api/fetch_emails.py** - Récupération mails

```python
def get_gmail_service(credentials):
    """Crée client Gmail API"""

def list_unsubscribe_emails(service):
    """Récupère mails avec List-Unsubscribe"""
    # Mode démo : charge mock_analysis.json
    # Mode local : appelle Gmail API
    # Retourne dict groupé par domaine
```

**Responsabilités :**
- Interface Gmail API
- Parsing List-Unsubscribe
- Groupement par domaine
- Tri et filtrage

---

### 4. **gmail_api/actions.py** - Actions sur mails

```python
def delete_emails(service, message_ids):
    """Supprime une liste de mails"""
    # Mode démo : simule
    # Mode local : appelle Gmail API de suppression
```

**Responsabilités :**
- Suppression d'emails
- Gestiion d'erreurs API

---

### 5. **gmail_api/parsers.py** - Parsing headers

```python
def extract_unsubscribe_links(headers):
    """Extrait URLs depuis List-Unsubscribe header"""
    # Parse header complexe
    # Retourne liste d'URLs
```

**Responsabilités :**
- Parsing RFC 8058 (List-Unsubscribe)
- Extraction URLs sûres
- Nettoyage

---

### 6. **config/config.py** - Configuration

```python
class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    APP_MODE = os.getenv("APP_MODE", "local")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")

class DemoConfig(Config):
    APP_MODE = "demo"
    DEBUG = True
```

**Responsabilités :**
- Gestion variables d'env
- Différentes configs par env
- Validation config

---

### 7. **config/safelist_manager.py** - Gestion whitelist

```python
def load_safelist():
    """Charge domaines whitelistés"""
    
def add_domain_to_safelist(domain):
    """Ajoute domaine à safelist"""
    
def filter_safelist(results, safelist):
    """Filtre résultats par safelist"""
```

**Responsabilités :**
- Chargement/sauvegarde safelist.json
- Ajout/suppression domaines
- Filtrage résultats

---

### 8. **templates/** - Interface web

```
templates/
 base.html         # Layout principal (Jinja2)
 index.html        # Accueil
 results.html      # Résultats analyse
 domain.html       # Détails domaine
 safelist.html     # Gestion safelist
```

**Stack :**
- **Templating :** Jinja2
- **CSS :** app.css + tokens.css
- **JS :** Vanilla JS (forms, interactions)

---

### 9. **static/** - Assets

```
static/
 css/
     app.css       # Styles principaux
     tokens.css    # Variables CSS (couleurs, sizes)
```

**Approche :**
- CSS variables (`--color-primary`, etc.)
- Responsive design
- Accessibility (a11y)

---

##  Structure données

### Résultats analyse (retourné par get_sorted_results)

```python
{
    "gmail.com": {
        "count": 45,
        "unsubscribe_links": [
            "https://mail.google.com/unsubscribe"
        ],
        "message_ids": ["msg_id_1", "msg_id_2", ...]
    },
    "newsletter.example.com": {
        "count": 23,
        "unsubscribe_links": [
            "https://example.com/unsub"
        ],
        "message_ids": ["msg_id_3", ...]
    }
}
```

### Safelist (safelist.json)

```json
{
    "domains": [
        "gmail.com",
        "important-company.com",
        "personal@email.com"
    ]
}
```

---

##  Flux décision APP_MODE

### En mode démo

```python
if APP_MODE == "demo":
    # app.py ligne ~60
    mock_data = load_mock_data()
    results = dict(sorted(mock_data.items(), ...))
    return results, None  # Pas de service Gmail
```

- Charge `app/mock/mock_analysis.json`
- Ignore toute auth Gmail
- Simule toutes actions
- Données statiques

### En mode local

```python
else:  # APP_MODE == "local"
    credentials = auth()
    service = get_gmail_service(credentials)
    results = list_unsubscribe_emails(service)
    # Appel réel à Gmail API
```

- OAuth Gmail obligatoire
- Appels réels à l'API
- Données dynamiques
- Suppressions réelles

---

##  Sécurité

### Authentification

- **Mode local :** OAuth2 Google (standard)
- **Mode démo :** Aucune (données faites)

### Sessions

- **SECRET_KEY :** Générée ou depuis env
- **Cookies :** Sécurisés en production (HTTPS)
- **CSRF :** Via Jinja2 (si implémenté)

### API Gmail

- **Permissions :** `readonly`, `modify`, `delete` selon besoin
- **Rate limiting :** Gestion par Google
- **Token storage :** Fichier local sécurisé (à améliorer)

---

##  Déploiement

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]
```

### Railway

- Image Docker
- Variables d'env injectées
- Auto-redémarrage
- Logs centralisés

---

##  Tests

Structure :

```
tests/
 conftest.py       # Configuration pytest
 test_app.py       # Suite tests (11 tests)
```

Tests en mode démo :
- Routes principales
- Analyse
- Détails domaine
- Safelist
- Données mock

---

##  Dépendances

```
requests          → Calls HTTP (Gmail API)
Flask             → Web framework
google-auth-*     → OAuth2
python-dotenv     → Variables d'env
gunicorn          → WSGI server
pytest            → Tests
```

---

##  Prochaines étapes

-  [Tests détaillés](./TESTING_FR.md)
-  [Dev guide](./DEVELOPMENT_FR.md)
-  [Configuration](./CONFIGURATION_FR.md)
