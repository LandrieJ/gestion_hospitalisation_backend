FROM python:3.11-slim

# Préparer un dossier de travail
WORKDIR /app

# Copier uniquement ce qui est utile
COPY back-end/ /app/

# Installer pip + dépendances
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Exposer le port utilisé par Django
EXPOSE 8000

# Commande d'entrée
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]