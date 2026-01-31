from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.utils import parseaddr

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

        # Rechercher l'email et le nom de domaine dans le header
        email, domain = extract_domain(from_value)

        # Remplir le dictionnaire et compter les occurrences
        if not domain in dict_senders:
            dict_senders[domain] = 1
        else:
            dict_senders[domain] += 1

    # Afficher les domaines et leur nombre d'occurrences
    print(f'{dict_senders}')
            
# Recherche du domaine
def extract_domain(from_value):
    
    email = parseaddr(from_value)[1]

    domain = email.split("@")[1]

    return (email, domain)

