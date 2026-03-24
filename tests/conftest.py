import os
import sys

# Forcer APP_MODE en mode démo AVANT tout import d'app
os.environ['APP_MODE'] = 'demo'
os.environ['FLASK_ENV'] = 'testing'

# Ajouter le répertoire app au chemin
app_path = os.path.join(os.path.dirname(__file__), '..', 'app')
if app_path not in sys.path:
    sys.path.insert(0, app_path)
