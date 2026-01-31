from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_gmail_service(credentials):
    # Créer le service pour la récupération de mails
    service = build("gmail", "v1", credentials=credentials)

    return service


def list_unsubscribe_emails(service):

    # Dictionnaire expéditeurs mails
    dict_senders = {}

    # Demander à Gmail la liste des mails qui match la recherhe
    result = service.users().messages().list(
        userId="me",
        q="unsubscribe",
        maxResults=20
    ).execute()

    messages = result.get("messages", [])

    # Vérifier qu'il y a des messages
    if not messages:
        print("Aucun mail trouvé")
        return
    
    # Pour chaque message
    for message in messages:
        message_id = message["id"]

        # Récupérer les headers des messages
        detail = service.users().messages().get(
            userId="me",
            id=message_id,
            format="metadata",
            metadataHeaders = ["From", "Subject", "List-Unsubscribe"]
        ).execute()

        headers = detail["payload"]["headers"]

        from_value = ""
        subject_value = ""
        unsubscribe_value = ""

        # Parcourir les headers pour trouver ceux voulue
        for header in headers:

            if header["name"] == "From":
                from_value = header["value"]

            if header["name"] == "Subject":
                subject_value = header["value"]

            if header["name"] == "List-Unsubscribe":
                unsubscribe_value = header["value"]

        # Remplir le dictionnaire d'expéditeurs
        email = extract_email(from_value, "<", ">")

        domain = extract_domain(email, "@")

        # Afficher les résultats
        print(f'{from_value}')
        print(f'{subject_value}')
        print(f'{unsubscribe_value}')
        print(f"{email}")
        print(f"{domain}")
        print("-------------")



        if not domain in dict_senders:
            dict_senders[domain] = 1
        else:
            dict_senders[domain] += 1

    print(f'{dict_senders}')
        
# Recherche de l'adresse email à partir du header
def extract_email(from_value, first, last):
    start = from_value.index(first) + len(first)
    end = from_value.index(last, start)

    return from_value[start:end]
            
# Recherche du domaine
def extract_domain(email, at):
    start = email.index(at) + 1
    end = len(email)

    return email[start:end]