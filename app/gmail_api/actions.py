from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def trash_message(service, message_id):
    service.users().messages().trash(
        userId="me",
        id=message_id
    ).execute()