import pytest
import os
import sys
import json
from app import app, load_mock_data

# Ajouter le répertoire app au chemin pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

# Forcer APP_MODE en mode démo pour les tests
os.environ['APP_MODE'] = 'demo'
os.environ['FLASK_ENV'] = 'testing'


@pytest.fixture
def client():
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


class TestBasicRoutes:
    
    def test_index_responds_200(self, client):

        response = client.get('/')
        assert response.status_code == 200
        
    def test_index_returns_html(self, client):

        response = client.get('/')
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data


class TestAnalyzeRoute:
    
    def test_analyze_get_responds_200(self, client):
        response = client.get('/analyze')
        assert response.status_code == 200
        
    def test_analyze_post_responds_200(self, client):
        response = client.post('/analyze')
        assert response.status_code == 200
        
    def test_analyze_returns_data(self, client):
        response = client.get('/analyze')
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data


class TestDomainDetailRoute:
    
    def test_domain_detail_with_valid_domain(self, client):
        # D'abord lancer /analyze pour charger les données
        client.get('/analyze')
        
        # Récupérer les données fictives pour obtenir un domaine valide
        mock_data = load_mock_data()
        
        if mock_data:
            first_domain = list(mock_data.keys())[0]
            response = client.get(f'/domain/{first_domain}')
            assert response.status_code == 200
    
    def test_domain_detail_with_invalid_domain(self, client):
        response = client.get('/domain/invalid_domain_that_does_not_exist')
        assert response.status_code in [200, 404]


class TestSafelistManagement:
    
    def test_safelist_view_responds_200(self, client):
        response = client.get('/safelist')
        assert response.status_code == 200
    
    def test_safelist_post_succeeds_in_demo(self, client):
        # Lancer /analyze pour charger les données
        client.get('/analyze')
        
        # Récupérer les données fictives pour obtenir un domaine valide
        mock_data = load_mock_data()
        
        if mock_data:
            first_domain = list(mock_data.keys())[0]
            response = client.post('/safelist', data={'domain': first_domain})
            # Réponse : 200 + message de succès simulé
            assert response.status_code == 200
            # Vérifier que le message de succès est dans la réponse
            assert b'safelist' in response.data.lower()


class TestMockDataLoading:
    
    def test_mock_data_loads(self):
        mock_data = load_mock_data()
        
        # Données = dictionnaire non vide
        assert isinstance(mock_data, dict)
        assert len(mock_data) > 0
    
    def test_mock_data_has_required_fields(self):
        mock_data = load_mock_data()
        
        # Chaque domaine doit avoir au moins count
        for domain, data in mock_data.items():
            assert isinstance(domain, str)
            assert isinstance(data, dict)
            assert 'count' in data
