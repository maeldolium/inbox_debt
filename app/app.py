from auth.oauth_flow import auth
from gmail_api.fetch_emails import get_gmail_service, list_unsubscribe_emails
from gmail_api.actions import trash_message
from config.config import SAFE_DOMAINS
from config.safelist_manager import load_safelist, save_safelist, add_domain_to_safelist
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
    filtered_senders = {}

    for domain in dict_senders:
        if domain not in safelist:
            filtered_senders[domain] = dict_senders[domain]

    # Lister les domaines avec le nombre de mails
    mapping = {i + 1: {'domain': domain, 'count': filtered_senders[domain]['count']} 
           for i, domain in enumerate(filtered_senders)}

    # Tant qu'il y a des domaines dans mapping
    # Afficher le menu
    while mapping:
        # Choix du domaine par l'utilisateur
        print("Quel domaine voulez-vous traiter ?")

        for id, data in mapping.items():
            print(f'{id}. {data["domain"]} ({data["count"]} mails)')

        # Choix de l'utilisateur
        try:
            domain_id = int(input("Votre choix: "))
            # Si choix valide
            if domain_id in mapping:
                domain = mapping[domain_id]['domain']
                count = mapping[domain_id]['count']

                # Action à réaliser
                print("Que voulez vous faire ?\n 1. Supprimer\n 2. Ajouter à la safelist\n 3. Retour")

                action = int(input("Votre choix: "))

                match(action):
                    # Suppression
                    case 1:
                        confirmation = str(input(f'Êtes-vous sûr de vouloir supprimer {domain} ? ({count} mails) (y/n)'))
                
                        # Validation du choix
                        if confirmation == 'y':
                            trash_message(service, filtered_senders[domain]["message_ids"])
                            del filtered_senders[domain]
                            mapping = {i + 1: {'domain': d, 'count': filtered_senders[d]['count']} 
                                      for i, d in enumerate(filtered_senders)}
                    #  Ajout à la safelist
                    case 2:
                        add_domain_to_safelist(domain)
                        del filtered_senders[domain]
                        mapping = {i + 1: {'domain': d, 'count': filtered_senders[d]['count']} 
                                  for i, d in enumerate(filtered_senders)}
                    #  Retour
                    case 3:
                        continue
                    #  Choix invalide
                    case _:
                        print("Choix invalide")
                    
            # Sinon
            else:
                print("Choix invalide !")
        # Choix ne correspond pas
        except ValueError:
            print("Entrez un numéro !")
                    


                


    
main()