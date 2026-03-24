from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from auth.oauth_flow import auth
from gmail_api.fetch_emails import get_gmail_service, list_unsubscribe_emails, SEARCH_QUERY
from gmail_api.actions import delete_emails
from ux.ux import display_domains, select_domain, display_actions, select_action, confirm_deletion, count_with_without_link_mails
from config.safelist_manager import load_safelist, save_safelist, add_domain_to_safelist, filter_safelist
from config.settings import APP_MODE
from config.config import get_config, validate_config
import webbrowser
from datetime import datetime
import json
import os
import secrets

LAST_ANALYSIS = None
LAST_QUERY = None
LAST_UPDATED_AT = None

app = Flask(__name__)

# Charger la clé depuis env, ou générer une clé de développement
secret_key = os.environ.get('FLASK_SECRET_KEY')
if not secret_key:
    # Fallback pour dev: génère une clé aléatoire (sera différente à chaque redémarrage)
    secret_key = secrets.token_hex(32)
    print("FLASK_SECRET_KEY non trouvée. Clé auto-générée (sessions non persistantes)")

app.config['SECRET_KEY'] = secret_key

# Valider et charger la configuration
config = validate_config()
app.config.from_object(config)

# Définir la secret_key de manière sécurisée
app.secret_key = config.SECRET_KEY

print(f"\n{'='*70}")
print(f"Application initialisée")
print(f"   Mode : {config.APP_MODE.upper()}")
print(f"   Environnement : {config.FLASK_ENV}")
print(f"   Debug : {app.debug}")
print(f"{'='*70}\n")

# Charger les données de démonstration
def load_mock_data():
    mock_file = os.path.join(os.path.dirname(__file__), 'mock', 'mock_analysis.json')
    
    try:
        with open(mock_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Fichier {mock_file} non trouvé!")
        return {}
    except json.JSONDecodeError as e:
        print(f"Erreur de parsing JSON: {e}")
        return {}

# Trie des mails par ordre croissant
def get_sorted_results():
 
    # En mode démo, charger les données fictives depuis le JSON
    if APP_MODE == "demo":
        mock_data = load_mock_data()
        results = dict(sorted(mock_data.items(), key=lambda x: x[1]['count'], reverse=True))
        return results, None
    
    # En mode local, accéder à l'API Gmail réelle
    credentials = auth()
    service = get_gmail_service(credentials)
    results = list_unsubscribe_emails(service)
    
    # Charger et appliquer le filtre de safelist
    safelist = load_safelist()
    filtered_results = filter_safelist(results, safelist)
    
    return dict(sorted(filtered_results.items(), key=lambda x: x[1]['count'], reverse=True)), service

# Affichage de l'accueil
@app.route("/")
def index():
    return render_template("index.html", app_mode=APP_MODE)

# Affichage des détails d'un domaine
@app.route("/domain/<domain>")
def view_domain(domain):
    if LAST_ANALYSIS:
        domain_data = LAST_ANALYSIS.get(domain)
    else:
        domain_data = None
        
    if not domain_data:
        return render_template("domain.html", domain=domain, error="Domaine non trouvé", app_mode=APP_MODE)
    
    # Compter les mails avec lien de désabonnement
    unsubscribe_count = sum(1 for link in domain_data.get('unsubscribe_links', []) if link)
    
    return render_template(
        "domain.html", 
        domain=domain, 
        domain_data=domain_data,
        total_count=domain_data.get('count', 0),
        unsubscribe_count=unsubscribe_count,
        app_mode=APP_MODE
    )

# Analyse de la boîte mail
@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    global LAST_ANALYSIS, LAST_QUERY, LAST_UPDATED_AT
    analysis, _ = get_sorted_results()
    LAST_ANALYSIS = analysis
    LAST_QUERY = SEARCH_QUERY if APP_MODE == "local" else "DEMO_MODE (données fictives)"
    LAST_UPDATED_AT = datetime.now()
    
    # Récupérer les messages de la session s'ils existent
    message = session.pop('message', None)
    message_type = session.pop('message_type', None)
    
    return render_template("results.html", data=analysis, message=message, message_type=message_type, last_query=LAST_QUERY, last_updated_at=LAST_UPDATED_AT, app_mode=APP_MODE)

# Suppression des mails
@app.route("/delete", methods=["POST"])
def delete():
    global LAST_ANALYSIS
    
    domain = request.form.get("domain")
    message = None
    message_type = None

    # En mode démo, afficher un message informatif
    if APP_MODE == "demo":
        # Compter les mails du domaine
        domain_count = LAST_ANALYSIS.get(domain, {}).get('count', 0) if LAST_ANALYSIS else 0
        message = f"[{APP_MODE.upper()}] {domain_count} mail(s) simulé(s) supprimé(s) de {domain}"
        message_type = "info"
        
        # Supprimer le domaine de LAST_ANALYSIS (simulation)
        if LAST_ANALYSIS and domain in LAST_ANALYSIS:
            del LAST_ANALYSIS[domain]
        
        sorted_results = LAST_ANALYSIS
        return render_template("results.html", data=sorted_results, message=message, message_type=message_type, last_query=LAST_QUERY, last_updated_at=LAST_UPDATED_AT, app_mode=APP_MODE)

    # Mode local : suppression réelle
    try:
        credentials = auth()
        service = get_gmail_service(credentials)
        results = list_unsubscribe_emails(service)

        message_ids = results[domain]["message_ids"]
        count = len(message_ids)

        delete_emails(service, message_ids)

        message = f"✓ {count} mails de {domain} ont été supprimés avec succès"
        message_type = "success"
        
        # Supprimer le domaine de LAST_ANALYSIS
        if LAST_ANALYSIS and domain in LAST_ANALYSIS:
            del LAST_ANALYSIS[domain]
        
        sorted_results = LAST_ANALYSIS

    except Exception as e:
        message = f"✗ Erreur lors de la suppression : {str(e)}"
        message_type = "error"
        sorted_results = LAST_ANALYSIS

    return render_template("results.html", data=sorted_results, message=message, message_type=message_type, last_query=LAST_QUERY, last_updated_at=LAST_UPDATED_AT, app_mode=APP_MODE)

# Ajout à la safelist
@app.route("/safelist", methods=["GET"])
def view_safelist():
    safelist_domains = load_safelist()
    return render_template("safelist.html", safelist_domains=safelist_domains, app_mode=APP_MODE)

@app.route("/safelist", methods=["POST"])
def add_safelist():
    global LAST_ANALYSIS
    
    domain = request.form.get("domain")
    message = None
    message_type = None

    # En mode démo, simulation de modification de la safelist
    if APP_MODE == "demo":
        message = f"✓ [{APP_MODE.upper()}] {domain} simulé en safelist"
        message_type = "success"
        
        # Supprimer le domaine de LAST_ANALYSIS (simulation)
        if LAST_ANALYSIS and domain in LAST_ANALYSIS:
            del LAST_ANALYSIS[domain]
        
        sorted_results = LAST_ANALYSIS
        return render_template("results.html", data=sorted_results, message=message, message_type=message_type, last_query=LAST_QUERY, last_updated_at=LAST_UPDATED_AT, app_mode=APP_MODE)

    # Mode local : modification de la safelist
    try:
        add_domain_to_safelist(domain)
        message = f"✓ {domain} ajouté à la safelist !"
        message_type = "success"
        
        # Supprimer le domaine de LAST_ANALYSIS
        if LAST_ANALYSIS and domain in LAST_ANALYSIS:
            del LAST_ANALYSIS[domain]
        
        sorted_results = LAST_ANALYSIS

    except Exception as e:
        message = f"✗ Erreur lors de l'ajout à la safelist : {str(e)}"
        message_type = "error"
        sorted_results = LAST_ANALYSIS

    return render_template("results.html", data=sorted_results, message=message, message_type=message_type, last_query=LAST_QUERY, last_updated_at=LAST_UPDATED_AT, app_mode=APP_MODE)

@app.route("/remove-from-safelist", methods=["POST"])
def remove_from_safelist():
    domain = request.form.get("domain")
    message = None
    message_type = None

    # En mode démo, simulation de modification de la safelist
    if APP_MODE == "demo":
        message = f"✓ [{APP_MODE.upper()}] {domain} retiré de la safelist simulée"
        message_type = "success"
    else:
        # Mode local : modification de la safelist
        try:
            safelist = load_safelist()
            domain = domain.lower().strip()
            
            if domain in safelist:
                safelist.remove(domain)
                save_safelist(safelist)
                message = f"✓ {domain} supprimé de la safelist !"
                message_type = "success"
            else:
                message = f"✗ {domain} n'est pas dans la safelist"
                message_type = "error"

        except Exception as e:
            message = f"✗ Erreur lors de la suppression : {str(e)}"
            message_type = "error"

    safelist_domains = load_safelist()
    return render_template("safelist.html", safelist_domains=safelist_domains, message=message, message_type=message_type, app_mode=APP_MODE)

# Actions sur un domaine
@app.route("/domain/<domain>/delete-all", methods=["POST"])
def delete_domain_all(domain):
    global LAST_ANALYSIS
    
    message = None
    message_type = None

    # En mode démo, afficher un message informatif
    if APP_MODE == "demo":
        # Compter les mails du domaine
        domain_count = LAST_ANALYSIS.get(domain, {}).get('count', 0) if LAST_ANALYSIS else 0
        message = f"[{APP_MODE.upper()}] {domain_count} mail(s) simulé(s) supprimé(s) de {domain}"
        message_type = "info"
        
        # Supprimer le domaine de LAST_ANALYSIS (simulation)
        if LAST_ANALYSIS and domain in LAST_ANALYSIS:
            del LAST_ANALYSIS[domain]
    else:
        # Mode local : suppression réelle
        try:
            credentials = auth()
            service = get_gmail_service(credentials)
            results = list_unsubscribe_emails(service)

            if domain not in results:
                message = f"✗ Domaine {domain} non trouvé"
                message_type = "error"
            else:
                message_ids = results[domain]["message_ids"]
                count = len(message_ids)

                delete_emails(service, message_ids)

                message = f"✓ {count} mails de {domain} ont été supprimés avec succès"
                message_type = "success"
                
                # Supprimer le domaine de LAST_ANALYSIS
                if LAST_ANALYSIS and domain in LAST_ANALYSIS:
                    del LAST_ANALYSIS[domain]

        except Exception as e:
            message = f"✗ Erreur lors de la suppression : {str(e)}"
            message_type = "error"

    # Stocker les messages dans la session et rediriger
    session['message'] = message
    session['message_type'] = message_type
    return redirect(url_for('analyze'))

@app.route("/domain/<domain>/delete-with-link", methods=["POST"])
def delete_domain_with_link(domain):
    global LAST_ANALYSIS
    
    message = None
    message_type = None

    # En mode démo, afficher un message informatif
    if APP_MODE == "demo":
        domain_data = LAST_ANALYSIS.get(domain) if LAST_ANALYSIS else None
        if domain_data:
            # Compter les mails avec lien (simulation)
            links_with_url = [link for link in domain_data.get('unsubscribe_links', []) if link]
            count = len(links_with_url)
            
            if count > 0:
                message = f"[{APP_MODE.upper()}] {count} mail(s) avec lien simulé(s) supprimé(s) de {domain}"
                message_type = "info"
                del LAST_ANALYSIS[domain]
            else:
                message = f"✗ Aucun mail avec lien de désabonnement pour {domain}"
                message_type = "error"
        else:
            message = f"✗ Domaine {domain} non trouvé"
            message_type = "error"
    else:
        # Mode local : suppression réelle
        try:
            credentials = auth()
            service = get_gmail_service(credentials)
            results = list_unsubscribe_emails(service)

            if domain not in results:
                message = f"✗ Domaine {domain} non trouvé"
                message_type = "error"
            else:
                domain_data = results[domain]
                message_ids_with_link = [
                    domain_data["message_ids"][i] 
                    for i, link in enumerate(domain_data["unsubscribe_links"]) 
                    if link
                ]
                
                if not message_ids_with_link:
                    message = f"✗ Aucun mail avec lien de désabonnement pour {domain}"
                    message_type = "error"
                else:
                    count = len(message_ids_with_link)
                    delete_emails(service, message_ids_with_link)
                    
                    message = f"✓ {count} mails de {domain} avec lien ont été supprimés"
                    message_type = "success"

                    # Récupérer les données fraîches après suppression
                    fresh_results = list_unsubscribe_emails(service)
                    
                    # Mettre à jour LAST_ANALYSIS avec les données fraîches
                    if fresh_results and domain in fresh_results:
                        LAST_ANALYSIS[domain] = fresh_results[domain]
                    elif LAST_ANALYSIS and domain in LAST_ANALYSIS:
                        # Si le domaine n'existe plus, le supprimer
                        del LAST_ANALYSIS[domain]

        except Exception as e:
            message = f"✗ Erreur lors de la suppression : {str(e)}"
            message_type = "error"

    # Vérifier si le domaine n'a plus de mails
    domain_data = LAST_ANALYSIS.get(domain) if LAST_ANALYSIS else None
    
    # Si le domaine n'existe plus ou n'a plus de mails, rediriger vers la liste
    if not domain_data or domain_data.get('count', 0) <= 0:
        if LAST_ANALYSIS and domain in LAST_ANALYSIS:
            del LAST_ANALYSIS[domain]
        # Stocker les messages dans la session et rediriger
        session['message'] = message
        session['message_type'] = message_type
        return redirect(url_for('analyze'))
    else:
        # Sinon, rester sur la page du domaine avec les infos à jour
        unsubscribe_count = sum(1 for link in domain_data.get('unsubscribe_links', []) if link) if domain_data else 0
        return render_template(
            "domain.html",
            domain=domain,
            domain_data=domain_data,
            total_count=domain_data.get('count', 0) if domain_data else 0,
            unsubscribe_count=unsubscribe_count,
            message=message,
            message_type=message_type,
            app_mode=APP_MODE
        )

@app.route("/domain/<domain>/open-unsubscribe", methods=["POST"])
def open_unsubscribe_link(domain):
    domain_data = LAST_ANALYSIS.get(domain) if LAST_ANALYSIS else None
    
    if not domain_data:
        return jsonify({"error": "Domaine non trouvé"}), 404
    
    # Trouver le dernier lien non-vide
    unsubscribe_link = None
    for link in reversed(domain_data.get('unsubscribe_links', [])):
        if link:
            unsubscribe_link = link
            break
    
    if not unsubscribe_link:
        return jsonify({"error": "Aucun lien de désabonnement trouvé"}), 404
    
    # Retourner le lien en JSON
    return jsonify({"link": unsubscribe_link})



if __name__ == "__main__":
    # Lire le port depuis la variable d'environnement
    # Default à 5000 en local pour le développement
    port = int(os.getenv("PORT", 5000))
    
    # Afficher les infos de démarrage
    print(f"\n{'='*70}")
    print(f"Serveur démarrage sur le port {port}")
    print(f"   Debug: {app.debug}")
    print(f"   URL: http://localhost:{port}")
    print(f"{'='*70}\n")
    
    # Lancer l'app
    app.run(host="0.0.0.0", port=port, debug=app.debug)