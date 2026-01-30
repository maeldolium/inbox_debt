import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# SCOPES de l'application
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def auth():

    creds = None
    
    # Le fichier token.json stocke l'accès utilisateur et le refresh_token, 
    # il est créer automatiquement après la première authentification 
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    # Si il n'y a pas de token ou non valid, connexion utilisateur:
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Enregistrer les infos pour la prochaine utilisation
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    return creds

