from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.utils import parseaddr
import webbrowser

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
        q="has:unsubscribe",
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

 
    # Afficher les domaines et leur nombre d'occurrences
    print(f"{'Domain':<30} {'Count':<8} {'Subjects':<10} {'Links':<10}")
    print("-" * 60)
    for domain, data in dict_senders.items():
        print(f"{domain:<30} {data['count']:<8} {len(data['subjects']):<10} {len(data['unsubscribe_links']):<10}")
    
    # Tester l'ouverture de lien http
    for domain in dict_senders:
        domain_test = dict_senders[domain]

        for link in domain_test["unsubscribe_links"]:
            if link:
                webbrowser.open_new_tab(link)
                return
            
# Recherche du domaine
def extract_domain(from_value):
    
    email = parseaddr(from_value)[1]

    domain = email.split("@")[1]

    return (email, domain)

# Extraire les liens http de désinscription
def extract_http_unsubscribe(unsubscribe_header):
    
    unsubscribe_header = unsubscribe_header.split(',')

    for i in range(len(unsubscribe_header)):
        unsubscribe_header[i] = unsubscribe_header[i].strip().lstrip('<').rstrip('>')

        if unsubscribe_header[i].find("http") != -1:
            return unsubscribe_header[i]

    return None

