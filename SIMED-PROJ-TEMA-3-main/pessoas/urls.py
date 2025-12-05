# pessoas/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
# A importação do 'admin' foi REMOVIDA daqui

# A linha app_name = 'pessoas' foi REMOVIDA para corrigir o NoReverseMatch

urlpatterns = [
    # O path('admin/', ...) foi REMOVIDO daqui.
    
    # O path('home/', ...) foi MUDADO para '' (vazio) para corrigir o erro 404
   path('', views.home, name='home'),
   path('sobre/', views.sobre, name='sobre'),
   path('consulta-rapida/', views.consulta_rapida, name='consulta_rapida'),
       
    path('cirurgia/', views.cirurgia, name='cirurgia'),
    path('exames/', views.exames, name='exames'),
    path('odontologia/', views.odontologia, name='odontologia'),
    path('oftalmologia/', views.oftalmologia, name='oftalmologia'),
    path('tomografia/', views.tomografia, name='tomografia'),
    path('encontre/', views.nos_encontre, name='encontre'),
    path('consulta/', views.consulta, name='consulta'),
    path('agenda/', views.agenda, name='agenda'),
    path('checkup_consulta/', views.checkup_consulta, name='checkup_consulta'),
    path('checkup_tratamento/', views.checkup_tratamento, name='checkup_tratamento'),
    path('politicas-de-uso/', views.politicas_de_uso, name='politicas-de-uso'),
    path('profissionais/', views.profissionais, name='profissionais'),
    path('profissional/<slug:slug>/', views.profissional_detalhe, name='profissional_detalhe'),
    path('especialidade/<int:especialidade_id>/', views.profissionais_por_especialidade, name='profissionais_especialidade'),
    path('privacidade/', views.privacidade, name='privacidade'),

    # URLs de Autenticação
    path("cadastrar_usuario/", views.cadastrar_usuario, name="cadastro"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # URLs dos Painéis
    path("painel/", views.painel, name="painel"),
    path("painel/medico/", views.painel_medico, name="painel_medico"),
    path("painel/paciente/", views.painel_paciente, name="painel_paciente"),
    path("painel/atendente/", views.painel_atendente, name="painel_atendente"),
    path('ajax/horarios_disponiveis/', views.get_horarios_disponiveis_ajax, name='horarios_disponiveis_ajax'),

    # URLs de Ações
    path("consulta/<int:consulta_id>/relatorio/", views.escrever_relatorio, name="escrever_relatorio"),
    
    path('medicamentos/', views.lista_medicamentos, name='lista_medicamentos'),
    path('medicamentos/cadastrar/', views.cadastrar_medicamento, name='cadastrar_medicamento'),
    path('medicamentos/<int:medicamento_id>/excluir/', views.excluir_medicamento, name='excluir_medicamento'),
    # URLs do Dashboard Administrativo
    path('dashboard/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/produtos/', views.dashboard_produtos, name='dashboard_produtos'),
    path('dashboard/consultas/', views.dashboard_consultas, name='dashboard_consultas'),
    path('dashboard/ocupacao/', views.dashboard_ocupacao, name='dashboard_ocupacao'),
    path('dashboard/pacientes/', views.dashboard_pacientes, name='dashboard_pacientes'),
    path('dashboard/medicos/', views.dashboard_medicos, name='dashboard_medicos'),
    
    # Ações do Dashboard
    path('dashboard/medicamento/<int:medicamento_id>/editar/', views.editar_medicamento, name='editar_medicamento'),
    path('dashboard/consulta/<int:consulta_id>/cancelar/', views.cancelar_consulta_admin, name='cancelar_consulta_admin'),
    path('dashboard/medico/<int:medico_id>/remover/', views.remover_medico, name='remover_medico'),
    path('dashboard/paciente/<int:paciente_id>/remover/', views.remover_paciente, name='remover_paciente'),

    # URL para Gerenciamento de Cargos
    path('dashboard/usuario/<int:user_id>/cargos/', views.gerenciar_cargos, name='gerenciar_cargos'),
]
