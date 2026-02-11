from auth.oauth_flow import auth
from gmail_api.fetch_emails import get_gmail_service, list_unsubscribe_emails
from gmail_api.actions import trash_message
from config.config import SAFE_DOMAINS
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
    
    filtered_senders = {}

    # Filtrer les domaines
    for domain in dict_senders:
        if domain not in SAFE_DOMAINS:
            filtered_senders[domain] = dict_senders[domain]

    # Lister les domaines avec le nombre de mails
    mapping = {i + 1: {'domain': domain, 'count': filtered_senders[domain]['count']} 
           for i, domain in enumerate(filtered_senders)}


    # Choix du domaine par l'utilisateur
    print("Quel domaine voulez-vous supprimer ?")

    for id, data in mapping.items():
        print(f'{id}. {data["domain"]} ({data["count"]} mails)')

    while True:
        try:
            user_choice = int(input("Votre choix: "))
            # Si choix valide
            if user_choice in mapping:
                domain = mapping[user_choice]['domain']
                count = mapping[user_choice]['count']

                user_choice = str(input(f'Êtes-vous sûr de vouloir supprimer {domain} ? ({count} mails) (y/n)'))
                # Validation du choix
                if user_choice == 'y':
                    trash_message(service, filtered_senders[domain]["message_ids"])
                    return
            # Sinon
            else:
                print("Choix invalide !")
        except ValueError:
            print("Entrez un numéro !")    
    
main()