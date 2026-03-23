# Image Python
FROM python:3.11-slim

# Empêcher python de buffer les logs
ENV PYTHONUNBUFFERED=1

# Ajouter le dossier de l'application
ENV PYTHONPATH=/app/app

# Dossier de travail
WORKDIR /app

# Copier les dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le projet
COPY . .

# Exposer le port
EXPOSE 8080

# Démarrage de Gunicorn
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:$PORT"]