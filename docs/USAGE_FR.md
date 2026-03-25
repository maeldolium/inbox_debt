#  Guide d'utilisation

Comment utiliser **Inbox Debt** pour nettoyer votre Gmail.

---

##  Connexion (Mode production)

### Avec Gmail OAuth

1. Lancez l'app : `python app/app.py`
2. Allez sur `http://localhost:5000`
3. Cliquez sur **"Connecter avec Gmail"**
4. Autorisez l'accès
5. Vous êtes connectés ! 

### Mode démo (sans Gmail)

Pas de connexion requise ! Lancez simplement :

```bash
export APP_MODE=demo
python app/app.py
```

 Voir [Mode Démo](./DEMO_MODE_FR.md)

---

##  Accueil

La première page montre :

- **Votre mode** : "local" (Gmail) ou "demo" (données fictives)
- **Bouton d'analyse** : Pour lancer le scan
- **Bouton safelist** : Pour gérer la whitelist

---

##  Analyser les emails

### Lancer une analyse

1. Cliquez sur **"Analyser ma boîte"**
2. L'app se connecte à Gmail
3. Récupère les mails avec en-têtes `List-Unsubscribe`
4. Les groupe par domaine
5. Les trie par nombre décroissant

### Résultat

Vous voyez une **liste de domaines** avec :

| Info | Exemple |
|------|---------|
|  Domaine | `newsletter.example.com` |
|  Nombre | `42 emails` |
|  Lien désabonnement |  ou  |
|  Actions | Voir détails / Supprimer |

---

##  Détails d'un domaine

Cliquez sur un domaine pour voir :

- **Nombre de mails** totaux
- **Nombre avec lien désabonnement**
- **Preview des mails** (domaine, objet, date)
- **Option de suppression**

---

##  Safelist (Whitelist)

### Voir la safelist

1. Accueil → Cliquez **"Gérer la safelist"**
2. Ou allez à `/safelist`

Vous voyez les domaines protégés (jamais supprimés).

### Ajouter à la safelist

#### Option 1 : depuis l'analyse

1. Allez à `/analyze`
2. Trouvez le domaine
3. Cliquez **"Ajouter à safelist"**
4. Le domaine est protégé 

#### Option 2 : depuis la safelist

1. Allez à `/safelist`
2. Entrez un domaine en bas
3. Cliquez **"Ajouter"**

### Supprimer de la safelist

Via l'interface safelist, cliquez sur le domaine pour le retirer.

---

##  Supprimer des mails

###  Avant de supprimer

1. **Vérifiez le domaine** → Voir les détails
2. **Vérifiez pas en safelist** → Allez à `/safelist`
3. **Doublez-checked** → C'est nécessaire !

### Supprimer

1. Depuis `/analyze`, trouvez le domaine
2. Cliquez **"Supprimer"**
3. Confirmez 
4. Les mails sont supprimés 

### Après suppression

- Le domaine disparait de la liste
- `N` emails ont été supprimés
- Un message de confirmation apparait

---

##  Workflow complet

```
1. Connexion Gmail (ou mode démo)
     ↓
2. Cliquez "Analyser"
     ↓
3. Récupération mails avec List-Unsubscribe
     ↓
4. Résultats groupés par domaine (triés)
     ↓
5. Pour chaque domaine :
      Voir détails
      Optionnel : ajouter à safelist
      Si sûr : supprimer
     ↓
6. Mails supprimés définitivement
```

---

##  Actions possibles

Par domaine, vous pouvez :

| Action | Effet | Réversible |
|--------|-------|-----------|
|  Voir détails | Affiche infos | N/A |
|  Ajouter safelist | Protège |  (retirer) |
|  Supprimer | Supprime Gmail |  (permanent) |

---

##  Conseils d'utilisation

###  Bonnes pratiques

-  **Vérifiez toujours avant de supprimer**
-  **Utilisez la safelist pour les domaines importants**
-  **Commencez petit** : testez avec 1-2 domaines
-  **Nettoyez régulièrement** : une fois par mois
-  **Prenez note de vos exclusions**

###  À éviter

-  Ne supprimez pas en masse sans vérifier
-  Ne supprimez pas avant de voir les détails
-  Ne fermez pas l'onglet pendant la suppression

---

##  Problèmes courants

###  "Pas de lien de désabonnement"

**Raison :** Le mail n'a pas d'en-tête `List-Unsubscribe`

**Solution :** Vous ne pouvez pas le désabonner automatiquement. Supprimez manuellement ou ignorez.

###  "Erreur : accès Gmail refusé"

**Raison :** Permissions insuffisantes ou token expiré

**Solution :**
- Reconnectez-vous
- Vérifiez les permissions OAuth
- Essayez depuis une fenêtre incognito

###  "Rien à analyser"

**Raison :** Pas de mails avec `List-Unsubscribe` trouvés

**Solution :**
- Peut être normalement votre Gmail est déjà clean !
- Essayez avec un moteur de recherche : `has:unsubscribe`

---

##  Besoin d'aide ?

-  [Troubleshooting](./TROUBLESHOOTING_FR.md)
-  [Configuration](./CONFIGURATION_FR.md)
-  [Mode Démo](./DEMO_MODE_FR.md)
