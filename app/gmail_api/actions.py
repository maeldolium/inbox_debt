from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def trash_message(service, message_ids_list):
    for i in range(len(message_ids_list)):
        service.users().messages().trash(
        userId="me",
        id=message_ids_list[i]
        ).execute()
        print(f'Message supprimé : {message_ids_list[i]}')

def delete_emails(service, message_ids_list):
    if not message_ids_list:
        return
    
    service.users().messages().batchModify(
        userId="me",
        body={
            "ids": message_ids_list,
            "addLabelIds": ["TRASH"]
        }
    ).execute()

    print(f"Mails supprimés avec succès !")