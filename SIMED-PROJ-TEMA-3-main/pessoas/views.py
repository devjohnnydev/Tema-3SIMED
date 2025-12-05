from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import (
    CadastroUsuarioForm, PerfilForm, AgendarConsultaForm, 
    RelatorioConsultaForm, AgendarConsultaAtendenteForm, 
    MedicamentoForm, LoginUsuarioForm
)
from .models import User, Perfil, Consulta, Medicamento, Profissional, Especialidade
from .decorators import (
    admin_required, medico_required, atendente_required, paciente_required,
    role_required, min_role_required, get_user_role
)
from django.utils import timezone
from datetime import timedelta, time, datetime
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_GET

def gerar_horarios_disponiveis(medico_id, data_selecionada=None):
    """
    Gera uma lista de tuplas (hora_str, hora_str) para os horários disponíveis
    do médico no dia selecionado, de 15 em 15 minutos, das 8h às 18h.
    """
    horarios_base = []
    hora_inicio = datetime.strptime("08:00", "%H:%M").time()
    hora_fim = datetime.strptime("18:00", "%H:%M").time()
    intervalo = timedelta(minutes=15)

    # Gera todos os horários possíveis de 15 em 15 minutos
    current_time = datetime.combine(datetime.min, hora_inicio)
    while current_time.time() < hora_fim:
        horarios_base.append(current_time.time())
        current_time += intervalo

    if not medico_id or not data_selecionada:
        # Se o médico ou a data não forem selecionados, retorna uma lista vazia
        return []

    # Se a data for selecionada, verifica as consultas existentes
    data_inicio = timezone.make_aware(datetime.combine(data_selecionada, hora_inicio))
    data_fim = timezone.make_aware(datetime.combine(data_selecionada, hora_fim))

    consultas_ocupadas = Consulta.objects.filter(
        medico__id=medico_id,
        data_hora__gte=data_inicio,
        data_hora__lt=data_fim,
        status='agendada'
    ).values_list('data_hora', flat=True)

    # Converte os datetimes ocupados para objetos time localizados
    horarios_ocupados = {timezone.localtime(dt).time() for dt in consultas_ocupadas}
    
    horarios_disponiveis = []
    for h in horarios_base:
        if h not in horarios_ocupados:
            horarios_disponiveis.append((h.isoformat(timespec='minutes'), h.strftime("%H:%M")))
            
    return horarios_disponiveis

@require_GET
def get_horarios_disponiveis_ajax(request):
    """
    View AJAX para retornar os horários disponíveis para um médico e data específicos.
    """
    medico_id_str = request.GET.get('medico_id')
    data_str = request.GET.get('data')

    if not medico_id_str or not data_str:
        return JsonResponse({'error': 'Médico e data são obrigatórios.'}, status=400)

    try:
        medico_id = int(medico_id_str)
        data_selecionada = datetime.strptime(data_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'ID do médico ou formato de data inválido.'}, status=400)

    horarios = gerar_horarios_disponiveis(medico_id, data_selecionada)
    
    # Formato de retorno: [{'value': '08:00:00', 'display': '08:00'}, ...]
    horarios_json = [{'value': h[0], 'display': h[1]} for h in horarios]

    return JsonResponse({'horarios': horarios_json})

# --- VIEWS DE PÁGINA ---

def home(request):
    return render(request, 'pessoas/home.html')

def sobre(request):
    return render(request, 'pessoas/sobre.html')

def produtos(request):
    return render(request, 'pessoas/lista_medicamentos.html')

def nos_encontre(request):
    return render(request, 'pessoas/encontre.html')

def cirurgia(request):
    return render(request, 'pessoas/cirurgia.html')

def exames(request):
    return render(request, 'pessoas/exames.html')

def odontologia(request):
    return render(request, 'pessoas/odontologia.html')

def oftalmologia(request):
    return render(request, 'pessoas/oftalmologia.html') 

def tomografia(request):
    return render(request, 'pessoas/tomografia.html')

def consulta(request):
    return render(request, 'pessoas/consulta.html')

def agenda(request):
    return render(request, 'pessoas/agenda.html')

def politicas_de_uso(request): 
    return render(request, 'pessoas/politicas-de-uso.html')

def profissionais(request):
    """Lista todos os profissionais ativos"""
    profissionais_lista = Profissional.objects.filter(ativo=True).select_related('especialidade')
    especialidades = Especialidade.objects.all()
    return render(request, 'pessoas/profissionais.html', {
        'profissionais': profissionais_lista,
        'especialidades': especialidades
    })

def profissional_detalhe(request, slug):
    """Página individual do profissional"""
    profissional = get_object_or_404(Profissional, slug=slug, ativo=True)
    return render(request, 'pessoas/profissional_detalhe.html', {
        'profissional': profissional
    })

def profissionais_por_especialidade(request, especialidade_id):
    """Lista profissionais de uma especialidade específica"""
    especialidade = get_object_or_404(Especialidade, pk=especialidade_id)
    profissionais_lista = Profissional.objects.filter(
        especialidade=especialidade, 
        ativo=True
    )
    return render(request, 'pessoas/profissionais_especialidade.html', {
        'especialidade': especialidade,
        'profissionais': profissionais_lista
    })

def privacidade(request):
    return render(request,'pessoas/privacidade.html')

# --- VIEWS DE AUTENTICAÇÃO ---

def login_view(request):
    if request.method == 'POST':
        form = LoginUsuarioForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            messages.success(request, f'Bem-vindo(a) de volta, {user.first_name or user.username}!')

            # Redirecionamento baseado no tipo de usuário
            if user.is_staff:
                return redirect('dashboard_consultas')
            elif hasattr(user, 'perfil'):
                if user.perfil.tipo_usuario == 'medico':
                    return redirect('painel_medico')
                elif user.perfil.tipo_usuario == 'paciente':
                    return redirect('painel_paciente')
                elif user.perfil.tipo_usuario == 'atendente':
                    return redirect('painel_atendente')

            return redirect('home')
    else:
        form = LoginUsuarioForm()
    return render(request, 'pessoas/login.html', {'form': form})


def cadastrar_usuario(request):
    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            Perfil.objects.get_or_create(usuario=user, defaults={'tipo_usuario': 'paciente'})
            messages.success(request, 'Cadastro realizado com sucesso! Faça login para continuar.')
            return redirect('login')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = CadastroUsuarioForm()

    return render(request, 'pessoas/cadastrar_usuario.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

# --- VIEWS DE MEDICAMENTOS ---

def excluir_medicamento(request, medicamento_id):
    medicamento = get_object_or_404(Medicamento, pk=medicamento_id)
    if request.method == 'POST':
        nome = medicamento.nome
        medicamento.delete()
        messages.success(request, f'Medicamento "{nome}" excluído com sucesso.')
        return redirect('dashboard_produtos')
    return redirect('dashboard_produtos')

def cadastrar_medicamento(request):
    if request.method == 'POST':
        form = MedicamentoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard_produtos')
    else:
        form = MedicamentoForm()
    
    contexto = {
        'form': form
    }
    return render(request, 'pessoas/cadastrar_medicamento.html', contexto)

def lista_medicamentos(request):
    medicamentos = Medicamento.objects.all().order_by('nome')
    contexto = {
        'medicamentos': medicamentos
    }
    return render(request, 'pessoas/lista_medicamentos.html', contexto)

# --- PAINÉIS (DASHBOARDS) ---

@login_required
def painel(request):
    try:
        perfil = request.user.perfil
        if request.user.is_staff:
            return redirect('dashboard_consultas')
        elif perfil.tipo_usuario == 'medico':
            return redirect('dashboard')
        elif perfil.tipo_usuario == 'paciente':
            return redirect('home')
        elif perfil.tipo_usuario == "atendente":
            return redirect("painel_atendente")
    except Perfil.DoesNotExist:
        return redirect('login')
        
@medico_required
def painel_medico(request):
    user_role = get_user_role(request.user)
    if user_role == 'admin':
        consultas = Consulta.objects.all().order_by('data_hora')
    else:
        consultas = Consulta.objects.filter(medico=request.user).order_by('data_hora')
    return render(request, 'pessoas/painel_medico.html', {'consultas': consultas})

@paciente_required
def painel_paciente(request):
    user_role = get_user_role(request.user)
    if user_role == 'admin':
        consultas = Consulta.objects.all().order_by('data_hora')
    else:
        consultas = Consulta.objects.filter(paciente=request.user).order_by('data_hora')

    if request.method == 'POST':
        form = AgendarConsultaForm(request.POST)
        if form.is_valid():
            nova_consulta = form.save(commit=False)
            nova_consulta.paciente = request.user
            nova_consulta.data_hora = form.cleaned_data.get('data_hora')
            nova_consulta.save()
            return redirect('painel_paciente')
    else:
        form = AgendarConsultaForm()

    return render(request, 'pessoas/painel_paciente.html', {
        'consultas': consultas,
        'form': form
    })

@login_required
def checkup_consulta(request):
    return render(request, 'pessoas/checkup_consulta.html')

@login_required
def checkup_tratamento(request):
    return render(request, 'pessoas/checkup_tratamento.html')
    
@atendente_required
def painel_atendente(request):
    consultas = Consulta.objects.all().order_by("data_hora")

    if request.method == "POST":
        form = AgendarConsultaAtendenteForm(request.POST)
        if form.is_valid():
            nova_consulta = form.save(commit=False)
            nova_consulta.data_hora = form.cleaned_data.get('data_hora')
            nova_consulta.save()
            messages.success(request, 'Consulta agendada com sucesso!')
            return redirect("painel_atendente")
    else:
        form = AgendarConsultaAtendenteForm()

    form.fields['hora'].choices = [('', '---------')]

    return render(request, "pessoas/painel_atendente.html", {
        "consultas": consultas,
        "form": form
    })

# --- AÇÕES ESPECÍFICAS ---

@medico_required
def escrever_relatorio(request, consulta_id):
    user_role = get_user_role(request.user)
    if user_role == 'admin':
        consulta = get_object_or_404(Consulta, id=consulta_id)
    else:
        consulta = get_object_or_404(Consulta, id=consulta_id, medico=request.user)

    if request.method == 'POST':
        form = RelatorioConsultaForm(request.POST, instance=consulta)
        if form.is_valid():
            consulta.status = 'concluida'
            form.save()
            messages.success(request, 'Relatório salvo com sucesso!')
            return redirect('painel_medico')
    else:
        form = RelatorioConsultaForm(instance=consulta)

    return render(request, 'pessoas/escrever_relatorio.html', {'form': form, 'consulta': consulta})

# --- DASHBOARD ADMINISTRATIVO ---

@admin_required
def dashboard_admin(request):
    return redirect('dashboard_consultas')

@admin_required
def dashboard_produtos(request):
    medicamentos = Medicamento.objects.all().order_by('nome')
    return render(request, 'pessoas/dashboard_produtos.html', {'medicamentos': medicamentos})

@admin_required
def dashboard_consultas(request):
    from django.db.models import Count
    from datetime import date
    
    total_consultas = Consulta.objects.count()
    consultas_realizadas = Consulta.objects.filter(status='concluida').count()
    consultas_agendadas = Consulta.objects.filter(status='agendada').count()
    consultas_canceladas = Consulta.objects.filter(status='cancelada').count()
    
    max_atendimentos_dia = Consulta.objects.filter(
        data_hora__date=date.today()
    ).count()
    
    medico_mais_ocupado = Consulta.objects.filter(
        status='agendada'
    ).values(
        'medico__first_name', 'medico__last_name'
    ).annotate(
        total=Count('id')
    ).order_by('-total').first()
    
    profissional_nome = "N/A"
    if medico_mais_ocupado:
        profissional_nome = f"{medico_mais_ocupado['medico__first_name']} {medico_mais_ocupado['medico__last_name']}"
    
    contexto = {
        'total_consultas': total_consultas,
        'consultas_realizadas': consultas_realizadas,
        'max_atendimentos_dia': max_atendimentos_dia,
        'consultas_agendadas': consultas_agendadas,
        'consultas_canceladas': consultas_canceladas,
        'profissional_nome': profissional_nome,
    }
    
    return render(request, 'pessoas/dashboard_consultas.html', contexto)

@admin_required
def dashboard_ocupacao(request):
    consultas = Consulta.objects.filter(status='agendada').order_by('data_hora')
    return render(request, 'pessoas/dashboard_ocupacao.html', {'consultas': consultas})

@admin_required
def dashboard_pacientes(request):
    pacientes = User.objects.filter(perfil__tipo_usuario='paciente').order_by('first_name')
    return render(request, 'pessoas/dashboard_pacientes.html', {'pacientes': pacientes})

@admin_required
def dashboard_medicos(request):
    medicos = User.objects.filter(perfil__tipo_usuario='medico').order_by('first_name')
    return render(request, 'pessoas/dashboard_medicos.html', {'medicos': medicos})

@admin_required
def editar_medicamento(request, medicamento_id):
    medicamento = get_object_or_404(Medicamento, pk=medicamento_id)
    if request.method == 'POST':
        form = MedicamentoForm(request.POST, request.FILES, instance=medicamento)
        if form.is_valid():
            form.save()
            return redirect('dashboard_produtos')
    else:
        form = MedicamentoForm(instance=medicamento)
    return render(request, 'pessoas/editar_medicamento.html', {'form': form})

@admin_required
def cancelar_consulta_admin(request, consulta_id):
    consulta = get_object_or_404(Consulta, pk=consulta_id)
    consulta.status = 'cancelada'
    consulta.save()
    messages.success(request, 'Consulta cancelada com sucesso.')
    return redirect('dashboard_ocupacao')

@admin_required
def remover_medico(request, medico_id):
    medico = get_object_or_404(User, pk=medico_id, perfil__tipo_usuario='medico')
    nome = f"{medico.first_name} {medico.last_name}"
    medico.delete()
    messages.success(request, f'Médico {nome} removido com sucesso.')
    return redirect('dashboard_medicos')

@admin_required
def remover_paciente(request, paciente_id):
    paciente = get_object_or_404(User, pk=paciente_id, perfil__tipo_usuario='paciente')
    nome = f"{paciente.first_name} {paciente.last_name}"
    paciente.delete()
    messages.success(request, f'Paciente {nome} removido com sucesso.')
    return redirect('dashboard_pacientes')

@admin_required
def gerenciar_cargos(request, user_id):
    usuario = get_object_or_404(User, pk=user_id)
    perfil, created = Perfil.objects.get_or_create(usuario=usuario, defaults={'tipo_usuario': 'paciente'})
    
    if request.method == 'POST':
        tipo_usuario = request.POST.get('tipo_usuario')
        if tipo_usuario in ['admin', 'medico', 'paciente', 'atendente']:
            perfil.tipo_usuario = tipo_usuario
            perfil.save()
            messages.success(request, f'Cargo de {usuario.first_name} atualizado para {perfil.get_tipo_usuario_display()}.')
            return redirect('dashboard_pacientes')
    
    cargos = Perfil.TIPOS_USUARIO
    return render(request, 'pessoas/gerenciar_cargos.html', {
        'usuario': usuario,
        'perfil': perfil,
        'cargos': cargos
    })

def consulta_rapida(request):
    return render(request, 'pessoas/consulta_rapida.html')
