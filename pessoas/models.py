# pessoas/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Perfil(models.Model):
    """
    Modelo para estender o User padrão com o tipo de perfil
    Hierarquia: Admin > Médico > Atendente > Paciente
    """
    TIPOS_USUARIO = (
        ('admin', 'Administrador'),
        ('medico', 'Médico'),
        ('atendente', 'Atendente'),
        ('paciente', 'Paciente'),
    )
    
    ROLE_HIERARCHY = {
        'admin': 4,
        'medico': 3,
        'atendente': 2,
        'paciente': 1,
    }
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_usuario = models.CharField(max_length=10, choices=TIPOS_USUARIO, default='paciente')
    data_nascimento = models.DateField(null=True, blank=True)
    rg = models.CharField(max_length=20, null=True, blank=True)
    endereco = models.CharField(max_length=255, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f'{self.usuario.username} - {self.get_tipo_usuario_display()}'
    
    @property
    def role_level(self):
        return self.ROLE_HIERARCHY.get(self.tipo_usuario, 0)
    
    def is_admin(self):
        return self.tipo_usuario == 'admin' or self.usuario.is_staff or self.usuario.is_superuser
    
    def is_medico(self):
        return self.tipo_usuario in ['admin', 'medico'] or self.usuario.is_staff
    
    def is_atendente(self):
        return self.tipo_usuario in ['admin', 'medico', 'atendente'] or self.usuario.is_staff
    
    def has_min_role(self, min_role):
        required_level = self.ROLE_HIERARCHY.get(min_role, 0)
        return self.role_level >= required_level or self.usuario.is_staff

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'


class Especialidade(models.Model):
    """
    Modelo para categorias de especialidades médicas
    """
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    icone = models.CharField(max_length=50, default='fa-stethoscope', help_text='Classe do ícone FontAwesome')

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Especialidade'
        verbose_name_plural = 'Especialidades'
        ordering = ['nome']


class Profissional(models.Model):
    """
    Modelo para profissionais de saúde com informações detalhadas
    """
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nome = models.CharField(max_length=200)
    especialidade = models.ForeignKey(Especialidade, on_delete=models.SET_NULL, null=True, blank=True)
    crm = models.CharField(max_length=20, blank=True, null=True, verbose_name='CRM/CRO')
    foto = models.ImageField(upload_to='profissionais/', blank=True, null=True)
    biografia = models.TextField(blank=True, null=True, help_text='Descrição do profissional')
    formacao = models.TextField(blank=True, null=True, help_text='Formação acadêmica')
    certificacoes = models.TextField(blank=True, null=True, help_text='Certificações e especializações')
    objetivos = models.TextField(blank=True, null=True, help_text='Objetivos e filosofia de trabalho')
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    destaque = models.BooleanField(default=False, help_text='Mostrar na página principal')
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        especialidade_nome = self.especialidade.nome if self.especialidade else 'Sem especialidade'
        return f'{self.nome} - {especialidade_nome}'

    class Meta:
        verbose_name = 'Profissional'
        verbose_name_plural = 'Profissionais'
        ordering = ['nome']


class Consulta(models.Model):
    """
    Modelo para armazenar as consultas agendadas
    """
    STATUS_CHOICES = (
        ('agendada', 'Agendada'),
        ('confirmada', 'Confirmada'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    )
    paciente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultas_como_paciente')
    medico = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultas_como_medico')
    profissional = models.ForeignKey(Profissional, on_delete=models.SET_NULL, null=True, blank=True)
    data_hora = models.DateTimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='agendada')
    relatorio = models.TextField(blank=True, null=True, help_text='Relatório a ser preenchido pelo médico após a consulta.')
    observacoes = models.TextField(blank=True, null=True, help_text='Observações do paciente')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Consulta de {self.paciente.username} com Dr(a). {self.medico.last_name} em {self.data_hora.strftime("%d/%m/%Y %H:%M")}'

    class Meta:
        ordering = ['-data_hora']
        verbose_name = 'Consulta'
        verbose_name_plural = 'Consultas'


class Medicamento(models.Model):
    """
    Este modelo armazena o cadastro de medicamentos da clínica.
    """
    nome = models.CharField(
        max_length=200, 
        unique=True, 
        help_text='Nome comercial do medicamento.'
    )
    principio_ativo = models.CharField(max_length=200, blank=True, null=True)
    foto = models.ImageField(
        upload_to='medicamentos/', 
        blank=True, 
        null=True, 
        help_text='Foto da embalagem do medicamento.'
    )
    valor = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        help_text='Preço do medicamento em R$.'
    )
    necessita_receita = models.BooleanField(
        default=True, 
        help_text='Marque esta opção se o medicamento exige receita médica.'
    )
    descricao = models.TextField(blank=True, null=True)
    estoque = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ['nome']
        verbose_name = 'Medicamento'
        verbose_name_plural = 'Medicamentos'
