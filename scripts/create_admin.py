#!/usr/bin/env python
"""
Script para criar usuario administrador no SIMED
Execute com: python scripts/create_admin.py
Ou via Railway: railway run python scripts/create_admin.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cadastro_pessoas.settings')

import django
django.setup()

from django.contrib.auth.models import User
from pessoas.models import Perfil


def create_admin():
    """Cria usuario administrador padrao"""
    
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@simed.com')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'SiMED@2024!')
    
    if User.objects.filter(username=admin_username).exists():
        print(f'Usuario "{admin_username}" ja existe.')
        user = User.objects.get(username=admin_username)
    else:
        user = User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            first_name='Administrador',
            last_name='SIMED'
        )
        print(f'Superusuario "{admin_username}" criado com sucesso!')
    
    if not hasattr(user, 'perfil'):
        Perfil.objects.create(usuario=user, tipo_usuario='admin')
        print(f'Perfil de administrador criado para "{admin_username}"')
    else:
        user.perfil.tipo_usuario = 'admin'
        user.perfil.save()
        print(f'Perfil de "{admin_username}" atualizado para admin')
    
    print('\n' + '='*50)
    print('CREDENCIAIS DO ADMINISTRADOR:')
    print('='*50)
    print(f'Username: {admin_username}')
    print(f'Email: {admin_email}')
    print(f'Password: {admin_password}')
    print('='*50)
    print('\nIMPORTANTE: Altere a senha apos o primeiro login!')
    print('Acesse: /admin para o painel administrativo')


if __name__ == '__main__':
    create_admin()
