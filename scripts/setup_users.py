#!/usr/bin/env python
"""
Script para criar usuarios padrao do SIMED
Execute com: python scripts/setup_users.py

Para Railway:
  railway run python scripts/setup_users.py

Ou via Django shell no Railway:
  railway run python manage.py shell < scripts/setup_users.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cadastro_pessoas.settings')

import django
django.setup()

from django.contrib.auth.models import User
from pessoas.models import Perfil, Especialidade, Profissional


def create_or_update_user(username, email, password, first_name, last_name, tipo_usuario, is_superuser=False):
    """Cria ou atualiza um usuario"""
    
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        user.email = email
        user.set_password(password)
        user.first_name = first_name
        user.last_name = last_name
        user.is_staff = is_superuser
        user.is_superuser = is_superuser
        user.save()
        print(f'Usuario "{username}" atualizado.')
    else:
        if is_superuser:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
        print(f'Usuario "{username}" criado.')
    
    if hasattr(user, 'perfil'):
        user.perfil.tipo_usuario = tipo_usuario
        user.perfil.save()
    else:
        Perfil.objects.create(usuario=user, tipo_usuario=tipo_usuario)
    
    print(f'Perfil de "{username}" configurado como {tipo_usuario}')
    return user


def setup_users():
    """Configura todos os usuarios padrao"""
    
    print('\n' + '='*60)
    print('CONFIGURANDO USUARIOS DO SIMED')
    print('='*60 + '\n')
    
    print('Aplicando migracoes pendentes...')
    from django.core.management import call_command
    call_command('migrate', verbosity=0)
    print('Migracoes aplicadas!\n')
    
    admin_user = create_or_update_user(
        username='admin',
        email='admin@simed.com',
        password='admin123',
        first_name='Administrador',
        last_name='SIMED',
        tipo_usuario='admin',
        is_superuser=True
    )
    
    print()
    
    medico_user = create_or_update_user(
        username='medico',
        email='medico@simed.com',
        password='medico123',
        first_name='Dr. Carlos',
        last_name='Silva',
        tipo_usuario='medico',
        is_superuser=False
    )
    
    especialidade, _ = Especialidade.objects.get_or_create(
        nome='Clinica Geral',
        defaults={'descricao': 'Medicina Geral e Familiar', 'icone': 'fa-user-md'}
    )
    
    profissional, created = Profissional.objects.get_or_create(
        usuario=medico_user,
        defaults={
            'nome': 'Dr. Carlos Silva',
            'especialidade': especialidade,
            'crm': 'CRM 12345/SP',
            'ativo': True,
            'destaque': True
        }
    )
    if not created:
        profissional.nome = 'Dr. Carlos Silva'
        profissional.especialidade = especialidade
        profissional.crm = 'CRM 12345/SP'
        profissional.ativo = True
        profissional.save()
    print(f'Profissional "{profissional.nome}" configurado.')
    
    print()
    
    recepcionista_user = create_or_update_user(
        username='recepcionista',
        email='recepcionista@simed.com',
        password='recepcionista123',
        first_name='Maria',
        last_name='Santos',
        tipo_usuario='atendente',
        is_superuser=False
    )
    
    print('\n' + '='*60)
    print('CREDENCIAIS CONFIGURADAS:')
    print('='*60)
    print()
    print('ADMINISTRADOR:')
    print('  Usuario: admin')
    print('  Senha: admin123')
    print('  Email: admin@simed.com')
    print()
    print('MEDICO:')
    print('  Usuario: medico')
    print('  Senha: medico123')
    print('  Email: medico@simed.com')
    print()
    print('RECEPCIONISTA:')
    print('  Usuario: recepcionista')
    print('  Senha: recepcionista123')
    print('  Email: recepcionista@simed.com')
    print()
    print('='*60)
    print('Acesse /login para entrar no sistema')
    print('Acesse /admin para o painel administrativo (apenas admin)')
    print('='*60 + '\n')


if __name__ == '__main__':
    setup_users()
