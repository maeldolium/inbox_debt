#  Démarrage rapide

Pour lancer Inbox Debt en **2 minutes** ! ⏱

## Mode démo (aucune connexion Gmail)

### Étape 1 : Setup

```bash
# Cloner et rentrer dans le dossier
git clone https://github.com/votre-username/inbox_debt
cd inbox_debt

# Créer l'environnement
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# Installer
pip install -r requirements.txt
```

### Étape 2 : Lancer

```bash
export APP_MODE=demo
python app/app.py
```

**Accédez à http://localhost:5000** 

---

## C'est tout ! 

Vous pouvez maintenant :

 Explorer l'interface en mode démo
 Analyser des données fictives
 Gérer la safelist
 Voir comment ça fonctionne

---

## Prochaine étape ? 

 [Mode Démo - Guide complet](./DEMO_MODE_FR.md)

 [Installation complète](./INSTALLATION_FR.md)

 [Guide utilisateur](./USAGE_FR.md)
