from flask import Flask, render_template, request, jsonify
from auth.oauth_flow import auth
from gmail_api.fetch_emails import get_gmail_service, list_unsubscribe_emails, SEARCH_QUERY
from gmail_api.actions import delete_emails
from ux.ux import display_domains, select_domain, display_actions, select_action, confirm_deletion, count_with_without_link_mails
from config.safelist_manager import load_safelist, save_safelist, add_domain_to_safelist, filter_safelist
import webbrowser
from datetime import datetime

LAST_ANALYSIS = None
LAST_QUERY = None
LAST_UPDATED_AT = None

app = Flask(__name__)

# Obtenir la liste de mail trier dans l'ordre décroissant
# du nombre de mails par domaine
def get_sorted_results():
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
    return render_template("index.html")

# Affichage des détails d'un domaine
@app.route("/domain/<domain>")
def view_domain(domain):
    if LAST_ANALYSIS:
        domain_data = LAST_ANALYSIS.get(domain)
    else:
        domain_data = None
        
    if not domain_data:
        return render_template("domain.html", domain=domain, error="Domaine non trouvé")
    
    # Compter les mails avec lien de désabonnement
    unsubscribe_count = sum(1 for link in domain_data.get('unsubscribe_links', []) if link)
    
    return render_template(
        "domain.html", 
        domain=domain, 
        domain_data=domain_data,
        total_count=domain_data.get('count', 0),
        unsubscribe_count=unsubscribe_count
    )

# Analyse de la boîte mail
@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    global LAST_ANALYSIS, LAST_QUERY, LAST_UPDATED_AT
    analysis, _ = get_sorted_results()
    LAST_ANALYSIS = analysis
    LAST_QUERY = SEARCH_QUERY
    LAST_UPDATED_AT = datetime.now()
    return render_template("results.html", data=analysis, last_query=LAST_QUERY, last_updated_at=LAST_UPDATED_AT)

# Suppression des mails
@app.route("/delete", methods=["POST"])
def delete():
    global LAST_ANALYSIS
    
    domain = request.form.get("domain")
    message = None
    message_type = None

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

    return render_template("results.html", data=sorted_results, message=message, message_type=message_type, last_query=LAST_QUERY, last_updated_at=LAST_UPDATED_AT)

# Ajout à la safelist
@app.route("/safelist", methods=["GET"])
def view_safelist():
    safelist_domains = load_safelist()
    return render_template("safelist.html", safelist_domains=safelist_domains)

@app.route("/safelist", methods=["POST"])
def add_safelist():
    global LAST_ANALYSIS
    
    domain = request.form.get("domain")
    message = None
    message_type = None

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

    return render_template("results.html", data=sorted_results, message=message, message_type=message_type, last_query=LAST_QUERY, last_updated_at=LAST_UPDATED_AT)

@app.route("/remove-from-safelist", methods=["POST"])
def remove_from_safelist():
    domain = request.form.get("domain")
    message = None
    message_type = None

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
    return render_template("safelist.html", safelist_domains=safelist_domains, message=message, message_type=message_type)

# Actions sur un domaine
@app.route("/domain/<domain>/delete-all", methods=["POST"])
def delete_domain_all(domain):
    global LAST_ANALYSIS
    
    message = None
    message_type = None

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

    domain_data = LAST_ANALYSIS.get(domain) if LAST_ANALYSIS else None
    unsubscribe_count = sum(1 for link in domain_data.get('unsubscribe_links', []) if link) if domain_data else 0
    
    return render_template(
        "domain.html",
        domain=domain,
        domain_data=domain_data,
        total_count=domain_data.get('count', 0) if domain_data else 0,
        unsubscribe_count=unsubscribe_count,
        message=message,
        message_type=message_type
    )

@app.route("/domain/<domain>/delete-with-link", methods=["POST"])
def delete_domain_with_link(domain):
    global LAST_ANALYSIS
    
    message = None
    message_type = None

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

                # Mettre à jour LAST_ANALYSIS
                if LAST_ANALYSIS and domain in LAST_ANALYSIS:
                    LAST_ANALYSIS[domain]["message_ids"] = [
                        mid for i, mid in enumerate(domain_data["message_ids"])
                        if not domain_data["unsubscribe_links"][i]
                    ]
                    LAST_ANALYSIS[domain]["unsubscribe_links"] = [
                        link for link in domain_data["unsubscribe_links"] if not link
                    ]
                    LAST_ANALYSIS[domain]["count"] -= count

    except Exception as e:
        message = f"✗ Erreur lors de la suppression : {str(e)}"
        message_type = "error"

    domain_data = LAST_ANALYSIS.get(domain) if LAST_ANALYSIS else None
    unsubscribe_count = sum(1 for link in domain_data.get('unsubscribe_links', []) if link) if domain_data else 0
    
    return render_template(
        "domain.html",
        domain=domain,
        domain_data=domain_data,
        total_count=domain_data.get('count', 0) if domain_data else 0,
        unsubscribe_count=unsubscribe_count,
        message=message,
        message_type=message_type
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
    app.run(debug=True)

# def main():
#     # Connexion avec OAuth2
#     credentials = auth()

#     # Service pour la récupération des mails
#     service = get_gmail_service(credentials)

#     # Récupération des mails
#     dict_senders = list_unsubscribe_emails(service)
    
#     # Si pas de domaine
#     if not dict_senders:
#         print("Aucun domaine à traiter")
#         return
    
#     # Chargement de la safelist
#     safelist = load_safelist()

#     # Filtrer les domaines
#     filtered_senders = filter_safelist(dict_senders, safelist)

#     # Lister les domaines avec le nombre de mails
#     mapping = {i + 1: {'domain': domain, 'count': filtered_senders[domain]['count'], 'subjects': filtered_senders[domain]['subjects'], 'unsubscribe_links': filtered_senders[domain]['unsubscribe_links']} 
#            for i, domain in enumerate(filtered_senders)}

#     # Tant qu'il y a des domaines dans mapping
#     while mapping:

#         # Affichage de la liste
#         display_domains(mapping)

#         # Choix du domaine
#         domain, count, subjects = select_domain(mapping)

#         # Affichage du menu des actions
#         display_actions(domain, count, filtered_senders[domain]['unsubscribe_links'])

#         # Choix de l'action
#         action = select_action()

#         match(action):
#             # Quitter le programme
#             case 0: break
#             # Supprimer tous les mails
#             case 1:
#                 if confirm_deletion(domain, count, subjects, filtered_senders[domain]['unsubscribe_links']) == True:
#                     delete_emails(service, filtered_senders[domain]["message_ids"])
#                     del filtered_senders[domain]
#                     mapping = {i + 1: {'domain': d, 'count': filtered_senders[d]['count'], 'subjects': filtered_senders[d]['subjects'], 'unsubscribe_links': filtered_senders[d]['unsubscribe_links']} 
#                             for i, d in enumerate(filtered_senders)}
#             # Supprimer seulement les mails avec lien de désinscription
#             case 2:
#                 ids_with_link = [filtered_senders[domain]["message_ids"][i] 
#                                 for i, link in enumerate(filtered_senders[domain]["unsubscribe_links"]) if link]
#                 if ids_with_link:
#                     if confirm_deletion(domain, len(ids_with_link), subjects, filtered_senders[domain]['unsubscribe_links']) == True:
#                         delete_emails(service, ids_with_link)
#                         # Mettre à jour les données du domaine
#                         filtered_senders[domain]["message_ids"] = [filtered_senders[domain]["message_ids"][i] 
#                                                                     for i, link in enumerate(filtered_senders[domain]["unsubscribe_links"]) if not link]
#                         filtered_senders[domain]["unsubscribe_links"] = [link for link in filtered_senders[domain]["unsubscribe_links"] if not link]
#                         filtered_senders[domain]["count"] -= len(ids_with_link)
#                 else:
#                     print("Aucun mail avec lien de désinscription pour ce domaine.")
#             # Ajouter à la safelist
#             case 3:
#                 add_domain_to_safelist(domain)
#                 del filtered_senders[domain]
#                 mapping = {i + 1: {'domain': d, 'count': filtered_senders[d]['count'], 'subjects': filtered_senders[d]['subjects'], 'unsubscribe_links': filtered_senders[d]['unsubscribe_links']} 
#                             for i, d in enumerate(filtered_senders)}
#             # Retour au menu principale
#             case 4:
#                 continue

#             case _:
#                 print("Choix invalide")

#     # Sauvegarde de la safelist
#     save_safelist(safelist)
    
# main()