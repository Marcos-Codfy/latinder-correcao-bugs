#Esse arquivo contém as views do aplicativo de contas (accounts) do projeto Latinder.
# As views são responsáveis por processar as requisições HTTP, interagir com os modelos (models) 
# e retornar respostas HTTP, geralmente renderizando templates HTML.
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.base import TemplateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.http import HttpResponseRedirect
import json
from django.http import JsonResponse
from django.views import View
#-------------------------------- Sprint 2 ----------------------------------#
from django.views.generic import ListView
from .models import Pet, Owner, PetPhoto, Swipe 
#-------------------------------------------------------------------------#
# Importações dos nossos Forms e Models
from .forms import PetForm, PetPhotoForm, OwnerProfileForm
from .models import Pet, Owner, PetPhoto
from .models import Pet, Owner, PetPhoto, Swipe, Match
from django.db import models
#-------------------------------- Sprint 4 ----------------------------------#
from django.shortcuts import get_object_or_404
from .models import Pet, Owner, PetPhoto, Swipe, Match, Message
from django.db.models import Q
#-------------------------------------------------------------------------#
# --- Nossas Views ---
# View para cadastro de novos usuários
class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
    # função para criar o Owner automaticamente após o cadastro do User
    # essa função sobrescreve o método form_valid da classe CreateView
    # para adicionar a lógica de criação do Owner
    # Após o User ser criado com sucesso, um Owner associado é criado
    # para o novo usuário.
    # Isso garante que cada usuário tenha um perfil de Owner.
    def form_valid(self, form):
        response = super().form_valid(form)
        Owner.objects.create(user=self.object)
        return response

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

class PetCreateView(LoginRequiredMixin, CreateView):
    model = Pet
    form_class = PetForm
    template_name = 'pet_form.html'
    # Ao salvar o formulário, associa o pet ao dono (owner) logado
    def form_valid(self, form):
        form.instance.owner = self.request.user.owner
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('pet_detail', kwargs={'pk': self.object.pk})
    
class PetDetailView(DetailView):
    model = Pet
    template_name = 'pet_detail.html'
    # Adiciona o formulário de upload de fotos ao contexto
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photo_form'] = PetPhotoForm()
        return context
    # Processa o upload de fotos via POST
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = PetPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.pet = self.object
            photo.save()
            return HttpResponseRedirect(self.request.path_info)
        else:
            context = self.get_context_data()
            context['photo_form'] = form
            return self.render_to_response(context)

class OwnerDetailView(LoginRequiredMixin, DetailView):
    model = Owner
    template_name = 'owner_detail.html'

class OwnerUpdateView(LoginRequiredMixin, UpdateView):
    model = Owner
    form_class = OwnerProfileForm
    template_name = 'owner_form.html'
    # Após salvar, redireciona para a página de detalhes do Owner
    def get_success_url(self):
        return reverse_lazy('owner_detail', kwargs={'pk': self.object.pk})
    # Garante que o usuário só possa editar seu próprio perfil
    def get_object(self, queryset=None):
        return self.request.user.owner
    
 # View para editar um Pet existente   
class PetUpdateView(LoginRequiredMixin, UpdateView):
    model = Pet
    form_class = PetForm # Podemos reutilizar o mesmo PetForm que criamos!
    template_name = 'pet_form.html' # E também o mesmo template!
    # Após salvar, redireciona para a página de detalhes do Pet
    def get_success_url(self):
        # Após editar, volta para a página de detalhes do pet
        return reverse_lazy('pet_detail', kwargs={'pk': self.object.pk})
    # Garante que o usuário só possa editar seus próprios pets
    def get_queryset(self):
        # Esta é a checagem de segurança!
        # A view só poderá encontrar e editar pets que pertencem ao usuário logado.
        return Pet.objects.filter(owner=self.request.user.owner)

# Adicionado a view de Swipe
class SwipeView(LoginRequiredMixin, ListView):
    model = Pet
    template_name = 'swipe.html'
    context_object_name = 'pets_to_swipe' # Nome da lista no template
    # Filtra os pets para mostrar apenas os que ainda não foram avaliados
    def get_queryset(self):
        # Pega o pet do usuário logado
        try:
            user_pet = self.request.user.owner.pet_set.first()
        except (Owner.DoesNotExist, AttributeError):
            return Pet.objects.none()
        # Se o usuário não tem pet, não pode ver outros.
        if not user_pet:
            return Pet.objects.none()

        # Pega a lista de IDs de pets que o usuário já avaliou (swiped)
        swiped_pet_ids = Swipe.objects.filter(swiper=user_pet).values_list('swiped_id', flat=True)
        # Busca todos os pets, excluindo:
        # 1. O próprio pet do usuário.
        # 2. Os pets que já foram avaliados.
        queryset = Pet.objects.exclude(id=user_pet.id).exclude(id__in=swiped_pet_ids)
    
        return queryset
    

# View para processar os swipes via AJAX
# Essa view recebe os dados do swipe (like/pass) e salva no banco de dados
# Ela responde com um JSON indicando sucesso ou falha
# Essa view é chamada pelo JavaScript na página de swipe
class ProcessSwipeView(LoginRequiredMixin, View):
    """View para processar swipes e detectar matches"""
    def post(self, request, *args, **kwargs):
        try:
            # Pega o pet do usuário logado
            swiper_pet = request.user.owner.pet_set.first()
            if not swiper_pet:
                return JsonResponse({'status': 'error', 'message': 'User has no pet.'}, status=400)

            # Carrega os dados enviados pelo JavaScript
            data = json.loads(request.body)
            swiped_pet_id = data.get('swiped_pet_id')
            liked = data.get('liked')

            # Encontra o pet que foi avaliado
            swiped_pet = Pet.objects.get(id=swiped_pet_id)

            # Cria e salva o objeto Swipe no banco de dados
            Swipe.objects.create(
                swiper=swiper_pet,
                swiped=swiped_pet,
                liked=liked
            )
            
            # Verifica se houve match (apenas se foi um like)
            match_occurred = False
            if liked:
                # Verifica se o outro pet também deu like
                reciprocal_like = Swipe.objects.filter(
                    swiper=swiped_pet,
                    swiped=swiper_pet,
                    liked=True
                ).exists()
                
                if reciprocal_like:
                    # Cria o match (garante ordem consistente dos IDs para evitar duplicatas)
                    pet1, pet2 = sorted([swiper_pet.id, swiped_pet.id])
                    Match.objects.get_or_create(
                        pet1_id=pet1,
                        pet2_id=pet2
                    )
                    match_occurred = True
            
            # Responde ao JavaScript com informação sobre o match
            return JsonResponse({
                'status': 'success',
                'match': match_occurred
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

class MatchesView(LoginRequiredMixin, TemplateView):
    """View para exibir a lista de matches do usuário"""
    template_name = 'matches.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Pega o pet do usuário logado
        try:
            user_pet = self.request.user.owner.pet_set.first()
        except (Owner.DoesNotExist, AttributeError):
            context['matches'] = []
            return context
        
        if not user_pet:
            context['matches'] = []
            return context
        
        # Busca todos os matches do pet do usuário
        matches = Match.objects.filter(
            models.Q(pet1=user_pet) | models.Q(pet2=user_pet)
        ).select_related('pet1', 'pet2', 'pet1__owner__user', 'pet2__owner__user')
        
        # Cria lista com informações dos pets combinados
        matched_pets = []
        for match in matches:
            # Pega o outro pet do match
            other_pet = match.pet2 if match.pet1 == user_pet else match.pet1
            matched_pets.append({
                'match': match,  # ADICIONADO: objeto match completo
                'pet': other_pet,
                'match_date': match.created_at
            })
        
        context['matches'] = matched_pets
        return context
    
 #View para exibir a página de chat de um match específico
class ChatView(LoginRequiredMixin, DetailView):
    """Exibe a interface de chat para um match específico"""
    model = Match
    template_name = 'chat.html'
    context_object_name = 'match'
    
    def get_queryset(self):
        # Garante que o usuário só acesse chats dos seus próprios matches
        user_pet = self.request.user.owner.pet_set.first()
        return Match.objects.filter(
            Q(pet1=user_pet) | Q(pet2=user_pet)
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        match = self.get_object()
        
        # Identifica qual é o outro pet no match
        user_pet = self.request.user.owner.pet_set.first()
        other_pet = match.pet2 if match.pet1 == user_pet else match.pet1
        context['other_pet'] = other_pet
        
        # Carrega o histórico de mensagens do match
        context['messages'] = match.messages.all()
        
        # Marca mensagens recebidas como lidas
        match.messages.exclude(
            sender=self.request.user.owner
        ).update(is_read=True)
        
        return context


# View para enviar uma nova mensagem via AJAX
class SendMessageView(LoginRequiredMixin, View):
    """Recebe e salva uma nova mensagem no banco de dados"""
    
    def post(self, request, *args, **kwargs):
        try:
            # Pega os dados enviados pelo JavaScript
            data = json.loads(request.body)
            match_id = data.get('match_id')
            content = data.get('content', '').strip()
            
            # Validação básica
            if not content:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Mensagem vazia'
                }, status=400)
            
            # Busca o match e valida permissões
            match = get_object_or_404(Match, id=match_id)
            user_pet = request.user.owner.pet_set.first()
            
            # Verifica se o usuário faz parte deste match
            if match.pet1 != user_pet and match.pet2 != user_pet:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Acesso negado'
                }, status=403)
            
            # Cria a mensagem
            message = Message.objects.create(
                match=match,
                sender=request.user.owner,
                content=content
            )
            
            # Retorna os dados da mensagem criada
            return JsonResponse({
                'status': 'success',
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'sender': message.sender.user.username,
                    'timestamp': message.timestamp.strftime('%H:%M'),
                    'is_mine': True
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)


# View (API endpoint) para buscar novas mensagens via polling
class GetNewMessagesView(LoginRequiredMixin, View):
    """Retorna mensagens novas de um chat (para polling do frontend)"""
    
    def get(self, request, *args, **kwargs):
        try:
            match_id = request.GET.get('match_id')
            last_message_id = request.GET.get('last_message_id', 0)
            
            # Busca o match
            match = get_object_or_404(Match, id=match_id)
            user_pet = request.user.owner.pet_set.first()
            
            # Verifica permissões
            if match.pet1 != user_pet and match.pet2 != user_pet:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Acesso negado'
                }, status=403)
            
            # Busca mensagens novas (ID maior que o último conhecido)
            new_messages = match.messages.filter(
                id__gt=last_message_id
            ).select_related('sender__user')
            
            # Marca mensagens recebidas como lidas
            new_messages.exclude(
                sender=request.user.owner
            ).update(is_read=True)
            
            # Formata as mensagens para JSON
            messages_data = [{
                'id': msg.id,
                'content': msg.content,
                'sender': msg.sender.user.username,
                'timestamp': msg.timestamp.strftime('%H:%M'),
                'is_mine': msg.sender == request.user.owner
            } for msg in new_messages]
            
            return JsonResponse({
                'status': 'success',
                'messages': messages_data
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)