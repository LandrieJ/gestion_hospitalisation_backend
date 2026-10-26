import os
import django
from django.contrib.auth import get_user_model

# Initialisation Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gestion_hospitalisation.settings")
django.setup()

User = get_user_model()

# Données du superuser
SUPERUSER_EMAIL = "admin@gmail.com"
SUPERUSER_PASSWORD = "root"
SUPERUSER_FIRST_NAME = "Super"
SUPERUSER_LAST_NAME = "Admin"

# Vérifie si le superuser existe
existing_user = User.objects.filter(email=SUPERUSER_EMAIL).first()

if existing_user:
    if not existing_user.is_active:
        print(f"🗑 Superuser inactif trouvé. Suppression de {SUPERUSER_EMAIL}...")
        existing_user.delete()

        print(f"🔄 Création du superuser avec {SUPERUSER_EMAIL}...")
        user = User.objects.create_superuser(
            email=SUPERUSER_EMAIL,
            password=SUPERUSER_PASSWORD,
            first_name=SUPERUSER_FIRST_NAME,
            last_name=SUPERUSER_LAST_NAME,
        )
        user.save()
        print(f"✅ Superuser {SUPERUSER_EMAIL} recréé avec succès.")
    else:
        print(f"ℹ Le superuser {SUPERUSER_EMAIL} est déjà actif. Aucune action effectuée.")
else:
    print(f"➕ Aucun superuser trouvé. Création de {SUPERUSER_EMAIL}...")
    user = User.objects.create_superuser(
        email=SUPERUSER_EMAIL,
        password=SUPERUSER_PASSWORD,
        first_name=SUPERUSER_FIRST_NAME,
        last_name=SUPERUSER_LAST_NAME,
    )
    user.save()
    print(f"✅ Superuser {SUPERUSER_EMAIL} créé avec succès.")
