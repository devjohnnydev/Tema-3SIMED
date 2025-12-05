# 🚀 Guia Rápido - Google OAuth Implementado

## ✅ O que foi implementado?

### 1. **Autenticação com Google**
- Botão "Entrar com Google" na página de login
- Botão "Cadastrar com Google" na página de cadastro
- Login automático após autorização do Google
- Criação automática de perfil de paciente

### 2. **Integração com MySQL**
- Todas as contas Google são salvas no banco de dados MySQL
- Tabelas do django-allauth integradas ao banco existente
- Perfis criados automaticamente para novos usuários

### 3. **Vinculação de Contas**
- Se um usuário já existe com o mesmo email, a conta Google é vinculada automaticamente
- Usuários podem ter login tradicional E Google simultaneamente

## 📦 Arquivos Criados/Modificados

### Novos Arquivos:
- `pessoas/signals.py` - Lógica de criação automática de perfil
- `INSTALACAO_GOOGLE_OAUTH.md` - Documentação completa
- `GUIA_RAPIDO.md` - Este arquivo
- `setup_oauth.sh` - Script de instalação automatizada
- `requirements.txt` - Dependências do projeto

### Arquivos Modificados:
- `cadastro_pessoas/settings.py` - Configurações do allauth
- `cadastro_pessoas/urls.py` - Rotas do allauth
- `pessoas/apps.py` - Registro de signals
- `pessoas/templates/pessoas/login.html` - Botão Google
- `pessoas/templates/pessoas/cadastrar_usuario.html` - Botão Google

## 🔧 Como Instalar (Passo a Passo)

### 1. Extrair o projeto
```bash
unzip projeto_cimed_com_google_oauth.zip
cd projeto_cimed
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

Ou use o script automatizado:
```bash
./setup_oauth.sh
```

### 3. Configurar banco de dados
Certifique-se de que o MySQL está rodando e execute:
```bash
python3.11 manage.py migrate
```

### 4. Criar superusuário
```bash
python3.11 manage.py createsuperuser
```

### 5. Iniciar servidor
```bash
python3.11 manage.py runserver 0.0.0.0:8000
```

### 6. Configurar no Admin

Acesse: `http://localhost:8000/admin/`

#### 6.1. Configurar Site
1. Vá em **Sites**
2. Edite o site existente (example.com)
3. Altere para:
   - **Domain name**: `localhost:8000`
   - **Display name**: `Sistema de Consultas`
4. Salve

#### 6.2. Adicionar Social Application
1. Vá em **Social applications**
2. Clique em **Add social application**
3. Preencha:
   - **Provider**: Google
   - **Name**: Google OAuth
   - **Client id**: GOOGLE_CLIENT_ID
   - **Secret key**: GOOGLE_CLIENT_SECRET
   - **Sites**: Selecione "localhost:8000"
4. Salve

### 7. Configurar Google Cloud Console

Acesse: https://console.cloud.google.com/

1. Vá em **APIs & Services** > **Credentials**
2. Selecione o OAuth 2.0 Client ID correspondente
3. Em **Authorized redirect URIs**, adicione:
   ```
   http://localhost:8000/accounts/google/login/callback/
   http://127.0.0.1:8000/accounts/google/login/callback/
   ```
4. Em **Authorized JavaScript origins**, adicione:
   ```
   http://localhost:8000
   http://127.0.0.1:8000
   ```
5. Salve

## 🧪 Testando

### Teste 1: Login com Google (Novo Usuário)
1. Acesse `http://localhost:8000/login/`
2. Clique em "Entrar com Google"
3. Escolha uma conta Google
4. Autorize o acesso
5. Você deve ser redirecionado para `/painel/`
6. Verifique no admin que o usuário foi criado com perfil de paciente

### Teste 2: Login com Google (Usuário Existente)
1. Crie um usuário manualmente com email `teste@gmail.com`
2. Faça logout
3. Tente fazer login com Google usando `teste@gmail.com`
4. A conta Google deve ser vinculada ao usuário existente

### Teste 3: Login Tradicional
1. O login tradicional deve continuar funcionando normalmente
2. Usuários podem usar ambos os métodos

## 📊 Estrutura do Banco de Dados

### Tabelas Principais:
- `auth_user` - Usuários (criados por qualquer método)
- `pessoas_perfil` - Perfis (médico/paciente/atendente)
- `socialaccount_socialaccount` - Contas sociais vinculadas
- `socialaccount_socialapp` - Apps sociais (Google)
- `socialaccount_socialtoken` - Tokens OAuth

### Relacionamentos:
```
auth_user (1) -----> (1) pessoas_perfil
    |
    |
    v
socialaccount_socialaccount (N)
```

## 🔐 Credenciais do Google

**Client ID:**
```
GOOGLE_CLIENT_ID
```

**Client Secret:**
```
GOOGLE_CLIENT_SECRET
```

## ⚙️ Configurações Importantes

### Em `settings.py`:

```python
# Redirecionamentos
LOGIN_REDIRECT_URL = '/painel/'
LOGOUT_REDIRECT_URL = '/login/'

# Autenticação por email
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False

# Sem verificação de email
ACCOUNT_EMAIL_VERIFICATION = 'none'

# Cadastro automático
SOCIALACCOUNT_AUTO_SIGNUP = True
```

## 🐛 Troubleshooting

### Erro: "Can't connect to MySQL server"
- Verifique se o MySQL está rodando
- Verifique as credenciais em `settings.py`

### Erro: "No module named 'jwt'"
```bash
pip install PyJWT cryptography
```

### Erro: "redirect_uri_mismatch"
- Verifique se as URLs no Google Console estão corretas
- Use exatamente: `http://localhost:8000/accounts/google/login/callback/`

### Botão Google não aparece
- Verifique se `{% load socialaccount %}` está no topo do template
- Verifique se o app está configurado no admin

### Usuário não tem perfil
- O signal deve criar automaticamente
- Verifique se `pessoas/apps.py` tem o método `ready()`
- Crie manualmente no admin se necessário

## 📝 Notas Importantes

1. **Perfil Padrão**: Todos os usuários criados via Google recebem perfil de **paciente**
2. **Alteração de Perfil**: Para tornar um usuário médico ou atendente, edite no admin
3. **Produção**: Para produção, use HTTPS e atualize as URLs no Google Console
4. **Segurança**: Em produção, use variáveis de ambiente para as credenciais

## 🎯 Próximos Passos

1. Testar em ambiente de produção com HTTPS
2. Adicionar mais provedores OAuth (Facebook, Microsoft, etc.)
3. Implementar escolha de tipo de perfil no primeiro login
4. Adicionar foto do perfil do Google ao sistema

## 📞 Suporte

Se tiver problemas:
1. Leia `INSTALACAO_GOOGLE_OAUTH.md` para detalhes completos
2. Verifique os logs do Django: `python3.11 manage.py runserver`
3. Verifique o console do navegador para erros JavaScript
4. Verifique se todas as migrações foram aplicadas: `python3.11 manage.py showmigrations`
