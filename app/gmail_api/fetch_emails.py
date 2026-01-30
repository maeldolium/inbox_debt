from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

def get_gmail_service(credentials):
    # Créer le service pour la récupération de mails
    
    service = build("gmail", "v1", credentials=credentials)

    return service


def list_unsubscribe_emails(service):
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

        # Afficher les résultats
        print(f'{from_value}')
        print(f'{subject_value}')
        print(f'{unsubscribe_value}')
        print("-------------")