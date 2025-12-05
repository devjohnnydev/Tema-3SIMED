from django.apps import AppConfig


class PessoasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pessoas'
    
    def ready(self):
        import pessoas.signals  # Importa os signals quando o app é carregado
