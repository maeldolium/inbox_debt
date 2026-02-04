from auth.oauth_flow import auth
from gmail_api.fetch_emails import get_gmail_service, list_unsubscribe_emails
from gmail_api.actions import trash_message
import webbrowser

def main():
    # Connexion avec OAuth2
    credentials = auth()

    # Service pour la récupération des mails
    service = get_gmail_service(credentials)

    # Récupération des mails
    dict_senders = list_unsubscribe_emails(service)
    
    if not dict_senders:
        print("Aucun domaine à traiter")
        return

    # Afficher les domaines et leur nombre d'occurrences
    print(f"{'Domain':<30} {'Count':<8} {'Subjects':<10} {'Links':<10}")
    print("-" * 60)
    for domain, data in dict_senders.items():
        print(f"{domain:<30} {data['count']:<8} {len(data['subjects']):<10} {len(data['unsubscribe_links']):<10}")
    
    # Lister les domaines
    mapping = {i + 1: domain for i, domain in enumerate(dict_senders)}

    print("Quel domaine voulez-vous supprimer ?")

    for id, domain in mapping.items():
        print(f'{id}. {domain}')

    # Choix du domaine par l'utilisateur et suppresion des mails
    # correspondant si l'utilisateur confirme son choix
    while True:
        try:
            user_choice = int(input("Votre choix: "))

            if user_choice in mapping:
                domain = mapping[user_choice]

                user_choice = str(input(f'Etes vous sûr de vouloir supprimer {domain} ? (y/n)'))

                if user_choice == 'y':
                    trash_message(service, dict_senders[domain]["message_ids"])
                    return
            else:
                print("Choix invalide !")
        except ValueError:
            print("Entrez un numéro !")    
    
main()