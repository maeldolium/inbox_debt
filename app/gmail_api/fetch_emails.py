from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from gmail_api.parsers import extract_domain, extract_http_unsubscribe
import time

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
    
    def callback(request_id, response, exception):
        if exception:
            print("Erreur :", exception)
            return

        headers = response.get("payload", {}).get("headers", [])

        from_header = None
        subject = None
        unsubscribe = None

        for header in headers:
            if header["name"] == "From":
                from_header = header["value"]
            elif header["name"] == "Subject":
                subject = header["value"]
            elif header["name"] == "List-Unsubscribe":
                unsubscribe = header["value"]

        domain = extract_domain(from_header)

        if domain not in dict_senders:
            dict_senders[domain] = {
                "count": 0,
                "subjects": [],
                "unsubscribe_links": [],
                "message_ids": []
            }

        dict_senders[domain]["count"] += 1
        dict_senders[domain]["message_ids"].append(response["id"])

        if subject:
            dict_senders[domain]["subjects"].append(subject)

        if unsubscribe:
            dict_senders[domain]["unsubscribe_links"].append(unsubscribe)


    # Traiter les messages par batch de 10 pour éviter le rate limit
    batch_size = 10
    for i in range(0, len(all_messages), batch_size):
        batch = service.new_batch_http_request()
        batch_messages = all_messages[i:i + batch_size]
        
        for message in batch_messages:
            batch.add(
                service.users().messages().get(
                    userId="me",
                    id=message["id"],
                    format="metadata",
                    metadataHeaders=["Subject", "From", "List-Unsubscribe"]
                ),
                callback=callback
            )

        batch.execute()
        # Attendre un peu entre les batches pour respecter les limites de débit
        time.sleep(0.5)

    return dict_senders