-- ==========================================
-- SIMED - Script de Criação do Banco de Dados PostgreSQL
-- ==========================================
-- Este script cria todas as tabelas necessárias para o sistema SIMED
-- Execute este script em um banco PostgreSQL limpo
-- ==========================================

-- Habilitar extensão para UUIDs (opcional)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- TABELAS DO DJANGO AUTH
-- ==========================================

-- Tabela de usuários (Django Auth)
CREATE TABLE IF NOT EXISTS auth_user (
    id SERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) NOT NULL DEFAULT '',
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de grupos
CREATE TABLE IF NOT EXISTS auth_group (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE
);

-- Tabela de permissões
CREATE TABLE IF NOT EXISTS auth_permission (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content_type_id INTEGER NOT NULL,
    codename VARCHAR(100) NOT NULL
);

-- Tabela de relação usuário-grupo
CREATE TABLE IF NOT EXISTS auth_user_groups (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    group_id INTEGER NOT NULL REFERENCES auth_group(id) ON DELETE CASCADE,
    UNIQUE(user_id, group_id)
);

-- Tabela de relação usuário-permissão
CREATE TABLE IF NOT EXISTS auth_user_user_permissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES auth_permission(id) ON DELETE CASCADE,
    UNIQUE(user_id, permission_id)
);

-- ==========================================
-- TABELAS DO DJANGO CONTRIB
-- ==========================================

-- Content Types
CREATE TABLE IF NOT EXISTS django_content_type (
    id SERIAL PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    UNIQUE(app_label, model)
);

-- Sessions
CREATE TABLE IF NOT EXISTS django_session (
    session_key VARCHAR(40) PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX IF NOT EXISTS django_session_expire_date_idx ON django_session(expire_date);

-- Sites (para django-allauth)
CREATE TABLE IF NOT EXISTS django_site (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL
);

-- Inserir site padrão
INSERT INTO django_site (id, domain, name) VALUES (1, 'localhost', 'SIMED') ON CONFLICT (id) DO NOTHING;

-- ==========================================
-- TABELAS DO APP PESSOAS
-- ==========================================

-- Tabela de Perfis de Usuário
CREATE TABLE IF NOT EXISTS pessoas_perfil (
    id SERIAL PRIMARY KEY,
    tipo_usuario VARCHAR(10) NOT NULL CHECK (tipo_usuario IN ('medico', 'paciente', 'atendente')),
    data_nascimento DATE,
    rg VARCHAR(20),
    endereco VARCHAR(255),
    telefone VARCHAR(20),
    usuario_id INTEGER NOT NULL UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE
);

COMMENT ON TABLE pessoas_perfil IS 'Perfis de usuário com tipo (médico, paciente, atendente) e dados adicionais';

-- Tabela de Especialidades
CREATE TABLE IF NOT EXISTS pessoas_especialidade (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    icone VARCHAR(50) NOT NULL DEFAULT 'fa-stethoscope'
);

COMMENT ON TABLE pessoas_especialidade IS 'Especialidades médicas disponíveis na clínica';

-- Inserir especialidades padrão
INSERT INTO pessoas_especialidade (nome, descricao, icone) VALUES
    ('Clínica Geral', 'Atendimento médico geral e preventivo', 'fa-user-md'),
    ('Cardiologia', 'Especialidade do coração e sistema cardiovascular', 'fa-heartbeat'),
    ('Dermatologia', 'Tratamento de pele, cabelos e unhas', 'fa-hand-paper'),
    ('Oftalmologia', 'Cuidados com a visão e olhos', 'fa-eye'),
    ('Ortopedia', 'Tratamento do sistema músculo-esquelético', 'fa-bone'),
    ('Pediatria', 'Atendimento médico infantil', 'fa-baby'),
    ('Ginecologia', 'Saúde da mulher', 'fa-venus'),
    ('Neurologia', 'Tratamento do sistema nervoso', 'fa-brain'),
    ('Odontologia', 'Saúde bucal e dental', 'fa-tooth'),
    ('Psiquiatria', 'Saúde mental e emocional', 'fa-brain')
ON CONFLICT (nome) DO NOTHING;

-- Tabela de Profissionais
CREATE TABLE IF NOT EXISTS pessoas_profissional (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    crm VARCHAR(20),
    foto VARCHAR(100),
    biografia TEXT,
    formacao TEXT,
    certificacoes TEXT,
    objetivos TEXT,
    telefone VARCHAR(20),
    email VARCHAR(254),
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    destaque BOOLEAN NOT NULL DEFAULT FALSE,
    slug VARCHAR(50) UNIQUE,
    especialidade_id INTEGER REFERENCES pessoas_especialidade(id) ON DELETE SET NULL,
    usuario_id INTEGER UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE
);

COMMENT ON TABLE pessoas_profissional IS 'Profissionais de saúde da clínica';

-- Tabela de Consultas
CREATE TABLE IF NOT EXISTS pessoas_consulta (
    id SERIAL PRIMARY KEY,
    data_hora TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(15) NOT NULL DEFAULT 'agendada' CHECK (status IN ('agendada', 'confirmada', 'concluida', 'cancelada')),
    relatorio TEXT,
    observacoes TEXT,
    criado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    medico_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    paciente_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    profissional_id INTEGER REFERENCES pessoas_profissional(id) ON DELETE SET NULL
);

COMMENT ON TABLE pessoas_consulta IS 'Consultas médicas agendadas';

CREATE INDEX IF NOT EXISTS pessoas_consulta_data_hora_idx ON pessoas_consulta(data_hora DESC);
CREATE INDEX IF NOT EXISTS pessoas_consulta_status_idx ON pessoas_consulta(status);

-- Tabela de Medicamentos
CREATE TABLE IF NOT EXISTS pessoas_medicamento (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL UNIQUE,
    principio_ativo VARCHAR(200),
    foto VARCHAR(100),
    valor DECIMAL(10, 2) NOT NULL CHECK (valor > 0),
    necessita_receita BOOLEAN NOT NULL DEFAULT TRUE,
    descricao TEXT,
    estoque INTEGER NOT NULL DEFAULT 0 CHECK (estoque >= 0)
);

COMMENT ON TABLE pessoas_medicamento IS 'Catálogo de medicamentos da farmácia';

CREATE INDEX IF NOT EXISTS pessoas_medicamento_nome_idx ON pessoas_medicamento(nome);

-- ==========================================
-- TABELAS DO DJANGO-ALLAUTH (OAuth)
-- ==========================================

-- Social Account App
CREATE TABLE IF NOT EXISTS socialaccount_socialapp (
    id SERIAL PRIMARY KEY,
    provider VARCHAR(30) NOT NULL,
    name VARCHAR(40) NOT NULL,
    client_id VARCHAR(191) NOT NULL,
    secret VARCHAR(191) NOT NULL,
    key VARCHAR(191) NOT NULL DEFAULT '',
    provider_id VARCHAR(200) NOT NULL DEFAULT '',
    settings JSONB NOT NULL DEFAULT '{}'
);

-- Social Account App Sites
CREATE TABLE IF NOT EXISTS socialaccount_socialapp_sites (
    id SERIAL PRIMARY KEY,
    socialapp_id INTEGER NOT NULL REFERENCES socialaccount_socialapp(id) ON DELETE CASCADE,
    site_id INTEGER NOT NULL REFERENCES django_site(id) ON DELETE CASCADE,
    UNIQUE(socialapp_id, site_id)
);

-- Social Account
CREATE TABLE IF NOT EXISTS socialaccount_socialaccount (
    id SERIAL PRIMARY KEY,
    provider VARCHAR(200) NOT NULL,
    uid VARCHAR(191) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    extra_data JSONB NOT NULL DEFAULT '{}',
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    UNIQUE(provider, uid)
);

-- Social Account Token
CREATE TABLE IF NOT EXISTS socialaccount_socialtoken (
    id SERIAL PRIMARY KEY,
    token TEXT NOT NULL,
    token_secret TEXT NOT NULL DEFAULT '',
    expires_at TIMESTAMP WITH TIME ZONE,
    account_id INTEGER NOT NULL REFERENCES socialaccount_socialaccount(id) ON DELETE CASCADE,
    app_id INTEGER REFERENCES socialaccount_socialapp(id) ON DELETE CASCADE
);

-- Email Address (allauth)
CREATE TABLE IF NOT EXISTS account_emailaddress (
    id SERIAL PRIMARY KEY,
    email VARCHAR(254) NOT NULL,
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    "primary" BOOLEAN NOT NULL DEFAULT FALSE,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS account_emailaddress_email_idx ON account_emailaddress(email);
CREATE UNIQUE INDEX IF NOT EXISTS account_emailaddress_user_primary_idx ON account_emailaddress(user_id) WHERE "primary" = TRUE;

-- Email Confirmation
CREATE TABLE IF NOT EXISTS account_emailconfirmation (
    id SERIAL PRIMARY KEY,
    created TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sent TIMESTAMP WITH TIME ZONE,
    key VARCHAR(64) NOT NULL UNIQUE,
    email_address_id INTEGER NOT NULL REFERENCES account_emailaddress(id) ON DELETE CASCADE
);

-- ==========================================
-- TABELAS DE ADMINISTRAÇÃO
-- ==========================================

-- Admin Log
CREATE TABLE IF NOT EXISTS django_admin_log (
    id SERIAL PRIMARY KEY,
    action_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    object_id TEXT,
    object_repr VARCHAR(200) NOT NULL,
    action_flag SMALLINT NOT NULL CHECK (action_flag >= 0),
    change_message TEXT NOT NULL DEFAULT '',
    content_type_id INTEGER REFERENCES django_content_type(id) ON DELETE SET NULL,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE
);

-- ==========================================
-- MIGRAÇÕES DO DJANGO
-- ==========================================

CREATE TABLE IF NOT EXISTS django_migrations (
    id SERIAL PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- ÍNDICES ADICIONAIS PARA PERFORMANCE
-- ==========================================

CREATE INDEX IF NOT EXISTS pessoas_perfil_tipo_idx ON pessoas_perfil(tipo_usuario);
CREATE INDEX IF NOT EXISTS pessoas_profissional_ativo_idx ON pessoas_profissional(ativo);
CREATE INDEX IF NOT EXISTS pessoas_profissional_destaque_idx ON pessoas_profissional(destaque);

-- ==========================================
-- FIM DO SCRIPT
-- ==========================================
