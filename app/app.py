from auth.oauth_flow import auth
from gmail_api.fetch_emails import get_gmail_service, list_unsubscribe_emails
from gmail_api.actions import delete_emails
from ux.ux import display_domains, select_domain, display_actions, select_action, confirm_deletion, count_with_without_link_mails
from config.safelist_manager import load_safelist, save_safelist, add_domain_to_safelist, filter_safelist
import webbrowser

def main():
    # Connexion avec OAuth2
    credentials = auth()

    # Service pour la récupération des mails
    service = get_gmail_service(credentials)

    # Récupération des mails
    dict_senders = list_unsubscribe_emails(service)
    
    # Si pas de domaine
    if not dict_senders:
        print("Aucun domaine à traiter")
        return
    
    # Chargement de la safelist
    safelist = load_safelist()

    # Filtrer les domaines
    filtered_senders = filter_safelist(dict_senders, safelist)

    # Lister les domaines avec le nombre de mails
    mapping = {i + 1: {'domain': domain, 'count': filtered_senders[domain]['count'], 'subjects': filtered_senders[domain]['subjects'], 'unsubscribe_links': filtered_senders[domain]['unsubscribe_links']} 
           for i, domain in enumerate(filtered_senders)}

    # Tant qu'il y a des domaines dans mapping
    while mapping:

        # Affichage de la liste
        display_domains(mapping)

        # Choix du domaine
        domain, count, subjects = select_domain(mapping)

        # Affichage du menu des actions
        display_actions(domain, count, filtered_senders[domain]['unsubscribe_links'])

        # Choix de l'action
        action = select_action()

        match(action):
            # Quitter le programme
            case 0: break
            # Supprimer tous les mails
            case 1:
                if confirm_deletion(domain, count, subjects, filtered_senders[domain]['unsubscribe_links']) == True:
                    delete_emails(service, filtered_senders[domain]["message_ids"])
                    del filtered_senders[domain]
                    mapping = {i + 1: {'domain': d, 'count': filtered_senders[d]['count'], 'subjects': filtered_senders[d]['subjects'], 'unsubscribe_links': filtered_senders[d]['unsubscribe_links']} 
                            for i, d in enumerate(filtered_senders)}
            # Supprimer seulement les mails avec lien de désinscription
            case 2:
                ids_with_link = [filtered_senders[domain]["message_ids"][i] 
                                for i, link in enumerate(filtered_senders[domain]["unsubscribe_links"]) if link]
                if ids_with_link:
                    if confirm_deletion(domain, len(ids_with_link), subjects, filtered_senders[domain]['unsubscribe_links']) == True:
                        delete_emails(service, ids_with_link)
                        # Mettre à jour les données du domaine
                        filtered_senders[domain]["message_ids"] = [filtered_senders[domain]["message_ids"][i] 
                                                                    for i, link in enumerate(filtered_senders[domain]["unsubscribe_links"]) if not link]
                        filtered_senders[domain]["unsubscribe_links"] = [link for link in filtered_senders[domain]["unsubscribe_links"] if not link]
                        filtered_senders[domain]["count"] -= len(ids_with_link)
                else:
                    print("Aucun mail avec lien de désinscription pour ce domaine.")
            # Ajouter à la safelist
            case 3:
                add_domain_to_safelist(domain)
                del filtered_senders[domain]
                mapping = {i + 1: {'domain': d, 'count': filtered_senders[d]['count'], 'subjects': filtered_senders[d]['subjects'], 'unsubscribe_links': filtered_senders[d]['unsubscribe_links']} 
                            for i, d in enumerate(filtered_senders)}
            # Retour au menu principale
            case 4:
                continue

            case _:
                print("Choix invalide")

    # Sauvegarde de la safelist
    save_safelist(safelist)
    
main()