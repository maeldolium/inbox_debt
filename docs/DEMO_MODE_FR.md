#  Mode Démo - Guide complet

Le **mode démo** vous permet de tester Inbox Debt **sans Gmail** avec des données fictives.

---

##  Lancer le mode démo

### Localement

```bash
# Activer le venv
source venv/bin/activate  # Linux/macOS
# ou
.\venv\Scripts\Activate.ps1  # Windows

# Lancer
export APP_MODE=demo
python app/app.py
```

Ouvrez `http://localhost:5000`

### En ligne

 [https://inboxdebt-production.up.railway.app/](https://inboxdebt-production.up.railway.app/)

### Avec Docker

```bash
docker run -p 8080:8080 -e APP_MODE=demo inbox_debt:latest
```

Ouvrez `http://localhost:8080`

---

##  Données fictives (Mock Data)

Le mode démo charge des données depuis `app/mock/mock_analysis.json`.

### Structure des données

```json
{
  "gmail.com": {
    "count": 45,
    "unsubscribe_links": ["https://mail.google.com/unsubscribe"],
    "message_ids": ["msg_id_1", "msg_id_2", ...]
  },
  "newsletter.example.com": {
    "count": 23,
    "unsubscribe_links": ["https://example.com/unsub"]
  }
}
```

**Champs :**
- `count` : nombre d'emails de ce domaine
- `unsubscribe_links` : liste des liens de désabonnement
- `message_ids` : IDs des emails (pour la simulation)

---

##  Fonctionnalités du mode démo

###  Ce qu'on peut faire

| Fonctionnalité | Démo | Notes |
|---|---|---|
|  Voir l'accueil |  | Page d'index |
|  Analyser les données |  | Charge mock data |
|  Voir détails domaine |  | Route `/domain/<domain>` |
|  Gérer la safelist |  | Simulation en mémoire |
|  Supprimer (simulé) |  | Pas d'appel réel à Gmail |
|  Interface complète |  | HTML/CSS/JS normal |

###  Ce qu'on ne peut pas faire

| Fonctionnalité | Raison |
|---|---|
|  Connexion Gmail | Aucun OAuth en démo |
|  Accéder Gmail réel | APP_MODE=demo n'appelle pas l'API |
|  Persistance données | Les données sont reset à chaque refresh |
|  Désabonnement réel | Les liens ne fonctionnent pas (n'appelle pas Gmail) |

---

##  Tester les fonctionnalités

### 1⃣ Page d'accueil

```
http://localhost:5000/
```

Affiche une page simple avec mode démo.

### 2⃣ Analyser les mails

```
http://localhost:5000/analyze
```

Charge et affiche les données fictives groupées par domaine.

### 3⃣ Voir détails d'un domaine

Cliquez sur un domaine depuis `/analyze` ou allez à :

```
http://localhost:5000/domain/gmail.com
```

Montre les détails : nombre de mails, liens de désabonnement, etc.

### 4⃣ Gérer la safelist

```
http://localhost:5000/safelist
```

- Voir les domaines en safelist
- Simuler l'ajout d'un domaine
- En démo, pas de persistance disque

### 5⃣ Supprimer (simulé)

Depuis `/analyze`, cliquez sur le bouton "Supprimer" d'un domaine.

On reçoit un message : `[DEMO] N emails simulés supprimés de example.com`

Les données en mémoire sont mises à jour, mais rien n'affecte Gmail.

---

##  Tests en mode démo

Une suite de **11 tests pytest** valide le mode démo :

```bash
# Lancer tous les tests
pytest tests/ -v

# Partie de la suite :
#  test_index_responds_200
#  test_analyze_get_responds_200
#  test_domain_detail_with_valid_domain
#  test_safelist_view_responds_200
#  test_mock_data_loads
```

---

##  Fichiers sources du mode démo

```
app/
 app.py                      # Logique principale
 config/
    settings.py             # APP_MODE=demo
 mock/
    mock_analysis.json      # Données fictives
 templates/
    index.html
    results.html            # Affiche l'analyse
    domain.html             # Détails domaine
    safelist.html           # Gestion safelist
 gmail_api/
     fetch_emails.py         # Mode démo retourne mock data
```

---

##  Modifier les données fictives

Pour tester avec d'autres données, éditez `app/mock/mock_analysis.json` :

```json
{
  "exemple.com": {
    "count": 100,
    "unsubscribe_links": ["https://exemple.com/unsubscribe"],
    "message_ids": ["id1", "id2", "id3"]
  },
  "test.io": {
    "count": 50,
    "unsubscribe_links": [],
    "message_ids": []
  }
}
```

Relancez l'app, les nouvelles données seront chargées ! 

---

##  Mode démo → Mode production

Pour passer en mode production avec Gmail réel :

1. Authentifiez-vous auprès de Google OAuth
2. Changez `APP_MODE=local`
3. Fournissez `FLASK_SECRET_KEY` sécurisée
4. Lancez `python app/app.py`

 Voir [Configuration](./CONFIGURATION_FR.md)

---

##  Dépannage mode démo

###  La page est blanche

**Solution :**
```bash
# Vérifier que les templates existent
ls app/templates/

# Vérifier APP_MODE
export APP_MODE=demo
python app/app.py
```

###  Les données fictives ne chargent pas

**Solution :**
```bash
# Vérifier le fichier
cat app/mock/mock_analysis.json | head

# Vérifier le JSON est valide
python -c "import json; json.load(open('app/mock/mock_analysis.json'))"
```

###  Mode démo détecte pas

**Solution :**
```bash
# Forcer en dur
export APP_MODE=demo
# Ne pas d'espace autour du =
APP_MODE=demo python app/app.py
```

---

##  Prochaines étapes

-  [Guide utilisateur](./USAGE_FR.md) - Comment utiliser toutes les fonctionnalités
-  [Guide développement](./DEVELOPMENT_FR.md) - Modifier le code et contribuer
