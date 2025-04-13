import os
from pathlib import Path
from dotenv import load_dotenv
import ast


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

#ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
# Remplacer la ligne existante par :

# Remplacez la ligne ALLOWED_HOSTS par :
#ALLOWED_HOSTS = [host.strip() for host in os.environ.get('ALLOWED_HOSTS', '').split(',') if host]

#print("[DEBUG] RAW ALLOWED_HOSTS ENV:", repr(os.environ.get('ALLOWED_HOSTS')))
#print("[DEBUG] PROCESSED ALLOWED_HOSTS:", ALLOWED_HOSTS)



# Solution robuste avec ast.literal_eval pour gérer tous les cas

def get_allowed_hosts():
    try:
        # Essayer d'abord avec le nouveau format
        hosts = os.environ.get('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
        return [h.strip() for h in hosts if h.strip()]
    except:
        return ['127.0.0.1', 'localhost']

ALLOWED_HOSTS = get_allowed_hosts()

print("[FINAL CHECK] ALLOWED_HOSTS:", ALLOWED_HOSTS)




#print("[DEBUG] ALLOWED_HOSTS:", ALLOWED_HOSTS)  # Doit afficher ['127.0.0.1', 'localhost', '0.0.0.0']
INSTALLED_APPS = [
    # Applications de base Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',    
    # Applications tierces
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
    'django_extensions',
    'api.apps.ApiConfig',  # Ton application API principale
    #'dotenv',
    'nltk',
    'textblob',]


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Ajouter CORS middleware avant CommonMiddleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

# Configuration de la base de données
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}

# Configuration de REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Configuration CORS pour permettre les requêtes du frontend Angular
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",  # URL de développement Angular
]
ROOT_URLCONF = 'core.urls'  # Remplace 'core' par le nom de ton projet si nécessaire

# Configuration utilisateur personnalisé
AUTH_USER_MODEL = 'api.Utilisateur'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # Dossier où seront stockés les fichiers HTML
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
