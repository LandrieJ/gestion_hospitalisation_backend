from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Charger .env.docker si présent
if os.path.exists(BASE_DIR / ".env.docker"):
    load_dotenv(BASE_DIR / ".env.docker")
else:
    load_dotenv(BASE_DIR / ".env")

# Sécurité
SECRET_KEY = os.getenv("SECRET_KEY", "changeme-in-production")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")

# --- APPLICATIONS ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    # Third party apps
    "corsheaders",
    "rest_framework",
    "django_filters",
    
    # Mes applications
    "hospital",
    "service",
    "traumatologie",
    "comptes",
    "statistique",
    "patient",
    "logistique",
    "evenement",
]

# --- MIDDLEWARES ---
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "comptes.middleware.AddPartitionedAttributeMiddleware",
]

# --- TEMPLATES ---
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

# --- URL / WSGI ---
ROOT_URLCONF = "gestion_hospitalisation.urls"
WSGI_APPLICATION = "gestion_hospitalisation.wsgi.application"

# --- BASE DE DONNÉES ---
# --- BASE DE DONNÉES ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DATABASE_NAME", "mydb"),
        "USER": os.getenv("DATABASE_USER", "myuser"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD", "mypassword"),
        "HOST": os.getenv("DATABASE_HOST", "db"),           # fallback to 'db'
        "PORT": os.getenv("DATABASE_PORT", "5432"),
    }
}

# --- UTILISATEUR PERSONNALISÉ ---
AUTH_USER_MODEL = "comptes.CustomUser"
AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

# --- SESSIONS ET CSRF ---
SESSION_ENGINE = ("django.contrib.sessions.backends.db")
SESSION_COOKIE_NAME = "sessionid"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "")
SESSION_EXPIRE_AT_BROWSER_CLOSE = (True)

CSRF_USE_SESSIONS = True # Utiliser la session pour stocker le token CSRF
CSRF_COOKIE_NAME = "csrftoken"
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "")
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = "None"

# --- CORS ---
#CORS_ALLOW_CREDENTIALS = True
#CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
#CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")


# --- CORS ---
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]


CORS_ALLOW_HEADERS = [
    "accept",
    "x-requested-with",
    "x-csrftoken",
    "content-type",
    "authorization",
    "cookie",
]

# --- DJANGO REST FRAMEWORK ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication"
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated"
    ],
    # ✅ AJOUTÉ - Configuration des filtres
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    # ✅ AJOUTÉ - Renderers pour l'interface browsable
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    # ✅ AJOUTÉ - Pagination optionnelle
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20
}

# --- VALIDATEURS DE MOTS DE PASSE ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- INTERNATIONALISATION ---
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- EMAIL ---
EMAIL_BACKEND = os.getenv("MAIL_EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.getenv("MAIL_EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("MAIL_EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("MAIL_EMAIL_USE_TLS", "True").lower() in ["true", "1"]
EMAIL_HOST_USER = os.getenv("MAIL_EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("MAIL_EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("MAIL_DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

# --- FICHIERS STATIQUES & MÉDIAS ---
STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --- DÉFAUT PK ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"






















# from pathlib import Path
# import os
# from dotenv import load_dotenv

# # --- BASE CONFIGURATION ---
# BASE_DIR = Path(__file__).resolve().parent.parent

# # Chargement des variables d'environnement
# USE_DOCKER = os.getenv("USE_DOCKER")

# if USE_DOCKER == "yes":
#     load_dotenv(dotenv_path=BASE_DIR / ".env.docker")
# else:
#     load_dotenv(dotenv_path=BASE_DIR / ".env")

# # Sécurité
# SECRET_KEY = os.getenv("SECRET_KEY", "changeme-in-production")
# DEBUG = os.getenv("DEBUG", "False").lower() == "true"
# ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")

# # --- APPLICATIONS ---
# INSTALLED_APPS = [
#     "django.contrib.admin",
#     "django.contrib.auth",
#     "django.contrib.contenttypes",
#     "django.contrib.sessions",
#     "django.contrib.messages",
#     "django.contrib.staticfiles",
#     "corsheaders",
#     "rest_framework",
#     "traumatologie",
#     "comptes",
#     "statistique",
#     "patient",
#     "logistique",
# ]

# # --- MIDDLEWARES ---
# MIDDLEWARE = [
#     "corsheaders.middleware.CorsMiddleware",
#     "django.middleware.security.SecurityMiddleware",
#     "django.contrib.sessions.middleware.SessionMiddleware",
#     "django.middleware.common.CommonMiddleware",
#     "django.middleware.csrf.CsrfViewMiddleware",
#     "django.contrib.auth.middleware.AuthenticationMiddleware",
#     "django.contrib.messages.middleware.MessageMiddleware",
#     "django.middleware.clickjacking.XFrameOptionsMiddleware",
#     "comptes.middleware.AddPartitionedAttributeMiddleware",
# ]

# # --- TEMPLATES ---
# TEMPLATES = [
#     {
#         "BACKEND": "django.template.backends.django.DjangoTemplates",
#         "DIRS": [BASE_DIR / "templates"],
#         "APP_DIRS": True,
#         "OPTIONS": {
#             "context_processors": [
#                 "django.template.context_processors.debug",
#                 "django.template.context_processors.request",
#                 "django.contrib.auth.context_processors.auth",
#                 "django.contrib.messages.context_processors.messages",
#             ],
#         },
#     }
# ]

# # --- URL / WSGI ---
# ROOT_URLCONF = "gestion_hospitalisation.urls"
# WSGI_APPLICATION = "gestion_hospitalisation.wsgi.application"

# # --- BASE DE DONNÉES ---
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": os.getenv("DATABASE_NAME"),
#         "USER": os.getenv("DATABASE_USER"),
#         "PASSWORD": os.getenv("DATABASE_PASSWORD"),
#         "HOST": os.getenv("DATABASE_HOST"),
#         "PORT": os.getenv("DATABASE_PORT"),
#     }
# }

# # --- UTILISATEUR PERSONNALISÉ ---
# AUTH_USER_MODEL = "comptes.CustomUser"
# AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

# # --- SESSIONS ET CSRF ---
# SESSION_ENGINE = ("django.contrib.sessions.backends.db")
# SESSION_COOKIE_NAME = "sessionid"
# SESSION_COOKIE_HTTPONLY = True
# SESSION_COOKIE_SAMESITE = "None"
# SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "")
# SESSION_EXPIRE_AT_BROWSER_CLOSE = (True)

# CSRF_USE_SESSIONS = True # Utiliser la session pour stocker le token CSRF
# CSRF_COOKIE_NAME = "csrftoken"
# CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "")
# CSRF_COOKIE_HTTPONLY = False
# CSRF_COOKIE_SAMESITE = "None"

# # --- CORS ---
# CORS_ALLOW_CREDENTIALS = True
# CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
# CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")

# CORS_ALLOW_HEADERS = [
#     "accept",
#     "x-requested-with",
#     "x-csrftoken",
#     "content-type",
#     "authorization",
#     "cookie",
# ]

# # --- DJANGO REST FRAMEWORK ---
# REST_FRAMEWORK = {
#     "DEFAULT_AUTHENTICATION_CLASSES": [
#         "rest_framework.authentication.SessionAuthentication"
#     ],
#     "DEFAULT_PERMISSION_CLASSES": [
#         "rest_framework.permissions.IsAuthenticated"
#     ],
# }

# # --- VALIDATEURS DE MOTS DE PASSE ---
# AUTH_PASSWORD_VALIDATORS = [
#     {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
#     {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
#     {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
#     {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
# ]

# # --- INTERNATIONALISATION ---
# LANGUAGE_CODE = "en-us"
# TIME_ZONE = "UTC"
# USE_I18N = True
# USE_TZ = True

# # --- EMAIL ---
# EMAIL_BACKEND = os.getenv("MAIL_EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
# EMAIL_HOST = os.getenv("MAIL_EMAIL_HOST", "smtp.gmail.com")
# EMAIL_PORT = int(os.getenv("MAIL_EMAIL_PORT", 587))
# EMAIL_USE_TLS = os.getenv("MAIL_EMAIL_USE_TLS", "True").lower() in ["true", "1"]
# EMAIL_HOST_USER = os.getenv("MAIL_EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = os.getenv("MAIL_EMAIL_HOST_PASSWORD")
# DEFAULT_FROM_EMAIL = os.getenv("MAIL_DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

# # --- FICHIERS STATIQUES & MÉDIAS ---
# STATIC_URL = "static/"
# MEDIA_URL = "/media/"
# MEDIA_ROOT = BASE_DIR / "media"

# # --- DÉFAUT PK ---
# DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"