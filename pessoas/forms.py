# pessoas/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Medicamento, Perfil, Consulta
from django.contrib.auth import authenticate
from datetime import time, datetime, timedelta
from django.utils import timezone

def gerar_todos_horarios_possiveis():
    """Gera uma lista de todos os horários de 15 em 15 minutos entre 08:00 e 17:45."""
    horarios = [('', '---------')]
    hora_inicio = datetime.strptime("08:00", "%H:%M").time()
    hora_fim = datetime.strptime("18:00", "%H:%M").time()
    intervalo = timedelta(minutes=15)

    current_time = datetime.combine(datetime.min, hora_inicio)
    while current_time.time() < hora_fim:
        hora = current_time.time()
        horarios.append((hora.isoformat(timespec='minutes'), hora.strftime("%H:%M")))
        current_time += intervalo
    return horarios

class LoginUsuarioForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Usuário',
            'class': 'form-control',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Senha',
            'class': 'form-control',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Nome de usuário ou senha incorretos.")
            cleaned_data['user'] = user
        return cleaned_data

# Formulário para um novo usuário se cadastrar
class CadastroUsuarioForm(forms.ModelForm):

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nome',
            'class': 'form-control',
        })
    )

    # first_name = forms.CharField(
    #     max_length=150,
    #     required=True,
    #     widget=forms.TextInput(attrs={
    #         'placeholder': 'Nome',
    #         'class': 'form-control',
    #     })
    # )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Sobrenome',
            'class': 'form-control',
        })
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'E-mail',
            'class': 'form-control',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Senha',
            'class': 'form-control',
        })
    )

    class Meta:
        model = User
        fields = ["username", "last_name", "email", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

    # --- INÍCIO DA ALTERAÇÃO ---
    # --- FIM DA ALTERAÇÃO ---

    # Precisamos salvar o Perfil junto com o User
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            # O Perfil será criado separadamente ou atualizado
        return user

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ["data_nascimento", "rg", "endereco"]
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }

# Formulário para agendar uma nova consulta (para o paciente)
class AgendarConsultaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['hora'].choices = gerar_todos_horarios_possiveis()

    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get('data')
        hora_str = cleaned_data.get('hora')
        medico = cleaned_data.get('medico')

        if data and hora_str and medico:
            # Combina data e hora
            try:
                hora = time.fromisoformat(hora_str)
                data_hora = timezone.make_aware(datetime.combine(data, hora))
            except ValueError:
                raise forms.ValidationError("Formato de hora inválido.")

            # 1. Restrição de horário de funcionamento (8h às 18h)
            if not (time(8, 0) <= hora < time(18, 0)):
                raise forms.ValidationError("O horário de agendamento deve ser entre 08:00 e 18:00.")

            # 2. Espaçamento mínimo de 15 minutos (já garantido pela geração de choices, mas bom ter)
            if hora.minute % 15 != 0:
                raise forms.ValidationError("O agendamento deve ser feito em intervalos de 15 minutos.")

            # 3. Verifica se o horário está ocupado (redundante se a lista for gerada corretamente, mas é uma segurança)
            consulta_existente = Consulta.objects.filter(
                medico=medico,
                data_hora=data_hora,
                status='agendada'
            ).exists()

            if consulta_existente:
                raise forms.ValidationError("Este horário já está ocupado. Por favor, escolha outro.")

            # Adiciona o campo data_hora completo para ser usado na view
            cleaned_data['data_hora'] = data_hora

        return cleaned_data
    # O campo "medico" será um dropdown com todos os usuários que são médicos
    medico = forms.ModelChoiceField(queryset=User.objects.filter(perfil__tipo_usuario="medico"))
    data = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    hora = forms.ChoiceField(choices=[]) # Será preenchido dinamicamente na view

    class Meta:
        model = Consulta
        fields = ["medico", "data", "hora"]

# Formulário para agendar uma nova consulta (para o atendente)
class AgendarConsultaAtendenteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['hora'].choices = gerar_todos_horarios_possiveis()

    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get('data')
        hora_str = cleaned_data.get('hora')
        medico = cleaned_data.get('medico')

        if data and hora_str and medico:
            # Combina data e hora
            try:
                hora = time.fromisoformat(hora_str)
                data_hora = timezone.make_aware(datetime.combine(data, hora))
            except ValueError:
                raise forms.ValidationError("Formato de hora inválido.")

            # 1. Restrição de horário de funcionamento (8h às 18h)
            if not (time(8, 0) <= hora < time(18, 0)):
                raise forms.ValidationError("O horário de agendamento deve ser entre 08:00 e 18:00.")

            # 2. Espaçamento mínimo de 15 minutos (já garantido pela geração de choices, mas bom ter)
            if hora.minute % 15 != 0:
                raise forms.ValidationError("O agendamento deve ser feito em intervalos de 15 minutos.")

            # 3. Verifica se o horário está ocupado (redundante se a lista for gerada corretamente, mas é uma segurança)
            consulta_existente = Consulta.objects.filter(
                medico=medico,
                data_hora=data_hora,
                status='agendada'
            ).exists()

            if consulta_existente:
                raise forms.ValidationError("Este horário já está ocupado. Por favor, escolha outro.")

            # Adiciona o campo data_hora completo para ser usado na view
            cleaned_data['data_hora'] = data_hora

        return cleaned_data
    # O atendente precisa selecionar o paciente
    paciente = forms.ModelChoiceField(
        queryset=User.objects.filter(perfil__tipo_usuario="paciente"),
        label="Paciente"
    )
    # O atendente precisa selecionar o médico
    medico = forms.ModelChoiceField(
        queryset=User.objects.filter(perfil__tipo_usuario="medico"),
        label="Médico"
    )
    data = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Data"
    )
    hora = forms.ChoiceField(
        choices=[], # Será preenchido dinamicamente na view
        label="Hora"
    )

    class Meta:
        model = Consulta
        fields = ["paciente", "medico", "data", "hora"]

# Formulário para o médico escrever o relatório
class RelatorioConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ["relatorio"]
        widgets = {
            "relatorio": forms.Textarea(attrs={"rows": 5}),
        }
class MedicamentoForm(forms.ModelForm):
    class Meta:
        model = Medicamento
        # Lista dos campos do modelo que devem aparecer no formulário
        fields = ['nome', 'foto', 'valor', 'necessita_receita']
        
        # Opcional: Adicionar classes do Bootstrap para estilização
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control'}),
            'necessita_receita': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
