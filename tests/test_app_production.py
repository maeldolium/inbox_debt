import pytest
import os
import sys
import json
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Ajouter le répertoire app au chemin pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

# Forcer APP_MODE en mode local pour les tests de production
os.environ['APP_MODE'] = 'local'
os.environ['FLASK_ENV'] = 'testing'

from app import (
    app, 
    load_mock_data, 
    get_sorted_results, 
    LAST_ANALYSIS
)
from gmail_api.parsers import extract_domain, extract_http_unsubscribe
from config.safelist_manager import (
    load_safelist, 
    save_safelist, 
    add_domain_to_safelist, 
    filter_safelist
)
from config.config import get_config, validate_config, DevelopmentConfig, ProductionConfig
from ux.ux import count_with_without_link_mails


# ============= FIXTURES =============

@pytest.fixture
def client():
    """Fixture pour créer un client Flask de test"""
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


@pytest.fixture
def temp_safelist_dir():
    """Créer un dossier temporaire pour les tests de safelist"""
    # Créer un dossier temporaire
    temp_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    
    # Copier la structure de config si nécessaire
    app_config_dir = os.path.join(temp_dir, 'app', 'config')
    os.makedirs(app_config_dir, exist_ok=True)
    
    # Changer le répertoire de travail
    os.chdir(temp_dir)
    
    yield temp_dir
    
    # Nettoyage
    os.chdir(original_cwd)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_gmail_service():
    """Créer un mock du service Gmail"""
    service = Mock()
    return service


@pytest.fixture
def sample_gmail_results():
    """Données fictives d'analyse Gmail pour les tests"""
    return {
        'gmail.com': {
            'domain': 'gmail.com',
            'count': 5,
            'message_ids': ['msg1', 'msg2', 'msg3', 'msg4', 'msg5'],
            'subjects': ['Test 1', 'Test 2'],
            'unsubscribe_links': ['http://unsubscribe.gmail.com', None, 'http://unsubscribe2.gmail.com', None, None]
        },
        'example.com': {
            'domain': 'example.com',
            'count': 3,
            'message_ids': ['msg6', 'msg7', 'msg8'],
            'subjects': ['Newsletter'],
            'unsubscribe_links': [None, None, None]
        }
    }


# ============= TESTS DE FONCTIONS UTILITAIRES =============

class TestSortedResults:
    """Tests pour la fonction get_sorted_results en mode local/production"""
    
    @patch('app.auth')
    @patch('app.get_gmail_service')
    @patch('app.list_unsubscribe_emails')
    def test_get_sorted_results_in_local_mode(self, mock_list_emails, mock_service_fn, mock_auth, sample_gmail_results):
        # Test que le mode local récupère les résultats de Gmail
        mock_auth.return_value = Mock()
        mock_service = Mock()
        mock_service_fn.return_value = mock_service
        mock_list_emails.return_value = sample_gmail_results
        
        # Patcher APP_MODE en local
        with patch('app.APP_MODE', 'local'):
            results, service = get_sorted_results()
            
            assert isinstance(results, dict)
            assert service is not None
    
    @patch('app.APP_MODE', 'demo')
    def test_get_sorted_results_returns_sorted_dict(self):
        # Test que les résultats sont triés par count (descending)
        results, _ = get_sorted_results()
        
        # Les résultats doivent être un dictionnaire
        assert isinstance(results, dict)
        
        # Vérifier que les résultats sont triés (le premier doit avoir le plus grand count)
        if results:
            counts = [data.get('count', 0) for data in results.values()]
            assert counts == sorted(counts, reverse=True)


# ============= TESTS DES ACTIONS EMAILS =============

class TestEmailActions:
    """Tests pour les actions sur les emails (suppression, etc)"""
    
    def test_delete_emails_with_valid_message_ids(self, mock_gmail_service):
        # Test suppression d'emails avec une liste d'IDs valides
        from gmail_api.actions import delete_emails
        
        message_ids = ['msg1', 'msg2', 'msg3']
        
        # Appeler la fonction
        delete_emails(mock_gmail_service, message_ids)
        
        # Vérifier que batchModify a été appelé avec les bons IDs
        mock_gmail_service.users().messages().batchModify.assert_called_once()
        
        call_args = mock_gmail_service.users().messages().batchModify.call_args
        assert call_args[1]['userId'] == 'me'
        assert set(call_args[1]['body']['ids']) == set(message_ids)
    
    def test_delete_emails_empty_list(self, mock_gmail_service):
        # Test suppression avec une liste vide (ne doit rien faire)
        from gmail_api.actions import delete_emails
        
        delete_emails(mock_gmail_service, [])
        
        # Vérifier que la fonction n'appelle pas batchModify
        mock_gmail_service.users().messages().batchModify.assert_not_called()
    
    def test_delete_emails_with_label_application(self, mock_gmail_service):
        # Test que les emails sont déplacés en TRASH (via addLabelIds)
        from gmail_api.actions import delete_emails
        
        delete_emails(mock_gmail_service, ['msg1'])
        
        call_args = mock_gmail_service.users().messages().batchModify.call_args
        assert 'TRASH' in call_args[1]['body']['addLabelIds']


# ============= TESTS DES PARSERS =============

class TestParsers:
    """Tests pour les fonctions de parsing d'emails"""
    
    def test_extract_domain_valid_email(self):
        # Test extraction du domaine depuis un email valide
        domain = extract_domain('user@example.com')
        assert domain == 'example.com'
    
    def test_extract_domain_with_display_name(self):
        # Test extraction avec nom d'affichage
        domain = extract_domain('John Doe <john@example.com>')
        assert domain == 'example.com'
    
    def test_extract_domain_invalid_email(self):
        # Test avec un email invalide
        domain = extract_domain('invalid-email')
        assert domain is None
    
    def test_extract_domain_empty_string(self):
        # Test avec une chaîne vide
        domain = extract_domain('')
        assert domain is None
    
    def test_extract_domain_multiple_at_signs(self):
        # Test avec plusieurs arobase (invalide)
        domain = extract_domain('user@@example.com')
        assert domain is None
    
    def test_extract_http_unsubscribe_single_link(self):
        # Test extraction d'un lien unique
        links = extract_http_unsubscribe('<http://unsubscribe.example.com>')
        assert links == ['http://unsubscribe.example.com']
    
    def test_extract_http_unsubscribe_multiple_links(self):
        # Test extraction de plusieurs liens
        unsubscribe_header = '<http://link1.com>, <http://link2.com>, <mailto:unsub@example.com>'
        links = extract_http_unsubscribe(unsubscribe_header)
        assert len(links) == 2
        assert 'http://link1.com' in links
        assert 'http://link2.com' in links
    
    def test_extract_http_unsubscribe_no_http_links(self):
        # Test avec seulement des liens mailto
        links = extract_http_unsubscribe('<mailto:unsub@example.com>')
        assert links == []
    
    def test_extract_http_unsubscribe_empty_header(self):
        # Test avec header vide
        links = extract_http_unsubscribe('')
        assert links == []
    
    def test_extract_http_unsubscribe_none_header(self):
        # Test avec None
        links = extract_http_unsubscribe(None)
        assert links == []


class TestUXFunctions:
    """Tests pour les fonctions UX"""
    
    def test_count_with_without_link_mails_all_with_links(self):
        # Test comptage quand tous les mails ont des liens
        unsubscribe_links = [
            'http://unsub1.com',
            'http://unsub2.com',
            'http://unsub3.com'
        ]
        
        with_link, without_link = count_with_without_link_mails(unsubscribe_links)
        
        assert with_link == 3
        assert without_link == 0
    
    def test_count_with_without_link_mails_all_without_links(self):
        # Test comptage quand aucun mail n'a de lien
        unsubscribe_links = [None, None, None]
        
        with_link, without_link = count_with_without_link_mails(unsubscribe_links)
        
        assert with_link == 0
        assert without_link == 3
    
    def test_count_with_without_link_mails_mixed(self):
        # Test comptage mixte
        unsubscribe_links = [
            'http://unsub1.com',
            None,
            'http://unsub2.com',
            None,
            None
        ]
        
        with_link, without_link = count_with_without_link_mails(unsubscribe_links)
        
        assert with_link == 2
        assert without_link == 3
    
    def test_count_with_without_link_mails_empty_strings(self):
        # Test avec des chaînes vides (considérées comme sans lien)
        unsubscribe_links = [
            'http://unsub1.com',
            '',
            'http://unsub2.com'
        ]
        
        with_link, without_link = count_with_without_link_mails(unsubscribe_links)
        
        assert with_link == 2
        assert without_link == 1
    
    def test_count_with_without_link_mails_empty_list(self):
        # Test avec une liste vide
        with_link, without_link = count_with_without_link_mails([])
        
        assert with_link == 0
        assert without_link == 0


# ============= TESTS DE SAFELIST MANAGER =============

class TestSafelistManager:
    """Tests pour la gestion de la safelist"""
    
    def test_load_safelist_creates_file_if_not_exists(self, temp_safelist_dir):
        # Test création automatique du fichier s'il n'existe pas
        safelist = load_safelist()
        assert isinstance(safelist, list)
        assert os.path.exists('app/config/safelist.json')
    
    def test_add_domain_to_safelist(self, temp_safelist_dir):
        # Test ajout d'un domaine à la safelist
        result = add_domain_to_safelist('example.com')
        assert result is True
        
        safelist = load_safelist()
        assert 'example.com' in safelist
    
    def test_add_domain_to_safelist_duplicate(self, temp_safelist_dir):
        # Test ajout d'un domaine déjà dans la liste
        add_domain_to_safelist('example.com')
        result = add_domain_to_safelist('example.com')
        
        assert result is False
        safelist = load_safelist()
        assert safelist.count('example.com') == 1  # Pas de doublon
    
    def test_add_domain_strips_whitespace(self, temp_safelist_dir):
        # Test suppression des espaces
        add_domain_to_safelist('  EXAMPLE.COM  ')
        safelist = load_safelist()
        assert 'example.com' in safelist
    
    def test_save_and_load_safelist(self, temp_safelist_dir):
        # Test sauvegarde et chargement de la safelist
        # D'abord créer le fichier via load_safelist
        load_safelist()
        
        safelist = ['domain1.com', 'domain2.com', 'domain3.com']
        save_safelist(safelist)
        
        loaded = load_safelist()
        assert loaded == safelist
    
    def test_filter_safelist(self):
        # Test filtrage des domaines basé sur la safelist
        senders = {
            'gmail.com': {'count': 5},
            'example.com': {'count': 3},
            'test.com': {'count': 2}
        }
        
        safelist = ['example.com']
        filtered = filter_safelist(senders, safelist)
        
        assert 'gmail.com' in filtered
        assert 'test.com' in filtered
        assert 'example.com' not in filtered
        assert len(filtered) == 2
    
    def test_filter_safelist_empty_safelist(self):
        # Test filtrage avec une safelist vide
        senders = {
            'gmail.com': {'count': 5},
            'example.com': {'count': 3}
        }
        
        filtered = filter_safelist(senders, [])
        assert filtered == senders


# ============= TESTS DE CONFIGURATION =============

class TestConfig:
    """Tests pour la configuration de l'application"""
    
    def test_validate_config_returns_config(self):
        # Test que validate_config retourne une config valide
        config = validate_config()
        assert config is not None
    
    def test_get_config_development(self):
        # Test récupération config de développement
        with patch.dict(os.environ, {'FLASK_ENV': 'development'}):
            config = get_config()
            assert config.DEBUG is True
            assert config.FLASK_ENV == 'development'
    
    def test_get_config_production(self):
        # Test que la config production force HTTPS en sessions
        # ProductionConfig devrait avoir SESSION_COOKIE_SECURE = True
        assert ProductionConfig.SESSION_COOKIE_SECURE is True
        assert ProductionConfig.DEBUG is False
    
    def test_development_config_session_security(self):
        # Test que la config dev accepte HTTP
        assert DevelopmentConfig.SESSION_COOKIE_SECURE is False
    
    def test_production_config_session_security(self):
        # Test que la config prod force HTTPS
        assert ProductionConfig.SESSION_COOKIE_SECURE is True


# ============= TESTS DES ROUTES (MODE LOCAL) =============

class TestRoutesProduction:
    """Tests des routes en mode production (local)"""
    
    @patch('app.get_sorted_results')
    def test_analyze_route_calls_get_sorted_results(self, mock_get_sorted, client):
        # Test que la route /analyze appelle get_sorted_results
        mock_get_sorted.return_value = ({}, None)
        
        response = client.post('/analyze')
        assert response.status_code == 200
        mock_get_sorted.assert_called_once()
    
    @patch('app.auth')
    @patch('app.get_gmail_service')
    @patch('app.list_unsubscribe_emails')
    def test_analyze_filters_safelist(self, mock_list_emails, mock_service, mock_auth, client, temp_safelist_dir):
        # Test que l'analyse applique le filtre safelist
        mock_auth.return_value = Mock()
        mock_service.return_value = Mock()
        
        mock_results = {
            'gmail.com': {'count': 5, 'message_ids': []},
            'example.com': {'count': 3, 'message_ids': []}
        }
        mock_list_emails.return_value = mock_results
        
        # Ajouter example.com à la safelist
        add_domain_to_safelist('example.com')
        
        # Appeler analyze
        response = client.post('/analyze')
        assert response.status_code == 200
    
    @patch('app.auth')
    @patch('app.get_gmail_service')
    @patch('app.delete_emails')
    def test_delete_route_calls_delete_emails(self, mock_delete, mock_service, mock_auth, client):
        # Test que la route /delete appelle la fonction delete_emails
        mock_auth.return_value = Mock()
        mock_service.return_value = Mock()
        mock_delete.return_value = None
        
        # Préparer LAST_ANALYSIS
        with patch('app.LAST_ANALYSIS', {'example.com': {'count': 3, 'message_ids': ['msg1', 'msg2', 'msg3']}}):
            response = client.post('/delete', data={'domain': 'example.com'})
            assert response.status_code == 200
    
    @patch('app.auth')
    @patch('app.get_gmail_service')
    @patch('app.list_unsubscribe_emails')
    def test_safelist_post_adds_domain(self, mock_list_emails, mock_service, mock_auth, client, temp_safelist_dir):
        # Test ajout d'un domaine à la safelist via POST
        mock_auth.return_value = Mock()
        mock_service.return_value = Mock()
        mock_list_emails.return_value = {}
        
        response = client.post('/safelist', data={'domain': 'example.com'})
        assert response.status_code == 200
        
        safelist = load_safelist()
        assert 'example.com' in safelist


# ============= TESTS D'INTÉGRATION =============

class TestIntegration:
    """Tests d'intégration pour l'application complète"""
    
    @patch('app.auth')
    @patch('app.get_gmail_service')
    @patch('app.list_unsubscribe_emails')
    def test_workflow_analyze_and_safelist(self, mock_list_emails, mock_service, mock_auth, client, temp_safelist_dir):
        # Test du workflow: analyser -> ajouter à safelist -> réanalyser
        mock_auth.return_value = Mock()
        mock_service.return_value = Mock()
        
        # Résultats initiaux
        initial_results = {
            'gmail.com': {'count': 5, 'message_ids': ['m1', 'm2', 'm3', 'm4', 'm5']},
            'example.com': {'count': 3, 'message_ids': ['m6', 'm7', 'm8']}
        }
        mock_list_emails.return_value = initial_results
        
        # Première analyse
        response1 = client.post('/analyze')
        assert response1.status_code == 200
        
        # Ajouter à safelist
        response2 = client.post('/safelist', data={'domain': 'example.com'})
        assert response2.status_code == 200
        
        # Vérifier que la safelist contient le domaine
        safelist = load_safelist()
        assert 'example.com' in safelist
    
    @patch('app.auth')
    @patch('app.get_gmail_service')
    @patch('app.list_unsubscribe_emails')
    @patch('app.delete_emails')
    def test_workflow_analyze_and_delete(self, mock_delete, mock_list_emails, mock_service, mock_auth, client):
        # Test du workflow: analyser -> supprimer
        mock_auth.return_value = Mock()
        mock_service.return_value = Mock()
        mock_delete.return_value = None
        
        results = {
            'example.com': {
                'count': 3, 
                'message_ids': ['m1', 'm2', 'm3'],
                'unsubscribe_links': ['http://unsub.com', None, None]
            }
        }
        mock_list_emails.return_value = results
        
        # Analyser
        response1 = client.post('/analyze')
        assert response1.status_code == 200
        
        # Supprimer
        response2 = client.post('/delete', data={'domain': 'example.com'})
        assert response2.status_code == 200
        mock_delete.assert_called()


# ============= TESTS DE ROBUSTESSE =============

class TestErrorHandling:
    """Tests pour la gestion des erreurs"""
    
    def test_view_domain_with_invalid_domain(self, client):
        # Test accès à un domaine qui n'existe pas
        response = client.get('/domain/invalid_domain_xxxxxxx')
        assert response.status_code in [200, 404]
        assert b'Domaine non trouv' in response.data or b'not found' in response.data.lower()
    
    @patch('app.auth')
    @patch('app.get_gmail_service')
    def test_delete_emails_with_no_message_ids(self, mock_service, mock_auth, client):
        # Test suppression sans IDs de messages
        mock_auth.return_value = Mock()
        mock_service.return_value = Mock()
        
        with patch('app.LAST_ANALYSIS', {'example.com': {'count': 0, 'message_ids': []}}):
            response = client.post('/delete', data={'domain': 'example.com'})
            assert response.status_code == 200
    
    @patch('app.auth')
    @patch('app.get_gmail_service')
    @patch('app.list_unsubscribe_emails')
    def test_analyze_handles_empty_results(self, mock_list_emails, mock_service, mock_auth, client):
        # Test analyse avec résultats vides
        mock_auth.return_value = Mock()
        mock_service.return_value = Mock()
        mock_list_emails.return_value = {}
        
        response = client.post('/analyze')
        assert response.status_code == 200


# ============= TESTS DES CAS LIMITES =============

class TestEdgeCases:
    """Tests pour les cas limites et cas particuliers"""
    
    def test_extract_domain_with_special_characters(self):
        # Test domaine avec caractères spéciaux
        domain = extract_domain('user+tag@sub.example.co.uk')
        assert domain == 'sub.example.co.uk'
    
    def test_safelist_with_mixed_case_domains(self, temp_safelist_dir):
        # Test que les domaines sont convertis en minuscules
        add_domain_to_safelist('EXAMPLE.COM')
        add_domain_to_safelist('example.com')
        
        safelist = load_safelist()
        assert safelist.count('example.com') == 1  # Pas de doublon
    
    def test_extract_unsubscribe_with_spaces(self):
        # Test extraction avec espaces supplémentaires
        links = extract_http_unsubscribe('  <http://link1.com>  ,  <http://link2.com>  ')
        assert len(links) == 2
    
    @patch('app.auth')
    @patch('app.get_gmail_service')
    @patch('app.list_unsubscribe_emails')
    def test_analyze_with_large_dataset(self, mock_list_emails, mock_service, mock_auth, client):
        # Test avec un grand nombre de domaines
        mock_auth.return_value = Mock()
        mock_service.return_value = Mock()
        
        large_results = {
            f'domain{i}.com': {
                'count': i * 10,
                'message_ids': [f'msg{j}' for j in range(i)],
                'subjects': [],
                'unsubscribe_links': []
            }
            for i in range(100)
        }
        mock_list_emails.return_value = large_results
        
        response = client.post('/analyze')
        assert response.status_code == 200
