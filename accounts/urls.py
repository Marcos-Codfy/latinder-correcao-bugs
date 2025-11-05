# ESSE ARQUIVO É RESPONSÁVEL POR GERENCIAR AS ROTAS (URLS) DO APLICATIVO ACCOUNTS
from django.urls import path
from django.contrib.auth import views as auth_views
# Importação das nossas Views
from .views import (
    SignUpView, HomeView, PetCreateView, PetDetailView, OwnerDetailView,
    OwnerUpdateView, PetUpdateView, SwipeView, ProcessSwipeView, MatchesView,
    ChatView, SendMessageView, GetNewMessagesView
)

# Definição das rotas URL para o app de contas
# Cada rota mapeia uma URL para uma View específica
# Exemplo: 'login/' mapeia para a view de login padrão do Django
# As rotas incluem autenticação, criação e detalhes de pets, perfil do dono, e funcionalidades de swipe
# Note que algumas rotas usam conversores de URL, como <int:pk>, para capturar parâmetros dinâmicos
# As views associadas são responsáveis por renderizar templates e processar formulários conforme necessário
# As rotas são nomeadas para facilitar a referência em templates e redirecionamentos
# Exemplo de uso: {% url 'pet_detail' pk=pet.id %} em um template para linkar para a página de detalhes de um pet específico
# As views personalizadas como SignUpView, HomeView, PetCreateView, etc., são definidas em accounts/views.py
urlpatterns = [
    # Rotas de Autenticação
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('', HomeView.as_view(), name='home'),
    path('pet/add/', PetCreateView.as_view(), name='pet_add'),
    # Rota dinâmica para detalhes do Pet
    # O <int:pk> é um conversor que captura um número inteiro da URL
    # e o passa para a view como uma variável chamada 'pk' (Primary Key).
    path('pet/<int:pk>/', PetDetailView.as_view(), name='pet_detail'),
        # Rota dinâmica para detalhes do Owner
        # O <int:pk> captura o ID do Owner para exibir seu perfil
    path('profile/<int:pk>/', OwnerDetailView.as_view(), name='owner_detail'),
    path('profile/edit/', OwnerUpdateView.as_view(), name='owner_edit'),
    path('pet/<int:pk>/edit/', PetUpdateView.as_view(), name='pet_edit'),
    path('swipe/', SwipeView.as_view(), name='swipe'),
    path('api/swipe/', ProcessSwipeView.as_view(), name='process_swipe'),
    path('matches/', MatchesView.as_view(), name='matches'),
    path('chat/<int:pk>/', ChatView.as_view(), name='chat'),
    path('api/send-message/', SendMessageView.as_view(), name='send_message'),
    path('api/get-messages/', GetNewMessagesView.as_view(), name='get_messages'),
]