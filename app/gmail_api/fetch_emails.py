from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from gmail_api.parsers import extract_domain, extract_http_unsubscribe

def get_gmail_service(credentials):
    # Créer le service pour la récupération de mails
    service = build("gmail", "v1", credentials=credentials)

    return service


def list_unsubscribe_emails(service):

    # Dictionnaire expéditeurs mails
    dict_senders = {}

    all_messages = []
    page_token = None

    # Demander à Gmail la liste des mails qui match la recherhe
    while True:
        result = service.users().messages().list(
            userId="me",
            q="category:promotions OR unsubscribe OR \"désinscrire\"",
            maxResults=100,
            pageToken=page_token
        ).execute()

        messages = result.get("messages", [])

         # Vérifier qu'il y a des messages
        if not messages:
            print("Aucun mail trouvé")
            return dict_senders

        all_messages.extend(messages)

        page_token = result.get("nextPageToken")

        if not page_token:
            break
    
    # Pour chaque message
    for message in all_messages:
        message_id = message["id"]

        # Récupérer les headers des messages
        detail = service.users().messages().get(
            userId="me",
            id=message_id,
            format="metadata",
            metadataHeaders = ["From", "Subject", "List-Unsubscribe"]
        ).execute()

        headers = detail["payload"]["headers"]

        # Initialiser l'expéditeur, le sujet et le lien de désinscription
        from_value = ""
        subject_value = ""
        unsubscribe_links = ""

        # Parcourir les headers pour trouver ceux voulue
        for header in headers:

            if header["name"] == "From":
                from_value = header["value"]

            if header["name"] == "Subject":
                subject_value = header["value"]

            if header["name"] == "List-Unsubscribe":
                unsubscribe_links = header["value"]

        # Rechercher l'email et le nom de domaine dans le header
        email, domain = extract_domain(from_value)

        # Extraire les liens https de désinscription
        unsubscribe_links = extract_http_unsubscribe(unsubscribe_links)

        # Si le domaine n'est pas dans le dictionnaire
        if not domain in dict_senders:
            dict_senders[domain] = {
                "count": 1,
                "subjects": [subject_value],
                "unsubscribe_links": [unsubscribe_links],
                "message_ids": [message_id]
            }
        # Sinon rajouter un occurrence et les infos
        else:
            dict_senders[domain]["count"] += 1
            dict_senders[domain]["subjects"].append(subject_value)
            dict_senders[domain]["unsubscribe_links"].append(unsubscribe_links)
            dict_senders[domain]["message_ids"].append(message_id)

    return dict_senders
            
