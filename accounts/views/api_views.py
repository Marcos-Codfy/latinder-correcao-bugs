# Django Imports
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView
from django.http import JsonResponse
from django.views import View
from django.db import models
from django.db.models import Q
from django.shortcuts import get_object_or_404
import json

# App-specific Imports
from ..models import Pet, Owner, Swipe, Match, Message

# --- Views de API (Swipe, Match, Chat) ---

class SwipeView(LoginRequiredMixin, ListView):
    model = Pet
    template_name = 'swipe.html'
    context_object_name = 'pets_to_swipe' 
    
    def get_queryset(self):
        try:
            user_pet = self.request.user.owner.pet_set.first()
        except (Owner.DoesNotExist, AttributeError):
            return Pet.objects.none()
        
        if not user_pet:
            return Pet.objects.none()

        swiped_pet_ids = Swipe.objects.filter(swiper=user_pet).values_list('swiped_id', flat=True)
        queryset = Pet.objects.exclude(id=user_pet.id).exclude(id__in=swiped_pet_ids)
    
        return queryset
    
class ProcessSwipeView(LoginRequiredMixin, View):
    """View para processar swipes e detectar matches"""
    def post(self, request, *args, **kwargs):
        try:
            swiper_pet = request.user.owner.pet_set.first()
            if not swiper_pet:
                return JsonResponse({'status': 'error', 'message': 'User has no pet.'}, status=400)

            data = json.loads(request.body)
            swiped_pet_id = data.get('swiped_pet_id')
            liked = data.get('liked')

            swiped_pet = Pet.objects.get(id=swiped_pet_id)

            Swipe.objects.create(
                swiper=swiper_pet,
                swiped=swiped_pet,
                liked=liked
            )
            
            match_occurred = False
            if liked:
                reciprocal_like = Swipe.objects.filter(
                    swiper=swiped_pet,
                    swiped=swiper_pet,
                    liked=True
                ).exists()
                
                if reciprocal_like:
                    pet1, pet2 = sorted([swiper_pet.id, swiped_pet.id])
                    Match.objects.get_or_create(
                        pet1_id=pet1,
                        pet2_id=pet2
                    )
                    match_occurred = True
            
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
        context = super().get_context_data( **kwargs)
        
        try:
            user_pet = self.request.user.owner.pet_set.first()
        except (Owner.DoesNotExist, AttributeError):
            context['matches'] = []
            return context
        
        if not user_pet:
            context['matches'] = []
            return context
        
        matches = Match.objects.filter(
            models.Q(pet1=user_pet) | models.Q(pet2=user_pet)
        ).select_related('pet1', 'pet2', 'pet1__owner__user', 'pet2__owner__user')
        
        matched_pets = []
        for match in matches:
            other_pet = match.pet2 if match.pet1 == user_pet else match.pet1
            matched_pets.append({
                'match': match,
                'pet': other_pet,
                'match_date': match.created_at
            })
        
        context['matches'] = matched_pets
        return context
    
class ChatView(LoginRequiredMixin, DetailView):
    """Exibe a interface de chat para um match específico"""
    model = Match
    template_name = 'chat.html'
    context_object_name = 'match'
    
    def get_queryset(self):
        user_pet = self.request.user.owner.pet_set.first()
        return Match.objects.filter(
            Q(pet1=user_pet) | Q(pet2=user_pet)
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        match = self.get_object()
        
        user_pet = self.request.user.owner.pet_set.first()
        other_pet = match.pet2 if match.pet1 == user_pet else match.pet1
        context['other_pet'] = other_pet
        
        context['messages'] = match.messages.all()
        
        match.messages.exclude(
            sender=self.request.user.owner
        ).update(is_read=True)
        
        return context

class SendMessageView(LoginRequiredMixin, View):
    """Recebe e salva uma nova mensagem no banco de dados"""
    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            match_id = data.get('match_id')
            content = data.get('content', '').strip()
            
            if not content:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Mensagem vazia'
                }, status=400)
            
            match = get_object_or_404(Match, id=match_id)
            user_pet = request.user.owner.pet_set.first()
            
            if match.pet1 != user_pet and match.pet2 != user_pet:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Acesso negado'
                }, status=403)
            
            message = Message.objects.create(
                match=match,
                sender=request.user.owner,
                content=content
            )
            
            return JsonResponse({
                'status': 'success',
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'sender': message.sender.user.username,
                    
                    # ***** MUDANÇA 1/2 *****
                    # Trocado de .strftime('%H:%M') para .isoformat()
                    'timestamp': message.timestamp.isoformat(),
                    
                    'is_mine': True
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

class GetNewMessagesView(LoginRequiredMixin, View):
    """Retorna mensagens novas de um chat (para polling do frontend)"""
    
    def get(self, request, *args, **kwargs):
        try:
            match_id = request.GET.get('match_id')
            last_message_id = request.GET.get('last_message_id', 0)
            
            match = get_object_or_404(Match, id=match_id)
            user_pet = request.user.owner.pet_set.first()
            
            if match.pet1 != user_pet and match.pet2 != user_pet:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Acesso negado'
                }, status=403)
            
            new_messages = match.messages.filter(
                id__gt=last_message_id
            ).select_related('sender__user')
            
            new_messages.exclude(
                sender=request.user.owner
            ).update(is_read=True)
            
            messages_data = [{
                'id': msg.id,
                'content': msg.content,
                'sender': msg.sender.user.username,
                
                # ***** MUDANÇA 2/2 *****
                # Trocado de .strftime('%H:%M') para .isoformat()
                'timestamp': msg.timestamp.isoformat(),
                
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