# Instalação e Configuração do Google OAuth

## 📋 Resumo das Alterações

Este projeto foi atualizado para incluir autenticação via Google OAuth usando o **django-allauth**. Agora os usuários podem fazer login e se cadastrar usando suas contas do Google, além do método tradicional com usuário e senha.

## 🔧 Dependências Instaladas

```bash
pip install django-allauth mysqlclient PyJWT cryptography
```

## 📝 Arquivos Modificados

### 1. `cadastro_pessoas/settings.py`
- Adicionado `django.contrib.sites` e apps do `allauth` em `INSTALLED_APPS`
- Adicionado middleware `AccountMiddleware`
- Configurado `AUTHENTICATION_BACKENDS` para suportar OAuth
- Adicionadas credenciais do Google OAuth
- Configurações de redirecionamento e autenticação

### 2. `cadastro_pessoas/urls.py`
- Adicionada rota `path('accounts/', include('allauth.urls'))`

### 3. `pessoas/signals.py` (NOVO)
- Signal para criar perfil de paciente automaticamente ao registrar com Google
- Signal para vincular conta Google a usuário existente com mesmo email

### 4. `pessoas/apps.py`
- Adicionado método `ready()` para carregar signals

### 5. `pessoas/templates/pessoas/login.html`
- Adicionado botão "Entrar com Google"
- Mantido formulário de login tradicional

### 6. `pessoas/templates/pessoas/cadastrar_usuario.html`
- Adicionado botão "Cadastrar com Google"
- Mantido formulário de cadastro tradicional

## 🚀 Como Executar

### Passo 1: Configurar o Banco de Dados MySQL

Certifique-se de que o MySQL está rodando e crie o banco de dados:

```sql
CREATE DATABASE sistema_consultas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Passo 2: Executar Migrações

```bash
cd /home/ubuntu/projeto_cimed
python3.11 manage.py migrate
```

### Passo 3: Criar Superusuário (Opcional)

```bash
python3.11 manage.py createsuperuser
```

### Passo 4: Configurar o Google OAuth no Admin

1. Inicie o servidor:
```bash
python3.11 manage.py runserver 0.0.0.0:8000
```

2. Acesse o admin: `http://localhost:8000/admin/`

3. Vá em **Sites** e edite o site existente:
   - Domain name: `localhost:8000` (ou seu domínio)
   - Display name: `Sistema de Consultas`

4. Vá em **Social applications** e adicione um novo:
   - Provider: **Google**
   - Name: `Google OAuth`
   - Client id: GOOGLE_CLIENT_ID
   - Secret key: GOOGLE_CLIENT_SECRET
   - Sites: Selecione o site criado no passo 3

### Passo 5: Configurar URLs Autorizadas no Google Cloud Console

Acesse o [Google Cloud Console](https://console.cloud.google.com/) e configure:

**URIs de redirecionamento autorizados:**
```
http://localhost:8000/accounts/google/login/callback/
http://127.0.0.1:8000/accounts/google/login/callback/
```

**Origens JavaScript autorizadas:**
```
http://localhost:8000
http://127.0.0.1:8000
```

## 🔐 Credenciais do Google OAuth

**Client ID:**
```
GOOGLE_CLIENT_ID
```

**Client Secret:**
```
GOOGLE_CLIENT_SECRET
```

## 📊 Fluxo de Autenticação

### Login com Google:
1. Usuário clica em "Entrar com Google"
2. É redirecionado para página de login do Google
3. Após autorização, retorna ao sistema
4. Se é primeira vez: cria usuário + perfil de paciente
5. Se email já existe: vincula conta Google ao usuário existente
6. Redireciona para o painel apropriado

### Criação Automática de Perfil:
- Todo usuário criado via Google recebe automaticamente um perfil de **paciente**
- Se necessário alterar para médico ou atendente, deve ser feito pelo admin

## 🗄️ Estrutura do Banco de Dados

O sistema usa as tabelas padrão do Django + allauth:

- `auth_user` - Usuários do sistema
- `pessoas_perfil` - Perfis (médico/paciente/atendente)
- `socialaccount_socialaccount` - Contas sociais vinculadas
- `socialaccount_socialapp` - Aplicações sociais configuradas
- `socialaccount_socialtoken` - Tokens de acesso OAuth

## ⚠️ Observações Importantes

1. **Banco de Dados**: O sistema está configurado para MySQL. Certifique-se de que as credenciais em `settings.py` estão corretas:
   - Database: `sistema_consultas`
   - User: `root`
   - Password: `Gerc1943`
   - Host: `127.0.0.1`
   - Port: `3306`

2. **Produção**: Para ambiente de produção:
   - Altere `DEBUG = False`
   - Configure `ALLOWED_HOSTS`
   - Use HTTPS
   - Atualize URLs de callback no Google Console

3. **Segurança**: As credenciais do Google estão hardcoded no `settings.py`. Para produção, use variáveis de ambiente:
```python
import os
'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
'secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
```

## 🧪 Testando

1. Acesse `http://localhost:8000/login/`
2. Clique em "Entrar com Google"
3. Faça login com sua conta Google
4. Verifique se foi redirecionado para o painel de paciente
5. Verifique no admin se o usuário e perfil foram criados

## 📞 Suporte

Se encontrar problemas:
1. Verifique se o MySQL está rodando
2. Verifique se as migrações foram executadas
3. Verifique se as credenciais do Google estão corretas no admin
4. Verifique os logs do Django para erros específicos
