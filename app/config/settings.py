import os

# Lire la variable d'environnement, par défault "local"
APP_MODE = os.getenv("APP_MODE", "local")

# Normaliser la valeur
APP_MODE = APP_MODE.lower()

# Validation de la variable
if APP_MODE not in ["local", "demo"]:
    APP_MODE = "local"

# Export de la configuration
__all__ = ["APP_MODE"]
