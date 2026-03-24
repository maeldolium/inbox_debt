import os
from dotenv import load_dotenv

# Charger le fichier .env (développement local)
load_dotenv()


class Config:
    # Clé de chiffrement Flask
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

    # Lecture du mode depuis variable d'environnement
    APP_MODE = os.getenv("APP_MODE", "local").lower()

    # Validation du mode
    if APP_MODE not in ["local", "demo"]:
        APP_MODE = "local"

    # Environnement
    FLASK_ENV = os.getenv("FLASK_ENV", "development")

    # Debug
    DEBUG = FLASK_ENV == "development"

    # Session
    SESSION_COOKIE_SECURE = FLASK_ENV == "production"  # HTTPS only en prod
    SESSION_COOKIE_HTTPONLY = True  # Pas accessible au JavaScript
    SESSION_COOKIE_SAMESITE = "Lax"  # Protection CSRF


class DevelopmentConfig(Config):

    DEBUG = True
    FLASK_ENV = "development"
    SESSION_COOKIE_SECURE = False  # Accepte HTTP en dev


class ProductionConfig(Config):

    DEBUG = False
    FLASK_ENV = "production"
    SESSION_COOKIE_SECURE = True  # Force HTTPS

    @classmethod
    def validate(cls):
        if not cls.SECRET_KEY:
            raise ValueError(
                "CRITICAL: FLASK_SECRET_KEY not set in production! "
                "Set the environment variable and restart."
            )
        print("Production config validated")


class DemoConfig(Config):

    DEBUG = True
    APP_MODE = "demo"


# Sélection de la configuration selon l'environnement
def get_config():
    
    env = os.getenv("FLASK_ENV", "development").lower()

    if env == "production":
        # Valider avant de retourner
        ProductionConfig.validate()
        return ProductionConfig
    elif env == "staging":
        return ProductionConfig  # Même config que prod
    else:
        # Développement par défaut
        return DevelopmentConfig


# Validation à l'import
def validate_config():
    config = get_config()

    # Vérifier la secret_key en dev
    if not config.SECRET_KEY:
        if config.FLASK_ENV == "production":
            raise ValueError(
                "FLASK_SECRET_KEY must be set in production environment!"
            )
        else:
            print(
                "WARNING: FLASK_SECRET_KEY not set. "
                "Using temporary key (DEV ONLY - not secure!)"
            )
            config.SECRET_KEY = "dev-temporary-unsafe-key"

    return config


__all__ = ["Config", "DevelopmentConfig", "ProductionConfig", "DemoConfig", "get_config", "validate_config"]
