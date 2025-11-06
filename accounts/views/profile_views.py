# Django Imports
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.http import HttpResponseRedirect

# App-specific Imports
from ..forms import PetForm, PetPhotoForm, OwnerProfileForm
from ..models import Pet, Owner, PetPhoto

# --- Views de Perfil (CRUD) ---

class PetCreateView(LoginRequiredMixin, CreateView):
    model = Pet
    form_class = PetForm
    template_name = 'pet_form.html'
    
    def form_valid(self, form):
        form.instance.owner = self.request.user.owner
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('pet_detail', kwargs={'pk': self.object.pk})

class PetDetailView(DetailView):
    model = Pet
    template_name = 'pet_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        is_mine = False
        if self.request.user.is_authenticated:
            is_mine = (self.object.owner == self.request.user.owner)
        
        context['is_mine'] = is_mine
        
        if is_mine:
            context['photo_form'] = PetPhotoForm()
        
        context['pet_owner'] = self.object.owner
        
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object() 
        
        if self.object.owner != self.request.user.owner:
            return HttpResponseRedirect(self.request.path_info) 
            
        form = PetPhotoForm(request.POST, request.FILES)
        
        photo_count_before_save = self.object.petphoto_set.count()
            
        if form.is_valid():
            photo = form.save(commit=False)
            photo.pet = self.object
            photo.save()

            if photo_count_before_save == 0:
                return HttpResponseRedirect(reverse_lazy('swipe'))
            else:
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

    # ****** ESTA É A CORREÇÃO (2/2) ******
    # Esta função agora é "inteligente"
    def get_success_url(self):
        # self.object é o 'Owner' que acabamos de salvar.
        # Verificamos se ele já tem algum pet cadastrado.
        if self.object.pet_set.all().exists():
            # Se JÁ TEM pet, volte para a página de perfil do dono.
            return reverse_lazy('owner_detail', kwargs={'pk': self.object.pk})
        else:
            # Se NÃO TEM pet (onboarding), continue para a página 'pet_add'.
            return reverse_lazy('pet_add')

    # Garante que o usuário só possa editar seu próprio perfil
    def get_object(self, queryset=None):
        return self.request.user.owner
    
class PetUpdateView(LoginRequiredMixin, UpdateView):
    model = Pet
    form_class = PetForm 
    template_name = 'pet_form.html' 
    
    def get_success_url(self):
        return reverse_lazy('pet_detail', kwargs={'pk': self.object.pk})
    
    def get_queryset(self):
        return Pet.objects.filter(owner=self.request.user.owner)