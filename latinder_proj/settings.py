# Esses são as configurações principais do projeto Latinder.
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-+*!cr_wcpbc_&bpy#v26r*0+q)4+a**n)lprq%uz_!r1=d1*15'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Definiçãos do aplicativos instalados
# Inclui o app "accounts" e pacotes para formulários bonitos
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'crispy_forms',
    'crispy_bootstrap5',
]

# Middleware padrão do Django
# O que é middleware? São "camadas" que processam requisições e respostas.
# Elas podem adicionar funcionalidades como segurança, sessões, etc.
# Cada middleware é executado em ordem.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'latinder_proj.urls'

# Configuração dos templates HTML
# Define onde o Django deve procurar pelos arquivos de template
# Inclui diretórios globais e dos apps instalados
# Configurações detalhadas dos templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'latinder_proj.wsgi.application'


#Banco de dados
# Usando SQLite para desenvolvimento local
# Em produção, considerar usar PostgreSQL ou outro banco robusto
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Validação de senhas
# Define regras para senhas seguras
# Inclui validadores padrão do Django
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Configurações internacionais
# Define idioma e fuso horário
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Configurações de arquivos estáticos (CSS, JavaScript, Imagens)
# Define onde os arquivos estáticos são armazenados e servidos
STATIC_URL = 'static/'

# Configuração padrão para o campo auto incrementado do Django
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configurações do Crispy Forms
# O que é Crispy Forms? É uma biblioteca que facilita a criação de formulários bonitos e responsivos.
# Aqui estamos configurando para usar o template pack do Bootstrap 5
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


# Para onde ir após o login
LOGIN_REDIRECT_URL = 'home'

# Para onde ir após o logout
LOGOUT_REDIRECT_URL = 'login'

# URL para onde o Django redireciona usuários não autenticados
LOGIN_URL = '/login/'

# Configuração para arquivos de mídia (uploads dos usuários)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
