# Django Imports
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

# App-specific Imports
from ..models import Owner # Usamos ..models para "subir um nível" de pasta

# --- Views de Autenticação e Home ---

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        Owner.objects.create(user=self.object)
        return response

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        # Verifica se o dono já preencheu a data de nascimento
        if not request.user.owner.birth_date:
            # Redireciona direto para a página de edição do perfil
            return redirect('owner_edit')
        
        # Se já preencheu, continua e mostra a home.html
        return super().get(self, request, *args, **kwargs)