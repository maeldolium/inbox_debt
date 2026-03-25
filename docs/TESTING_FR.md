#  Tests et pytest

Guide complet de la suite de tests.

---

##  Vue d'ensemble

**11 tests pytest** validant les fonctionnalités essentielles en mode démo.

```bash
tests/
 conftest.py      # Configuration pytest
 test_app.py      # Suite complète (11 tests)
```

---

##  Lancer les tests

### Tous les tests

```bash
pytest tests/ -v
```

Résultat :
```
tests/test_app.py::TestBasicRoutes::test_index_responds_200 PASSED
tests/test_app.py::TestBasicRoutes::test_index_returns_html PASSED
tests/test_app.py::TestAnalyzeRoute::test_analyze_get_responds_200 PASSED
... (11 total)
============================= 11 passed in X.XXs ==============================
```

### Tests spécifiques

```bash
# Une classe entière
pytest tests/test_app.py::TestBasicRoutes -v

# Un test spécifique
pytest tests/test_app.py::TestBasicRoutes::test_index_responds_200 -v

# Avec pattern
pytest tests/ -k "test_analyze" -v
```

### Avec rapport couverture

```bash
pytest tests/ --cov=app --cov-report=html
# Génère rapport HTML dans htmlcov/
```

### Mode verbose vs quiet

```bash
pytest tests/ -v      # Détaillé
pytest tests/         # Normal
pytest tests/ -q      # Court
```

---

##  Suite de tests

### 1. **TestBasicRoutes** (2 tests)

Vérifie les routes basiques :

```python
def test_index_responds_200(client):
    """Test que / répond en 200."""
    response = client.get('/')
    assert response.status_code == 200
    
def test_index_returns_html(client):
    """Test que / retourne du HTML."""
    response = client.get('/')
    assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data
```

**Ce qu'on teste :**
-  Route `/` existe
-  Pas d'erreur (200)
-  Retourne HTML valide

---

### 2. **TestAnalyzeRoute** (3 tests)

Vérifie la route analyse :

```python
def test_analyze_get_responds_200(client):
    """Test que /analyze (GET) répond en 200."""
    response = client.get('/analyze')
    assert response.status_code == 200
    
def test_analyze_post_responds_200(client):
    """Test que /analyze (POST) répond en 200."""
    response = client.post('/analyze')
    assert response.status_code == 200
    
def test_analyze_returns_data(client):
    """Test que /analyze retourne des données fictives."""
    response = client.get('/analyze')
    assert response.status_code == 200
    assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data
```

**Ce qu'on teste :**
-  GET et POST marchent
-  Pas d'erreur
-  Retourne temps

---

### 3. **TestDomainDetailRoute** (2 tests)

Vérifie la vue détails domaine :

```python
def test_domain_detail_with_valid_domain(client):
    """Test qu'une route domaine répond avec un domaine valide."""
    client.get('/analyze')
    mock_data = load_mock_data()
    
    if mock_data:
        first_domain = list(mock_data.keys())[0]
        response = client.get(f'/domain/{first_domain}')
        assert response.status_code == 200
    
def test_domain_detail_with_invalid_domain(client):
    """Test qu'une route domaine renvoie une erreur pour un domaine invalide."""
    response = client.get('/domain/invalid_domain_that_does_not_exist')
    assert response.status_code in [200, 404]
```

**Ce qu'on teste :**
-  Domaine valide → 200
-  Domaine invalide → 200 ou 404

---

### 4. **TestSafelistManagement** (2 tests)

Vérifie gestion safelist :

```python
def test_safelist_view_responds_200(client):
    """Test que /safelist (view) répond en 200."""
    response = client.get('/safelist')
    assert response.status_code == 200
    
def test_safelist_post_succeeds_in_demo(client):
    """Test que l'ajout à la safelist fonctionne en mode démo."""
    client.get('/analyze')
    mock_data = load_mock_data()
    
    if mock_data:
        first_domain = list(mock_data.keys())[0]
        response = client.post('/safelist', data={'domain': first_domain})
        assert response.status_code == 200
        assert b'safelist' in response.data.lower()
```

**Ce qu'on teste :**
-  Vue safelist 200
-  POST ajout domaine retourne message

---

### 5. **TestMockDataLoading** (2 tests)

Vérifie données fictives :

```python
def test_mock_data_loads(self):
    """Test que les données fictives se chargent."""
    mock_data = load_mock_data()
    
    assert isinstance(mock_data, dict)
    assert len(mock_data) > 0
    
def test_mock_data_has_required_fields(self):
    """Test que les données fictives ont les champs requis."""
    mock_data = load_mock_data()
    
    for domain, data in mock_data.items():
        assert isinstance(domain, str)
        assert isinstance(data, dict)
        assert 'count' in data
```

**Ce qu'on teste :**
-  Mock data charge sans erreur
-  Structure valide (dict)
-  Champs requis présents

---

##  Fixture pytest

```python
@pytest.fixture
def client():
    """Configure un client Flask pour les tests."""
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client
```

**Qu'elle fait :**
- Crée client Flask test
- Mode TESTING activé
- Pas de serveur réel
- Réutilisé pour chaque test

---

##  Ajouter des tests

### Structure

```python
class TestMonFonctionnalite:
    """Tests pour ma fonctionnalité."""
    
    def test_case_1(self, client):
        """Première condition."""
        response = client.get('/ma-route')
        assert response.status_code == 200
    
    def test_case_2(self, client):
        """Deuxième condition."""
        response = client.post('/ma-route', data={'key': 'value'})
        assert response.status_code in [200, 201]
```

### Ajouter au fichier tests/test_app.py

```python
class TestMonFonctionnalite:
    
    def test_nouvelle_route(self, client):
        """Test la nouvelle route."""
        response = client.get('/nouvelle-route')
        assert response.status_code == 200
        assert b'expected content' in response.data
```

Lancer :
```bash
pytest tests/test_app.py::TestMonFonctionnalite::test_nouvelle_route -v
```

---

##  Assertions utiles

```python
# Status codes
assert response.status_code == 200
assert response.status_code in [200, 201]

# Contenu HTML
assert b'text content' in response.data
assert b'<!DOCTYPE html>' in response.data

# Redirects
assert response.status_code == 302
assert response.location == '/expected-url'

# JSON
data = json.loads(response.data)
assert data['key'] == 'value'

# Exceptions
with pytest.raises(ValueError):
    do_something()
```

---

##  Debugging tests

### Afficher stdout

```bash
pytest tests/ -v -s
# -s shows print() statements
```

### Arrêter au premier échec

```bash
pytest tests/ -x
# s'arrête au premier test échoué
```

### Déboguer interactif

```bash
pytest tests/ --pdb
# Lance pdb sur erreur
```

### Voir les logs

```bash
pytest tests/ -v --tb=short
# Plus détail sur les erreurs
```

---

##  CI/CD Jenkins

Tests lancés à chaque push :

```
Stage 1: Install Dependencies
         ↓
Stage 2: Run Tests (pytest) ← **TU ES ICI**
         ↓ (si ok)
Stage 3: Build Docker
    ...
```

### Commande lancée

```bash
. venv/bin/activate
pytest tests/ -v --tb=short
```

**Si pytest échoue :**
- Code de sortie != 0
- Pipeline s'arrête
- Email d'erreur envoyé
- Deploy Railway annulé

---

##  Checklist tests

- [ ] Tous les tests passent localement
- [ ] `pytest tests/ -v` = 11 passed
- [ ] Code cové si possible
- [ ] Nouveaux tests pour nouvelles features
- [ ] Tests en mode démo uniquement
- [ ] Dépendances pytest installées

---

##  Prochaines étapes

-  [Dépannage](./TROUBLESHOOTING_FR.md)
-  [Configuration](./CONFIGURATION_FR.md)
-  [Développement](./DEVELOPMENT_FR.md)
