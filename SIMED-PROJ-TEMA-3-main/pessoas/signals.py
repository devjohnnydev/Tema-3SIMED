# pessoas/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.socialaccount.signals import pre_social_login
from .models import Perfil

@receiver(post_save, sender=User)
def criar_perfil_usuario(sender, instance, created, **kwargs):
    """
    Cria automaticamente um perfil de paciente quando um novo usuário é criado.
    """
    if created:
        # Verifica se o usuário já tem um perfil (evita duplicação)
        if not hasattr(instance, 'perfil'):
            Perfil.objects.create(usuario=instance, tipo_usuario='paciente')

@receiver(pre_social_login)
def vincular_conta_social(sender, request, sociallogin, **kwargs):
    """
    Vincula conta social (Google) a usuário existente se o email já estiver cadastrado.
    """
    if sociallogin.is_existing:
        return
    
    try:
        email = sociallogin.account.extra_data.get('email', '').lower()
        if email:
            # Verifica se já existe um usuário com este email
            user = User.objects.get(email=email)
            # Conecta a conta social ao usuário existente
            sociallogin.connect(request, user)
    except User.DoesNotExist:
        pass
