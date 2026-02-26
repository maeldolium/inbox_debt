from flask import Flask, render_template, request
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

# Analyse de la boîte mail
@app.route("/analyze", methods=["POST"])
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
        sorted_results = LAST_ANALYSIS, last_query=LAST_QUERY, last_updated_at=LAST_UPDATED_AT

    return render_template("results.html", data=sorted_results, message=message, message_type=message_type)

# Ajout à la safelist
@app.route("/safelist", methods=["POST"])
def safelist():
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