#!/usr/bin/env python
"""
Database initialization script for CIMED Medical Clinic System.

This script creates sample data for development and testing purposes.
Run with: python manage.py shell < scripts/init_db.py
Or: python scripts/init_db.py (after setting DJANGO_SETTINGS_MODULE)
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cadastro_pessoas.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

django.setup()

from django.contrib.auth.models import User
from pessoas.models import Especialidade, Profissional, Perfil, Medicamento


def create_specialties():
    """Create sample medical specialties."""
    especialidades_data = [
        {'nome': 'Cardiologia', 'icone': 'fa-heart', 'descricao': 'Especialidade focada no diagnóstico e tratamento de doenças do coração e sistema cardiovascular.'},
        {'nome': 'Dermatologia', 'icone': 'fa-hand-sparkles', 'descricao': 'Especialidade médica dedicada ao diagnóstico e tratamento de doenças da pele, cabelos e unhas.'},
        {'nome': 'Ortopedia', 'icone': 'fa-bone', 'descricao': 'Especialidade focada no sistema musculoesquelético, tratando fraturas, lesões e problemas ósseos.'},
        {'nome': 'Pediatria', 'icone': 'fa-baby', 'descricao': 'Especialidade dedicada ao cuidado da saúde de bebês, crianças e adolescentes.'},
        {'nome': 'Neurologia', 'icone': 'fa-brain', 'descricao': 'Especialidade que trata doenças do sistema nervoso central e periférico.'},
        {'nome': 'Oftalmologia', 'icone': 'fa-eye', 'descricao': 'Especialidade focada na saúde dos olhos e tratamento de problemas visuais.'},
        {'nome': 'Ginecologia', 'icone': 'fa-venus', 'descricao': 'Especialidade dedicada à saúde do sistema reprodutor feminino.'},
        {'nome': 'Clínica Geral', 'icone': 'fa-stethoscope', 'descricao': 'Medicina geral para diagnóstico e tratamento de diversas condições de saúde.'},
        {'nome': 'Odontologia', 'icone': 'fa-tooth', 'descricao': 'Especialidade focada na saúde bucal, tratamento de dentes e gengivas.'},
        {'nome': 'Psiquiatria', 'icone': 'fa-head-side-virus', 'descricao': 'Especialidade dedicada ao diagnóstico e tratamento de transtornos mentais.'},
    ]
    
    created = 0
    for esp_data in especialidades_data:
        obj, is_new = Especialidade.objects.get_or_create(
            nome=esp_data['nome'],
            defaults={'icone': esp_data['icone'], 'descricao': esp_data['descricao']}
        )
        if is_new:
            created += 1
            print(f"  + Especialidade criada: {obj.nome}")
        else:
            print(f"  - Especialidade já existe: {obj.nome}")
    
    return created


def create_professionals():
    """Create sample medical professionals."""
    profissionais_data = [
        {
            'nome': 'Dr. Carlos Alberto Silva',
            'especialidade': 'Cardiologia',
            'crm': 'CRM/SP 123456',
            'email': 'carlos.silva@cimed.com',
            'telefone': '(11) 99999-1234',
            'biografia': 'Cardiologista com mais de 15 anos de experiência no tratamento de doenças cardiovasculares. Especializado em cardiologia intervencionista e prevenção de doenças do coração.',
            'formacao': 'Medicina - Universidade de São Paulo (USP)\nResidência em Cardiologia - InCor\nFellow em Cardiologia Intervencionista - Cleveland Clinic',
            'certificacoes': 'Título de Especialista em Cardiologia - SBC\nCertificação em Hemodinâmica\nMembro da Sociedade Brasileira de Cardiologia',
            'objetivos': 'Meu objetivo é proporcionar um atendimento humanizado e de excelência, utilizando as mais modernas técnicas diagnósticas e terapêuticas para cuidar da saúde cardiovascular dos meus pacientes.',
            'ativo': True,
            'destaque': True
        },
        {
            'nome': 'Dra. Maria Fernanda Costa',
            'especialidade': 'Dermatologia',
            'crm': 'CRM/SP 234567',
            'email': 'maria.costa@cimed.com',
            'telefone': '(11) 99999-2345',
            'biografia': 'Dermatologista especializada em dermatologia estética e clínica. Atuo no diagnóstico e tratamento de doenças da pele, com foco em procedimentos minimamente invasivos.',
            'formacao': 'Medicina - UNIFESP\nResidência em Dermatologia - Hospital das Clínicas\nPós-graduação em Dermatologia Estética',
            'certificacoes': 'Título de Especialista em Dermatologia - SBD\nCertificação em Procedimentos Estéticos\nMembro da Sociedade Brasileira de Dermatologia',
            'objetivos': 'Busco oferecer tratamentos personalizados que combinam saúde e bem-estar, sempre com foco na segurança e satisfação dos pacientes.',
            'ativo': True,
            'destaque': True
        },
        {
            'nome': 'Dr. Roberto Mendes',
            'especialidade': 'Ortopedia',
            'crm': 'CRM/SP 345678',
            'email': 'roberto.mendes@cimed.com',
            'telefone': '(11) 99999-3456',
            'biografia': 'Ortopedista especializado em cirurgia do joelho e medicina esportiva. Experiência no tratamento de atletas profissionais e amadores.',
            'formacao': 'Medicina - Unicamp\nResidência em Ortopedia - Hospital Einstein\nFellow em Cirurgia do Joelho - Hospital for Special Surgery, NYC',
            'certificacoes': 'Título de Especialista em Ortopedia - SBOT\nCertificação em Artroscopia\nMédico do Esporte - SBME',
            'objetivos': 'Minha missão é ajudar os pacientes a recuperarem sua mobilidade e qualidade de vida através de tratamentos modernos e cirurgias minimamente invasivas.',
            'ativo': True,
            'destaque': False
        },
        {
            'nome': 'Dra. Ana Paula Santos',
            'especialidade': 'Pediatria',
            'crm': 'CRM/SP 456789',
            'email': 'ana.santos@cimed.com',
            'telefone': '(11) 99999-4567',
            'biografia': 'Pediatra com foco em puericultura e desenvolvimento infantil. Apaixonada por cuidar da saúde das crianças desde os primeiros dias de vida.',
            'formacao': 'Medicina - USP\nResidência em Pediatria - Hospital Infantil Sabará\nEspecialização em Neonatologia',
            'certificacoes': 'Título de Especialista em Pediatria - SBP\nCertificação em Aleitamento Materno - IBCLC\nMembro da Sociedade Brasileira de Pediatria',
            'objetivos': 'Acredito que cada criança é única e merece um cuidado individualizado. Trabalho para promover a saúde e o desenvolvimento saudável desde a primeira infância.',
            'ativo': True,
            'destaque': True
        },
        {
            'nome': 'Dr. Paulo Henrique Lima',
            'especialidade': 'Neurologia',
            'crm': 'CRM/SP 567890',
            'email': 'paulo.lima@cimed.com',
            'telefone': '(11) 99999-5678',
            'biografia': 'Neurologista especializado em doenças neurodegenerativas e distúrbios do movimento. Pesquisador ativo na área de neurociências.',
            'formacao': 'Medicina - UFRJ\nResidência em Neurologia - Hospital das Clínicas FMUSP\nDoutorado em Neurologia - USP',
            'certificacoes': 'Título de Especialista em Neurologia - ABN\nMembro da Academia Brasileira de Neurologia\nPesquisador CNPq',
            'objetivos': 'Meu compromisso é oferecer diagnósticos precisos e tratamentos baseados nas mais recentes evidências científicas para melhorar a qualidade de vida dos pacientes neurológicos.',
            'ativo': True,
            'destaque': False
        },
        {
            'nome': 'Dra. Juliana Ferreira',
            'especialidade': 'Clínica Geral',
            'crm': 'CRM/SP 678901',
            'email': 'juliana.ferreira@cimed.com',
            'telefone': '(11) 99999-6789',
            'biografia': 'Clínica geral com abordagem integral do paciente. Especializada em medicina preventiva e acompanhamento de condições crônicas.',
            'formacao': 'Medicina - Santa Casa de São Paulo\nResidência em Clínica Médica - Hospital do Servidor Público\nPós-graduação em Medicina da Família',
            'certificacoes': 'Título de Especialista em Clínica Médica - SBCM\nCertificação em Medicina Preventiva\nMembro da SBMFC',
            'objetivos': 'Acredito na medicina preventiva e no cuidado continuado. Meu objetivo é ser a primeira referência de saúde para meus pacientes.',
            'ativo': True,
            'destaque': False
        }
    ]
    
    created = 0
    for prof_data in profissionais_data:
        especialidade = Especialidade.objects.filter(nome=prof_data['especialidade']).first()
        if not especialidade:
            print(f"  ! Especialidade não encontrada: {prof_data['especialidade']}")
            continue
        
        obj, is_new = Profissional.objects.get_or_create(
            crm=prof_data['crm'],
            defaults={
                'nome': prof_data['nome'],
                'especialidade': especialidade,
                'email': prof_data['email'],
                'telefone': prof_data['telefone'],
                'biografia': prof_data['biografia'],
                'formacao': prof_data['formacao'],
                'certificacoes': prof_data['certificacoes'],
                'objetivos': prof_data['objetivos'],
                'ativo': prof_data['ativo'],
                'destaque': prof_data['destaque']
            }
        )
        if is_new:
            created += 1
            print(f"  + Profissional criado: {obj.nome}")
        else:
            print(f"  - Profissional já existe: {obj.nome}")
    
    return created


def create_sample_medications():
    """Create sample medications."""
    medicamentos_data = [
        {
            'nome': 'Dipirona Sódica 500mg',
            'principio_ativo': 'Dipirona Sódica',
            'descricao': 'Analgésico e antitérmico para alívio de dores e febres.',
            'valor': 8.90,
            'necessita_receita': False,
            'estoque': 150
        },
        {
            'nome': 'Amoxicilina 500mg',
            'principio_ativo': 'Amoxicilina',
            'descricao': 'Antibiótico para tratamento de infecções bacterianas.',
            'valor': 24.50,
            'necessita_receita': True,
            'estoque': 80
        },
        {
            'nome': 'Omeprazol 20mg',
            'principio_ativo': 'Omeprazol',
            'descricao': 'Inibidor da bomba de prótons para tratamento de gastrite e úlceras.',
            'valor': 15.90,
            'necessita_receita': False,
            'estoque': 200
        },
        {
            'nome': 'Losartana 50mg',
            'principio_ativo': 'Losartana Potássica',
            'descricao': 'Anti-hipertensivo para controle da pressão arterial.',
            'valor': 18.70,
            'necessita_receita': True,
            'estoque': 120
        },
        {
            'nome': 'Paracetamol 750mg',
            'principio_ativo': 'Paracetamol',
            'descricao': 'Analgésico e antitérmico de ação suave.',
            'valor': 6.50,
            'necessita_receita': False,
            'estoque': 250
        }
    ]
    
    created = 0
    for med_data in medicamentos_data:
        obj, is_new = Medicamento.objects.get_or_create(
            nome=med_data['nome'],
            defaults={
                'principio_ativo': med_data['principio_ativo'],
                'descricao': med_data['descricao'],
                'valor': med_data['valor'],
                'necessita_receita': med_data['necessita_receita'],
                'estoque': med_data['estoque']
            }
        )
        if is_new:
            created += 1
            print(f"  + Medicamento criado: {obj.nome}")
        else:
            print(f"  - Medicamento já existe: {obj.nome}")
    
    return created


def main():
    """Main initialization function."""
    print("\n" + "="*60)
    print("CIMED - Inicialização do Banco de Dados")
    print("="*60 + "\n")
    
    print("[1/3] Criando especialidades médicas...")
    esp_count = create_specialties()
    print(f"      {esp_count} novas especialidades criadas.\n")
    
    print("[2/3] Criando profissionais de saúde...")
    prof_count = create_professionals()
    print(f"      {prof_count} novos profissionais criados.\n")
    
    print("[3/3] Criando medicamentos de exemplo...")
    med_count = create_sample_medications()
    print(f"      {med_count} novos medicamentos criados.\n")
    
    print("="*60)
    print("Inicialização concluída com sucesso!")
    print("="*60 + "\n")
    
    print("Resumo:")
    print(f"  - Especialidades: {Especialidade.objects.count()}")
    print(f"  - Profissionais: {Profissional.objects.count()}")
    print(f"  - Medicamentos: {Medicamento.objects.count()}")
    print()


if __name__ == '__main__':
    main()
