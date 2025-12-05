#!/usr/bin/env python
"""
Script de inicializacao completa para Railway
Execute com: python scripts/init_railway.py
Ou via Railway: railway run python scripts/init_railway.py

Este script:
1. Aplica todas as migracoes
2. Coleta arquivos estaticos
3. Cria o site padrao
4. Insere especialidades medicas
5. Cria usuario administrador
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cadastro_pessoas.settings')

import django
django.setup()

from django.core.management import call_command
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from pessoas.models import Perfil, Especialidade


def run_migrations():
    """Aplica todas as migracoes pendentes"""
    print('\n[1/5] Aplicando migracoes...')
    call_command('migrate', '--noinput')
    print('Migracoes aplicadas com sucesso!')


def collect_static():
    """Coleta arquivos estaticos"""
    print('\n[2/5] Coletando arquivos estaticos...')
    call_command('collectstatic', '--noinput', '--clear')
    print('Arquivos estaticos coletados!')


def setup_site():
    """Configura o site padrao"""
    print('\n[3/5] Configurando site...')
    
    domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'simed.railway.app')
    
    site, created = Site.objects.update_or_create(
        id=1,
        defaults={
            'domain': domain,
            'name': 'SIMED - Servico Integrado de Medicina'
        }
    )
    
    if created:
        print(f'Site criado: {domain}')
    else:
        print(f'Site atualizado: {domain}')


def setup_especialidades():
    """Insere especialidades medicas padrao"""
    print('\n[4/5] Configurando especialidades...')
    
    especialidades = [
        ('Clinica Geral', 'Atendimento medico geral para adultos', 'fa-user-md'),
        ('Pediatria', 'Atendimento especializado para criancas', 'fa-baby'),
        ('Cardiologia', 'Especialidade do coracao e sistema cardiovascular', 'fa-heartbeat'),
        ('Dermatologia', 'Especialidade da pele, cabelos e unhas', 'fa-hand-sparkles'),
        ('Ortopedia', 'Especialidade dos ossos, articulacoes e musculos', 'fa-bone'),
        ('Ginecologia', 'Saude da mulher', 'fa-venus'),
        ('Oftalmologia', 'Especialidade dos olhos e visao', 'fa-eye'),
        ('Neurologia', 'Especialidade do sistema nervoso', 'fa-brain'),
        ('Psiquiatria', 'Saude mental e transtornos psiquiatricos', 'fa-comments'),
        ('Endocrinologia', 'Especialidade das glandulas e hormonios', 'fa-syringe'),
        ('Urologia', 'Sistema urinario e reprodutor masculino', 'fa-procedures'),
        ('Gastroenterologia', 'Sistema digestivo', 'fa-stomach'),
        ('Pneumologia', 'Sistema respiratorio', 'fa-lungs'),
        ('Otorrinolaringologia', 'Ouvido, nariz e garganta', 'fa-ear'),
        ('Fisioterapia', 'Reabilitacao fisica', 'fa-running'),
    ]
    
    count = 0
    for nome, descricao, icone in especialidades:
        _, created = Especialidade.objects.get_or_create(
            nome=nome,
            defaults={'descricao': descricao, 'icone': icone}
        )
        if created:
            count += 1
    
    print(f'{count} especialidades adicionadas. Total: {Especialidade.objects.count()}')


def create_admin():
    """Cria usuario administrador"""
    print('\n[5/5] Configurando administrador...')
    
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
        print(f'Superusuario "{admin_username}" criado!')
    
    if not hasattr(user, 'perfil'):
        Perfil.objects.create(usuario=user, tipo_usuario='admin')
    
    return admin_username, admin_email, admin_password


def main():
    """Executa todas as etapas de inicializacao"""
    print('='*60)
    print('SIMED - Inicializacao do Sistema para Railway')
    print('='*60)
    
    try:
        run_migrations()
        collect_static()
        setup_site()
        setup_especialidades()
        username, email, password = create_admin()
        
        print('\n' + '='*60)
        print('INICIALIZACAO CONCLUIDA COM SUCESSO!')
        print('='*60)
        print('\nCREDENCIAIS DO ADMINISTRADOR:')
        print(f'  Username: {username}')
        print(f'  Email: {email}')
        print(f'  Password: {password}')
        print('\nACESSOS:')
        print('  Painel Admin: /admin')
        print('  Site: /')
        print('='*60)
        
    except Exception as e:
        print(f'\nERRO durante inicializacao: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
