# SIMED - Guia Completo de Deploy no Railway

## Indice

1. [Visao Geral](#visao-geral)
2. [Pre-requisitos](#pre-requisitos)
3. [Passo 1: Criar Conta no Railway](#passo-1-criar-conta-no-railway)
4. [Passo 2: Criar Novo Projeto](#passo-2-criar-novo-projeto)
5. [Passo 3: Configurar Banco de Dados PostgreSQL](#passo-3-configurar-banco-de-dados-postgresql)
6. [Passo 4: Configurar Variaveis de Ambiente](#passo-4-configurar-variaveis-de-ambiente)
7. [Passo 5: Deploy da Aplicacao](#passo-5-deploy-da-aplicacao)
8. [Passo 6: Executar Migracoes](#passo-6-executar-migracoes)
9. [Passo 7: Criar Superusuario](#passo-7-criar-superusuario)
10. [Passo 8: Configurar Dominio Personalizado](#passo-8-configurar-dominio-personalizado)
11. [Passo 9: Configurar Google OAuth (Opcional)](#passo-9-configurar-google-oauth-opcional)
12. [Solucao de Problemas](#solucao-de-problemas)
13. [Manutencao e Atualizacoes](#manutencao-e-atualizacoes)

---

## Visao Geral

Este guia detalha o processo completo de deploy do sistema SIMED (Servico Integrado de Medicina) na plataforma Railway. O Railway e uma plataforma de hospedagem moderna que oferece:

- Deploy automatico via GitHub
- Banco de dados PostgreSQL gerenciado
- SSL automatico
- Escalabilidade facil
- Interface intuitiva

**Arquitetura do Sistema:**
```
                    +------------------+
                    |    Railway       |
                    |    (Frontend)    |
                    +--------+---------+
                             |
                    +--------v---------+
                    |  Django Server   |
                    |   (Gunicorn)     |
                    +--------+---------+
                             |
                    +--------v---------+
                    |   PostgreSQL     |
                    |    Database      |
                    +------------------+
```

---

## Pre-requisitos

Antes de comecar, certifique-se de ter:

1. **Conta no GitHub** - O codigo deve estar em um repositorio
2. **Conta no Railway** - Cadastro gratuito em [railway.app](https://railway.app)
3. **Codigo do SIMED** - Clone ou fork do repositorio

### Estrutura de Arquivos Necessarios

```
simed/
├── cadastro_pessoas/          # Configuracoes Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── pessoas/                   # App principal
│   ├── models.py
│   ├── views.py
│   └── templates/
├── scripts/                   # Scripts utilitarios
│   └── database_schema_railway.sql
├── manage.py
├── requirements.txt           # Dependencias Python
├── Procfile                   # Comando de inicializacao
├── runtime.txt               # Versao do Python
└── railway.json              # Configuracao Railway
```

---

## Passo 1: Criar Conta no Railway

1. Acesse [railway.app](https://railway.app)
2. Clique em **"Start a New Project"**
3. Faca login com sua conta GitHub
4. Autorize o Railway a acessar seus repositorios

---

## Passo 2: Criar Novo Projeto

### 2.1 Criar Projeto via GitHub

1. No dashboard do Railway, clique em **"New Project"**
2. Selecione **"Deploy from GitHub repo"**
3. Escolha o repositorio do SIMED
4. Selecione a branch `main` ou `master`

### 2.2 Configuracao Automatica

O Railway detectara automaticamente:
- Tipo de aplicacao: Python/Django
- Arquivo Procfile para inicializacao
- requirements.txt para dependencias

---

## Passo 3: Configurar Banco de Dados PostgreSQL

### 3.1 Adicionar PostgreSQL ao Projeto

1. No painel do projeto, clique em **"+ New"**
2. Selecione **"Database"**
3. Escolha **"PostgreSQL"**
4. Aguarde a criacao (leva alguns segundos)

### 3.2 Obter Credenciais do Banco

1. Clique no servico PostgreSQL criado
2. Va na aba **"Variables"**
3. Copie as seguintes variaveis:
   - `DATABASE_URL`
   - `PGHOST`
   - `PGDATABASE`
   - `PGUSER`
   - `PGPASSWORD`
   - `PGPORT`

### 3.3 Sobre o Script SQL (Referencia)

O arquivo `scripts/database_schema_railway.sql` contem o schema completo do banco de dados exportado diretamente do PostgreSQL.

**IMPORTANTE:** Este script e apenas para REFERENCIA. O metodo correto para criar as tabelas e atraves das migracoes do Django:

```bash
railway run python manage.py migrate
```

As migracoes do Django sao a fonte de verdade (source of truth) para o schema do banco de dados. O script SQL pode ficar desatualizado se novas migracoes forem adicionadas.

**Quando usar o script SQL:**
- Para documentacao e auditoria
- Para criar um banco manualmente sem Django
- Para referencia de estrutura de dados

---

## Passo 4: Configurar Variaveis de Ambiente

### 4.1 Variaveis Obrigatorias

No servico da aplicacao Django, va em **"Variables"** e adicione:

| Variavel | Valor | Descricao |
|----------|-------|-----------|
| `SECRET_KEY` | Gerar chave segura* | Chave secreta do Django |
| `DEBUG` | `False` | Desabilitar modo debug |
| `ALLOWED_HOSTS` | `*.railway.app,.railway.app` | Hosts permitidos |
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` | Referencia ao banco |
| `PGDATABASE` | `${{Postgres.PGDATABASE}}` | Nome do banco |
| `PGHOST` | `${{Postgres.PGHOST}}` | Host do banco |
| `PGUSER` | `${{Postgres.PGUSER}}` | Usuario do banco |
| `PGPASSWORD` | `${{Postgres.PGPASSWORD}}` | Senha do banco |
| `PGPORT` | `${{Postgres.PGPORT}}` | Porta do banco |

*Para gerar uma SECRET_KEY segura, execute no terminal:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 4.2 Variaveis para Google OAuth (Opcional)

| Variavel | Valor | Descricao |
|----------|-------|-----------|
| `GOOGLE_CLIENT_ID` | Seu Client ID | ID do cliente Google |
| `GOOGLE_CLIENT_SECRET` | Seu Client Secret | Segredo do cliente |

### 4.3 Exemplo de Configuracao

```env
SECRET_KEY=sua-chave-secreta-muito-longa-e-segura-aqui
DEBUG=False
ALLOWED_HOSTS=*.railway.app,.railway.app,seudominio.com
DATABASE_URL=${{Postgres.DATABASE_URL}}
PGDATABASE=${{Postgres.PGDATABASE}}
PGHOST=${{Postgres.PGHOST}}
PGUSER=${{Postgres.PGUSER}}
PGPASSWORD=${{Postgres.PGPASSWORD}}
PGPORT=${{Postgres.PGPORT}}
```

---

## Passo 5: Deploy da Aplicacao

### 5.1 Arquivos de Configuracao

**Procfile** (ja incluido no projeto):
```
web: gunicorn cadastro_pessoas.wsgi --bind 0.0.0.0:$PORT
```

**runtime.txt** (ja incluido no projeto):
```
python-3.12.0
```

**railway.json** (ja incluido no projeto):
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt && python manage.py collectstatic --noinput"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && gunicorn cadastro_pessoas.wsgi --bind 0.0.0.0:$PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 5.2 Iniciar Deploy

1. Apos configurar as variaveis, o deploy iniciara automaticamente
2. Acompanhe o progresso em **"Deployments"**
3. Aguarde a mensagem de sucesso

### 5.3 Verificar Logs

Se houver erros:
1. Clique no deploy
2. Verifique a aba **"Logs"**
3. Procure por mensagens de erro

---

## Passo 6: Executar Migracoes

### 6.1 Via Interface do Railway

1. No servico da aplicacao, va em **"Settings"**
2. Em **"Service"**, encontre **"Run Command"**
3. Temporariamente, mude para:
   ```
   python manage.py migrate && gunicorn cadastro_pessoas.wsgi --bind 0.0.0.0:$PORT
   ```
4. Clique em **"Deploy"**

### 6.2 Via Railway CLI

Instale o Railway CLI:
```bash
npm install -g @railway/cli
```

Login:
```bash
railway login
```

Vincule ao projeto:
```bash
railway link
```

Execute as migracoes:
```bash
railway run python manage.py migrate
```

---

## Passo 7: Criar Superusuario

### 7.1 Via Railway CLI

```bash
railway run python manage.py createsuperuser
```

Siga as instrucoes:
- Username: admin
- Email: seu@email.com
- Password: senha-segura

### 7.2 Via Script (Alternativa)

Crie um arquivo `scripts/create_admin.py`:

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cadastro_pessoas.settings')
django.setup()

from django.contrib.auth.models import User
from pessoas.models import Perfil

# Criar superusuario
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser(
        username='admin',
        email='admin@simed.com',
        password='SuaSenhaSegura123!'
    )
    Perfil.objects.create(usuario=user, tipo_usuario='admin')
    print('Superusuario criado com sucesso!')
else:
    print('Superusuario ja existe.')
```

Execute:
```bash
railway run python scripts/create_admin.py
```

---

## Passo 8: Configurar Dominio Personalizado

### 8.1 Gerar Dominio Railway

1. No servico, va em **"Settings"**
2. Em **"Domains"**, clique em **"Generate Domain"**
3. Voce recebera um dominio como: `simed-production.up.railway.app`

### 8.2 Dominio Personalizado

Para usar seu proprio dominio:

1. Em **"Domains"**, clique em **"+ Custom Domain"**
2. Digite seu dominio: `simed.seudominio.com`
3. Configure o DNS do seu dominio:
   - Tipo: CNAME
   - Nome: simed (ou www)
   - Valor: fornecido pelo Railway

### 8.3 Atualizar ALLOWED_HOSTS

Adicione seu dominio nas variaveis:
```
ALLOWED_HOSTS=*.railway.app,.railway.app,simed.seudominio.com
```

### 8.4 Atualizar CSRF_TRUSTED_ORIGINS

No `settings.py`, adicione:
```python
CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',
    'https://*.up.railway.app',
    'https://simed.seudominio.com',  # Seu dominio
]
```

---

## Passo 9: Configurar Google OAuth (Opcional)

### 9.1 Criar Projeto no Google Cloud

1. Acesse [Google Cloud Console](https://console.cloud.google.com)
2. Crie um novo projeto
3. Va em **"APIs & Services"** > **"OAuth consent screen"**
4. Configure:
   - User Type: External
   - App name: SIMED
   - User support email: seu@email.com

### 9.2 Criar Credenciais OAuth

1. Va em **"Credentials"**
2. Clique em **"+ Create Credentials"** > **"OAuth client ID"**
3. Application type: **Web application**
4. Authorized redirect URIs:
   ```
   https://seu-dominio.railway.app/accounts/google/login/callback/
   https://simed.seudominio.com/accounts/google/login/callback/
   ```

### 9.3 Configurar no Railway

Adicione as variaveis:
```
GOOGLE_CLIENT_ID=seu-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=seu-client-secret
```

### 9.4 Configurar no Admin Django

1. Acesse `/admin`
2. Va em **"Sites"** e edite o site para seu dominio
3. Va em **"Social applications"**
4. Adicione um novo:
   - Provider: Google
   - Name: Google
   - Client ID: (do Google Cloud)
   - Secret key: (do Google Cloud)
   - Sites: selecione seu site

---

## Solucao de Problemas

### Erro: "No module named 'django'"

**Causa:** Dependencias nao instaladas

**Solucao:** Verifique o `requirements.txt` e force um novo deploy

### Erro: "relation does not exist"

**Causa:** Migracoes nao executadas

**Solucao:**
```bash
railway run python manage.py migrate
```

### Erro: "CSRF verification failed"

**Causa:** Dominio nao esta em CSRF_TRUSTED_ORIGINS

**Solucao:** Adicione o dominio no settings.py

### Erro: "DisallowedHost"

**Causa:** Host nao esta em ALLOWED_HOSTS

**Solucao:** Atualize a variavel ALLOWED_HOSTS

### Erro: "Static files not found"

**Causa:** collectstatic nao executado

**Solucao:**
```bash
railway run python manage.py collectstatic --noinput
```

### Erro de Conexao com Banco

**Causa:** Variaveis de banco incorretas

**Solucao:** Verifique se as variaveis do PostgreSQL estao corretas

---

## Manutencao e Atualizacoes

### Atualizar Aplicacao

1. Faca commit das alteracoes no GitHub
2. O Railway detectara e fara deploy automatico

### Backup do Banco de Dados

Via Railway CLI:
```bash
railway run pg_dump $DATABASE_URL > backup.sql
```

### Restaurar Backup

```bash
railway run psql $DATABASE_URL < backup.sql
```

### Monitoramento

- Verifique os logs regularmente
- Configure alertas no Railway
- Monitore o uso de recursos

### Escalar a Aplicacao

1. Va em **"Settings"** do servico
2. Ajuste os recursos:
   - CPU
   - Memoria
   - Replicas

---

## Checklist Final de Deploy

- [ ] Conta Railway criada
- [ ] Repositorio GitHub conectado
- [ ] PostgreSQL adicionado ao projeto
- [ ] Variaveis de ambiente configuradas
- [ ] SECRET_KEY gerada e configurada
- [ ] DEBUG definido como False
- [ ] ALLOWED_HOSTS configurado
- [ ] Deploy executado com sucesso
- [ ] Migracoes aplicadas
- [ ] Superusuario criado
- [ ] Dominio configurado
- [ ] SSL funcionando (automatico)
- [ ] Google OAuth configurado (opcional)
- [ ] Teste completo da aplicacao

---

## Suporte

Em caso de problemas:

1. Verifique os logs no Railway
2. Consulte a [documentacao do Railway](https://docs.railway.app)
3. Verifique a [documentacao do Django](https://docs.djangoproject.com)

---

## Custos Estimados

| Servico | Plano Gratuito | Plano Pago |
|---------|---------------|------------|
| App Django | 500h/mes | $5/mes base |
| PostgreSQL | 1GB | $5/mes base |
| Total | Gratis* | ~$10/mes |

*O plano gratuito tem limites de horas e recursos.

---

**Ultima atualizacao:** Dezembro 2024
**Versao do Guia:** 1.0
