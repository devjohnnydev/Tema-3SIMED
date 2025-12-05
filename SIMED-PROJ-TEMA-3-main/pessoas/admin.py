from django.contrib import admin
from .models import Perfil, Consulta, Medicamento, Especialidade, Profissional


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tipo_usuario', 'telefone', 'data_nascimento']
    list_filter = ['tipo_usuario']
    search_fields = ['usuario__username', 'usuario__email', 'telefone']


@admin.register(Especialidade)
class EspecialidadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'icone']
    search_fields = ['nome']


@admin.register(Profissional)
class ProfissionalAdmin(admin.ModelAdmin):
    list_display = ['nome', 'especialidade', 'crm', 'ativo', 'destaque']
    list_filter = ['especialidade', 'ativo', 'destaque']
    search_fields = ['nome', 'crm', 'email']
    prepopulated_fields = {'slug': ('nome',)}
    list_editable = ['ativo', 'destaque']


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'medico', 'data_hora', 'status', 'criado_em']
    list_filter = ['status', 'data_hora']
    search_fields = ['paciente__username', 'medico__username']
    date_hierarchy = 'data_hora'


@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'principio_ativo', 'valor', 'necessita_receita', 'estoque']
    list_filter = ['necessita_receita']
    search_fields = ['nome', 'principio_ativo']
    list_editable = ['valor', 'estoque']
