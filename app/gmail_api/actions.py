from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def trash_message(service, message_ids_list):
    for i in range(len(message_ids_list)):
        service.users().messages().trash(
        userId="me",
        id=message_ids_list[i]
        ).execute()
        print(f'Message supprimé : {message_ids_list[i]}')