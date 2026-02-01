from auth.oauth_flow import auth
from gmail_api.fetch_emails import get_gmail_service, list_unsubscribe_emails
import webbrowser

def main():
    credentials = auth()

    service = get_gmail_service(credentials)

    dict_senders = list_unsubscribe_emails(service)

    if not dict_senders:
        print("Aucun domaine à traiter")
        return

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
    
    
    
main()