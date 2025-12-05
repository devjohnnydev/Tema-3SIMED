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
from .models import User, Perfil, Consulta, Medicamento, Profissional, Especialidade, HorarioTrabalho
from .decorators import (
    admin_required, medico_required, atendente_required, paciente_required,
    role_required, min_role_required, get_user_role
)
from django.utils import timezone
from datetime import timedelta, time, datetime
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET
from django.template.loader import render_to_string
from weasyprint import HTML
import io

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
    profissionais = Profissional.objects.filter(ativo=True, destaque=True).select_related('especialidade')[:6]
    if not profissionais.exists():
        profissionais = Profissional.objects.filter(ativo=True).select_related('especialidade')[:6]
    return render(request, 'pessoas/sobre.html', {'profissionais': profissionais})

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
        consultas = Consulta.objects.all().order_by('-data_hora')
    else:
        consultas = Consulta.objects.filter(paciente=request.user).order_by('-data_hora')

    if request.method == 'POST':
        form = AgendarConsultaForm(request.POST)
        if form.is_valid():
            nova_consulta = form.save(commit=False)
            nova_consulta.paciente = request.user
            nova_consulta.data_hora = form.cleaned_data.get('data_hora')
            nova_consulta.save()
            medico_nome = f"{nova_consulta.medico.first_name} {nova_consulta.medico.last_name}"
            data_formatada = nova_consulta.data_hora.strftime("%d/%m/%Y às %H:%M")
            messages.success(request, f'Sua consulta com Dr(a). {medico_nome} foi agendada para {data_formatada}. Você pode baixar o comprovante em PDF.')
            return redirect('painel_paciente')
    else:
        form = AgendarConsultaForm()

    medicos = User.objects.filter(perfil__tipo_usuario='medico')
    medicos_info = []
    for medico in medicos:
        try:
            prof = Profissional.objects.get(usuario=medico)
            medicos_info.append({
                'id': medico.id,
                'nome': f"Dr(a). {medico.first_name} {medico.last_name}",
                'foto': prof.foto.url if prof.foto else '',
                'especialidade': prof.especialidade.nome if prof.especialidade else 'Clínica Geral',
                'inicial': medico.first_name[:1].upper() if medico.first_name else 'M'
            })
        except Profissional.DoesNotExist:
            medicos_info.append({
                'id': medico.id,
                'nome': f"Dr(a). {medico.first_name} {medico.last_name}",
                'foto': '',
                'especialidade': 'Clínica Geral',
                'inicial': medico.first_name[:1].upper() if medico.first_name else 'M'
            })

    return render(request, 'pessoas/painel_paciente.html', {
        'consultas': consultas,
        'form': form,
        'medicos_info': medicos_info
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


@login_required
def download_consulta_pdf(request, consulta_id):
    """
    Gera e baixa um PDF com os detalhes da consulta agendada.
    Apenas o paciente dono da consulta ou um admin/médico pode baixar.
    """
    consulta = get_object_or_404(Consulta, pk=consulta_id)
    
    if request.user != consulta.paciente and not request.user.is_staff:
        try:
            perfil = request.user.perfil
            if perfil.tipo_usuario not in ['admin', 'medico', 'atendente']:
                messages.error(request, 'Você não tem permissão para baixar este documento.')
                return redirect('painel_paciente')
        except Perfil.DoesNotExist:
            messages.error(request, 'Você não tem permissão para baixar este documento.')
            return redirect('painel_paciente')
    
    html_string = render_to_string('pessoas/consulta_pdf.html', {
        'consulta': consulta,
        'now': timezone.now(),
    })
    
    html = HTML(string=html_string)
    pdf_buffer = io.BytesIO()
    html.write_pdf(target=pdf_buffer)
    pdf_buffer.seek(0)
    
    filename = f"consulta_{consulta.id:05d}_{consulta.data_hora.strftime('%Y%m%d')}.pdf"
    
    response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


# --- GERENCIAMENTO DE PROFISSIONAIS ---

@admin_required
def dashboard_profissionais(request):
    profissionais = Profissional.objects.all().select_related('especialidade').prefetch_related('horarios')
    especialidades = Especialidade.objects.all()
    return render(request, 'pessoas/dashboard_profissionais.html', {
        'profissionais': profissionais,
        'especialidades': especialidades
    })

@admin_required
def adicionar_profissional(request):
    especialidades = Especialidade.objects.all()
    usuarios_disponiveis = User.objects.filter(
        perfil__tipo_usuario__in=['medico', 'atendente']
    ).exclude(profissional__isnull=False)
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        especialidade_id = request.POST.get('especialidade')
        crm = request.POST.get('crm')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        biografia = request.POST.get('biografia')
        formacao = request.POST.get('formacao')
        certificacoes = request.POST.get('certificacoes')
        usuario_id = request.POST.get('usuario')
        ativo = 'ativo' in request.POST
        destaque = 'destaque' in request.POST
        foto = request.FILES.get('foto')
        
        profissional = Profissional(
            nome=nome,
            crm=crm,
            email=email,
            telefone=telefone,
            biografia=biografia,
            formacao=formacao,
            certificacoes=certificacoes,
            ativo=ativo,
            destaque=destaque
        )
        
        if especialidade_id:
            profissional.especialidade = Especialidade.objects.get(pk=especialidade_id)
        if usuario_id:
            profissional.usuario = User.objects.get(pk=usuario_id)
        if foto:
            profissional.foto = foto
            
        profissional.save()
        messages.success(request, f'Profissional {nome} cadastrado com sucesso!')
        return redirect('dashboard_profissionais')
    
    return render(request, 'pessoas/adicionar_profissional.html', {
        'especialidades': especialidades,
        'usuarios_disponiveis': usuarios_disponiveis
    })

@admin_required
def editar_profissional(request, profissional_id):
    profissional = get_object_or_404(Profissional, pk=profissional_id)
    especialidades = Especialidade.objects.all()
    usuarios_disponiveis = User.objects.filter(
        perfil__tipo_usuario__in=['medico', 'atendente']
    ).exclude(profissional__isnull=False) | User.objects.filter(pk=profissional.usuario_id if profissional.usuario else 0)
    
    if request.method == 'POST':
        profissional.nome = request.POST.get('nome')
        profissional.crm = request.POST.get('crm')
        profissional.email = request.POST.get('email')
        profissional.telefone = request.POST.get('telefone')
        profissional.biografia = request.POST.get('biografia')
        profissional.formacao = request.POST.get('formacao')
        profissional.certificacoes = request.POST.get('certificacoes')
        profissional.ativo = 'ativo' in request.POST
        profissional.destaque = 'destaque' in request.POST
        
        especialidade_id = request.POST.get('especialidade')
        if especialidade_id:
            profissional.especialidade = Especialidade.objects.get(pk=especialidade_id)
        else:
            profissional.especialidade = None
            
        usuario_id = request.POST.get('usuario')
        if usuario_id:
            profissional.usuario = User.objects.get(pk=usuario_id)
        else:
            profissional.usuario = None
            
        if request.FILES.get('foto'):
            profissional.foto = request.FILES.get('foto')
            
        profissional.save()
        messages.success(request, f'Profissional {profissional.nome} atualizado com sucesso!')
        return redirect('dashboard_profissionais')
    
    return render(request, 'pessoas/adicionar_profissional.html', {
        'profissional': profissional,
        'especialidades': especialidades,
        'usuarios_disponiveis': usuarios_disponiveis
    })

@admin_required
def remover_profissional(request, profissional_id):
    profissional = get_object_or_404(Profissional, pk=profissional_id)
    nome = profissional.nome
    profissional.delete()
    messages.success(request, f'Profissional {nome} removido com sucesso.')
    return redirect('dashboard_profissionais')


# --- GERENCIAMENTO DE ESPECIALIDADES ---

@admin_required
def dashboard_especialidades(request):
    especialidades = Especialidade.objects.all().prefetch_related('profissional_set')
    return render(request, 'pessoas/dashboard_especialidades.html', {
        'especialidades': especialidades
    })

@admin_required
def adicionar_especialidade(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        icone = request.POST.get('icone', 'fa-stethoscope')
        
        if nome:
            Especialidade.objects.create(nome=nome, descricao=descricao, icone=icone)
            messages.success(request, f'Especialidade {nome} criada com sucesso!')
    
    return redirect('dashboard_especialidades')

@admin_required
def remover_especialidade(request, especialidade_id):
    especialidade = get_object_or_404(Especialidade, pk=especialidade_id)
    nome = especialidade.nome
    especialidade.delete()
    messages.success(request, f'Especialidade {nome} removida com sucesso.')
    return redirect('dashboard_especialidades')


# --- GERENCIAMENTO DE HORÁRIOS ---

@admin_required
def dashboard_horarios(request):
    profissionais = Profissional.objects.filter(ativo=True).select_related('especialidade').prefetch_related('horarios')
    
    for prof in profissionais:
        horarios_por_dia = {}
        for h in prof.horarios.filter(ativo=True):
            if h.dia_semana not in horarios_por_dia:
                horarios_por_dia[h.dia_semana] = []
            horarios_por_dia[h.dia_semana].append(h)
        prof.horarios_por_dia = horarios_por_dia
    
    return render(request, 'pessoas/dashboard_horarios.html', {
        'profissionais': profissionais
    })

@admin_required
def configurar_horarios(request, profissional_id):
    profissional = get_object_or_404(Profissional, pk=profissional_id)
    
    dias_semana = [
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    
    horarios_existentes = profissional.horarios.filter(ativo=True)
    horarios_ativos = list(horarios_existentes.values_list('dia_semana', flat=True))
    horarios_dict = {h.dia_semana: h for h in horarios_existentes}
    
    if request.method == 'POST':
        HorarioTrabalho.objects.filter(profissional=profissional).delete()
        
        for dia_num, dia_nome in dias_semana:
            ativo = f'dia_{dia_num}_ativo' in request.POST
            if ativo:
                hora_inicio = request.POST.get(f'dia_{dia_num}_inicio', '08:00')
                hora_fim = request.POST.get(f'dia_{dia_num}_fim', '18:00')
                intervalo = int(request.POST.get(f'dia_{dia_num}_intervalo', 30))
                
                HorarioTrabalho.objects.create(
                    profissional=profissional,
                    dia_semana=dia_num,
                    hora_inicio=hora_inicio,
                    hora_fim=hora_fim,
                    intervalo_minutos=intervalo,
                    ativo=True
                )
        
        messages.success(request, f'Horários de {profissional.nome} atualizados com sucesso!')
        return redirect('dashboard_horarios')
    
    return render(request, 'pessoas/configurar_horarios.html', {
        'profissional': profissional,
        'dias_semana': dias_semana,
        'horarios_ativos': horarios_ativos,
        'horarios_dict': horarios_dict
    })

@admin_required
def remover_horario(request, horario_id):
    horario = get_object_or_404(HorarioTrabalho, pk=horario_id)
    horario.delete()
    return JsonResponse({'success': True})


# --- API PARA HORÁRIOS DISPONÍVEIS ---

@require_GET
def get_horarios_profissional_ajax(request, profissional_id):
    """
    Retorna os horários disponíveis de um profissional para uma data específica.
    """
    data_str = request.GET.get('data')
    
    if not data_str:
        return JsonResponse({'error': 'Data é obrigatória.'}, status=400)
    
    try:
        profissional = Profissional.objects.get(pk=profissional_id, ativo=True)
        data_selecionada = datetime.strptime(data_str, '%Y-%m-%d').date()
    except (Profissional.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Profissional ou data inválidos.'}, status=400)
    
    dia_semana = data_selecionada.weekday()
    
    horario_trabalho = profissional.horarios.filter(dia_semana=dia_semana, ativo=True).first()
    
    if not horario_trabalho:
        return JsonResponse({
            'disponivel': False,
            'mensagem': 'Profissional não atende neste dia.',
            'horarios': []
        })
    
    horarios_disponiveis = []
    hora_atual = datetime.combine(data_selecionada, horario_trabalho.hora_inicio)
    hora_fim = datetime.combine(data_selecionada, horario_trabalho.hora_fim)
    intervalo = timedelta(minutes=horario_trabalho.intervalo_minutos)
    
    consultas_ocupadas = set()
    if profissional.usuario:
        consultas = Consulta.objects.filter(
            medico=profissional.usuario,
            data_hora__date=data_selecionada,
            status__in=['agendada', 'confirmada']
        ).values_list('data_hora', flat=True)
        consultas_ocupadas = {timezone.localtime(dt).time() for dt in consultas}
    
    while hora_atual < hora_fim:
        horario_time = hora_atual.time()
        if horario_time not in consultas_ocupadas:
            horarios_disponiveis.append({
                'value': horario_time.strftime('%H:%M'),
                'display': horario_time.strftime('%H:%M')
            })
        hora_atual += intervalo
    
    return JsonResponse({
        'disponivel': True,
        'profissional': {
            'id': profissional.id,
            'nome': profissional.nome,
            'foto': profissional.foto.url if profissional.foto else None,
            'especialidade': profissional.especialidade.nome if profissional.especialidade else None
        },
        'horarios': horarios_disponiveis
    })


@login_required
def download_consulta_ics(request, consulta_id):
    """
    Gera e baixa um arquivo ICS (iCalendar) para adicionar a consulta ao calendário.
    """
    consulta = get_object_or_404(Consulta, pk=consulta_id)
    
    if request.user != consulta.paciente and not request.user.is_staff:
        try:
            perfil = request.user.perfil
            if perfil.tipo_usuario not in ['admin', 'medico', 'atendente']:
                messages.error(request, 'Você não tem permissão para baixar este arquivo.')
                return redirect('painel_paciente')
        except Perfil.DoesNotExist:
            messages.error(request, 'Você não tem permissão para baixar este arquivo.')
            return redirect('painel_paciente')
    
    start_dt = consulta.data_hora
    end_dt = start_dt + timedelta(minutes=30)
    
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//SIMED//Consulta Médica//PT
BEGIN:VEVENT
UID:consulta-{consulta.id}@simed.com.br
DTSTAMP:{timezone.now().strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{start_dt.strftime('%Y%m%dT%H%M%S')}
DTEND:{end_dt.strftime('%Y%m%dT%H%M%S')}
SUMMARY:Consulta SIMED - Dr(a). {consulta.medico.first_name} {consulta.medico.last_name}
DESCRIPTION:Consulta médica na SIMED - Serviço Integrado de Medicina
LOCATION:SIMED - Clínica Médica
STATUS:CONFIRMED
BEGIN:VALARM
TRIGGER:-PT1H
ACTION:DISPLAY
DESCRIPTION:Lembrete: Consulta em 1 hora
END:VALARM
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:Lembrete: Consulta amanhã
END:VALARM
END:VEVENT
END:VCALENDAR"""
    
    response = HttpResponse(ics_content, content_type='text/calendar')
    response['Content-Disposition'] = f'attachment; filename="consulta_simed_{consulta.id}.ics"'
    
    return response
