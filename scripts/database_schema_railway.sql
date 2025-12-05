-- ============================================================
-- SIMED - Sistema Integrado de Medicina
-- Script SQL Completo para PostgreSQL (Railway)
-- Versão: 1.0
-- Data: 2024
-- ============================================================

-- ============================================================
-- PARTE 1: CRIAÇÃO DAS TABELAS DO DJANGO CORE
-- ============================================================

-- Tabela de tipos de conteúdo do Django
CREATE TABLE IF NOT EXISTS "django_content_type" (
    "id" SERIAL PRIMARY KEY,
    "app_label" VARCHAR(100) NOT NULL,
    "model" VARCHAR(100) NOT NULL,
    UNIQUE ("app_label", "model")
);

-- Tabela de migrações do Django
CREATE TABLE IF NOT EXISTS "django_migrations" (
    "id" BIGSERIAL PRIMARY KEY,
    "app" VARCHAR(255) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "applied" TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Tabela de sessões do Django
CREATE TABLE IF NOT EXISTS "django_session" (
    "session_key" VARCHAR(40) PRIMARY KEY,
    "session_data" TEXT NOT NULL,
    "expire_date" TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE INDEX IF NOT EXISTS "django_session_expire_date_idx" ON "django_session" ("expire_date");
CREATE INDEX IF NOT EXISTS "django_session_session_key_like" ON "django_session" ("session_key" varchar_pattern_ops);

-- Tabela de sites do Django
CREATE TABLE IF NOT EXISTS "django_site" (
    "id" SERIAL PRIMARY KEY,
    "domain" VARCHAR(100) NOT NULL UNIQUE,
    "name" VARCHAR(50) NOT NULL
);
CREATE INDEX IF NOT EXISTS "django_site_domain_like" ON "django_site" ("domain" varchar_pattern_ops);

-- ============================================================
-- PARTE 2: TABELAS DE AUTENTICAÇÃO
-- ============================================================

-- Tabela de permissões
CREATE TABLE IF NOT EXISTS "auth_permission" (
    "id" SERIAL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "content_type_id" INTEGER NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "codename" VARCHAR(100) NOT NULL,
    UNIQUE ("content_type_id", "codename")
);
CREATE INDEX IF NOT EXISTS "auth_permission_content_type_id_idx" ON "auth_permission" ("content_type_id");

-- Tabela de grupos
CREATE TABLE IF NOT EXISTS "auth_group" (
    "id" SERIAL PRIMARY KEY,
    "name" VARCHAR(150) NOT NULL UNIQUE
);
CREATE INDEX IF NOT EXISTS "auth_group_name_like" ON "auth_group" ("name" varchar_pattern_ops);

-- Tabela de permissões de grupos
CREATE TABLE IF NOT EXISTS "auth_group_permissions" (
    "id" BIGSERIAL PRIMARY KEY,
    "group_id" INTEGER NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED,
    "permission_id" INTEGER NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("group_id", "permission_id")
);
CREATE INDEX IF NOT EXISTS "auth_group_permissions_group_id_idx" ON "auth_group_permissions" ("group_id");
CREATE INDEX IF NOT EXISTS "auth_group_permissions_permission_id_idx" ON "auth_group_permissions" ("permission_id");

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS "auth_user" (
    "id" SERIAL PRIMARY KEY,
    "password" VARCHAR(128) NOT NULL,
    "last_login" TIMESTAMP WITH TIME ZONE NULL,
    "is_superuser" BOOLEAN NOT NULL DEFAULT FALSE,
    "username" VARCHAR(150) NOT NULL UNIQUE,
    "first_name" VARCHAR(150) NOT NULL DEFAULT '',
    "last_name" VARCHAR(150) NOT NULL DEFAULT '',
    "email" VARCHAR(254) NOT NULL DEFAULT '',
    "is_staff" BOOLEAN NOT NULL DEFAULT FALSE,
    "is_active" BOOLEAN NOT NULL DEFAULT TRUE,
    "date_joined" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "auth_user_username_like" ON "auth_user" ("username" varchar_pattern_ops);

-- Tabela de grupos de usuários
CREATE TABLE IF NOT EXISTS "auth_user_groups" (
    "id" BIGSERIAL PRIMARY KEY,
    "user_id" INTEGER NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "group_id" INTEGER NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("user_id", "group_id")
);
CREATE INDEX IF NOT EXISTS "auth_user_groups_user_id_idx" ON "auth_user_groups" ("user_id");
CREATE INDEX IF NOT EXISTS "auth_user_groups_group_id_idx" ON "auth_user_groups" ("group_id");

-- Tabela de permissões de usuários
CREATE TABLE IF NOT EXISTS "auth_user_user_permissions" (
    "id" BIGSERIAL PRIMARY KEY,
    "user_id" INTEGER NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "permission_id" INTEGER NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("user_id", "permission_id")
);
CREATE INDEX IF NOT EXISTS "auth_user_user_permissions_user_id_idx" ON "auth_user_user_permissions" ("user_id");
CREATE INDEX IF NOT EXISTS "auth_user_user_permissions_permission_id_idx" ON "auth_user_user_permissions" ("permission_id");

-- Log do admin do Django
CREATE TABLE IF NOT EXISTS "django_admin_log" (
    "id" SERIAL PRIMARY KEY,
    "action_time" TIMESTAMP WITH TIME ZONE NOT NULL,
    "object_id" TEXT NULL,
    "object_repr" VARCHAR(200) NOT NULL,
    "action_flag" SMALLINT NOT NULL CHECK ("action_flag" >= 0),
    "change_message" TEXT NOT NULL,
    "content_type_id" INTEGER NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "user_id" INTEGER NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX IF NOT EXISTS "django_admin_log_content_type_id_idx" ON "django_admin_log" ("content_type_id");
CREATE INDEX IF NOT EXISTS "django_admin_log_user_id_idx" ON "django_admin_log" ("user_id");

-- ============================================================
-- PARTE 3: TABELAS DO DJANGO-ALLAUTH (Autenticação Social)
-- ============================================================

-- Endereços de email
CREATE TABLE IF NOT EXISTS "account_emailaddress" (
    "id" SERIAL PRIMARY KEY,
    "email" VARCHAR(254) NOT NULL,
    "verified" BOOLEAN NOT NULL DEFAULT FALSE,
    "primary" BOOLEAN NOT NULL DEFAULT FALSE,
    "user_id" INTEGER NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX IF NOT EXISTS "account_emailaddress_user_id_idx" ON "account_emailaddress" ("user_id");
CREATE INDEX IF NOT EXISTS "account_emailaddress_email_like" ON "account_emailaddress" ("email" varchar_pattern_ops);
CREATE INDEX IF NOT EXISTS "account_emailaddress_upper_email_idx" ON "account_emailaddress" (UPPER("email"));

-- Confirmações de email
CREATE TABLE IF NOT EXISTS "account_emailconfirmation" (
    "id" SERIAL PRIMARY KEY,
    "created" TIMESTAMP WITH TIME ZONE NOT NULL,
    "sent" TIMESTAMP WITH TIME ZONE NULL,
    "key" VARCHAR(64) NOT NULL UNIQUE,
    "email_address_id" INTEGER NOT NULL REFERENCES "account_emailaddress" ("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX IF NOT EXISTS "account_emailconfirmation_email_address_id_idx" ON "account_emailconfirmation" ("email_address_id");
CREATE INDEX IF NOT EXISTS "account_emailconfirmation_key_like" ON "account_emailconfirmation" ("key" varchar_pattern_ops);

-- Aplicativos de conta social
CREATE TABLE IF NOT EXISTS "socialaccount_socialapp" (
    "id" SERIAL PRIMARY KEY,
    "provider" VARCHAR(30) NOT NULL,
    "name" VARCHAR(40) NOT NULL,
    "client_id" VARCHAR(191) NOT NULL,
    "secret" VARCHAR(191) NOT NULL,
    "key" VARCHAR(191) NOT NULL DEFAULT '',
    "provider_id" VARCHAR(200) NOT NULL DEFAULT '',
    "settings" JSONB NOT NULL DEFAULT '{}'::JSONB
);

-- Relação entre apps sociais e sites
CREATE TABLE IF NOT EXISTS "socialaccount_socialapp_sites" (
    "id" BIGSERIAL PRIMARY KEY,
    "socialapp_id" INTEGER NOT NULL REFERENCES "socialaccount_socialapp" ("id") DEFERRABLE INITIALLY DEFERRED,
    "site_id" INTEGER NOT NULL REFERENCES "django_site" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("socialapp_id", "site_id")
);
CREATE INDEX IF NOT EXISTS "socialaccount_socialapp_sites_socialapp_id_idx" ON "socialaccount_socialapp_sites" ("socialapp_id");
CREATE INDEX IF NOT EXISTS "socialaccount_socialapp_sites_site_id_idx" ON "socialaccount_socialapp_sites" ("site_id");

-- Contas sociais dos usuários
CREATE TABLE IF NOT EXISTS "socialaccount_socialaccount" (
    "id" SERIAL PRIMARY KEY,
    "provider" VARCHAR(200) NOT NULL,
    "uid" VARCHAR(191) NOT NULL,
    "last_login" TIMESTAMP WITH TIME ZONE NOT NULL,
    "date_joined" TIMESTAMP WITH TIME ZONE NOT NULL,
    "extra_data" JSONB NOT NULL DEFAULT '{}'::JSONB,
    "user_id" INTEGER NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("provider", "uid")
);
CREATE INDEX IF NOT EXISTS "socialaccount_socialaccount_user_id_idx" ON "socialaccount_socialaccount" ("user_id");

-- Tokens de contas sociais
CREATE TABLE IF NOT EXISTS "socialaccount_socialtoken" (
    "id" SERIAL PRIMARY KEY,
    "token" TEXT NOT NULL,
    "token_secret" TEXT NOT NULL DEFAULT '',
    "expires_at" TIMESTAMP WITH TIME ZONE NULL,
    "account_id" INTEGER NOT NULL REFERENCES "socialaccount_socialaccount" ("id") DEFERRABLE INITIALLY DEFERRED,
    "app_id" INTEGER NULL REFERENCES "socialaccount_socialapp" ("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX IF NOT EXISTS "socialaccount_socialtoken_account_id_idx" ON "socialaccount_socialtoken" ("account_id");
CREATE INDEX IF NOT EXISTS "socialaccount_socialtoken_app_id_idx" ON "socialaccount_socialtoken" ("app_id");

-- ============================================================
-- PARTE 4: TABELAS DO APLICATIVO SIMED (pessoas)
-- ============================================================

-- Tabela de Especialidades Médicas
CREATE TABLE IF NOT EXISTS "pessoas_especialidade" (
    "id" BIGSERIAL PRIMARY KEY,
    "nome" VARCHAR(100) NOT NULL UNIQUE,
    "descricao" TEXT NULL,
    "icone" VARCHAR(50) NOT NULL DEFAULT 'fa-stethoscope'
);
CREATE INDEX IF NOT EXISTS "pessoas_especialidade_nome_like" ON "pessoas_especialidade" ("nome" varchar_pattern_ops);

-- Tabela de Perfis de Usuário
CREATE TABLE IF NOT EXISTS "pessoas_perfil" (
    "id" BIGSERIAL PRIMARY KEY,
    "tipo_usuario" VARCHAR(10) NOT NULL DEFAULT 'paciente',
    "data_nascimento" DATE NULL,
    "rg" VARCHAR(20) NULL,
    "endereco" VARCHAR(255) NULL,
    "telefone" VARCHAR(20) NULL,
    "usuario_id" INTEGER NOT NULL UNIQUE REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT "pessoas_perfil_tipo_check" CHECK ("tipo_usuario" IN ('admin', 'medico', 'atendente', 'paciente'))
);

-- Tabela de Profissionais de Saúde
CREATE TABLE IF NOT EXISTS "pessoas_profissional" (
    "id" BIGSERIAL PRIMARY KEY,
    "nome" VARCHAR(200) NOT NULL,
    "crm" VARCHAR(20) NULL,
    "foto" VARCHAR(100) NULL,
    "biografia" TEXT NULL,
    "formacao" TEXT NULL,
    "certificacoes" TEXT NULL,
    "objetivos" TEXT NULL,
    "telefone" VARCHAR(20) NULL,
    "email" VARCHAR(254) NULL,
    "ativo" BOOLEAN NOT NULL DEFAULT TRUE,
    "destaque" BOOLEAN NOT NULL DEFAULT FALSE,
    "slug" VARCHAR(50) NULL UNIQUE,
    "especialidade_id" BIGINT NULL REFERENCES "pessoas_especialidade" ("id") DEFERRABLE INITIALLY DEFERRED,
    "usuario_id" INTEGER NULL UNIQUE REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX IF NOT EXISTS "pessoas_profissional_slug_like" ON "pessoas_profissional" ("slug" varchar_pattern_ops);
CREATE INDEX IF NOT EXISTS "pessoas_profissional_especialidade_id_idx" ON "pessoas_profissional" ("especialidade_id");

-- Tabela de Horários de Trabalho
CREATE TABLE IF NOT EXISTS "pessoas_horariotrabalho" (
    "id" BIGSERIAL PRIMARY KEY,
    "dia_semana" INTEGER NOT NULL CHECK ("dia_semana" >= 0 AND "dia_semana" <= 6),
    "hora_inicio" TIME NOT NULL,
    "hora_fim" TIME NOT NULL,
    "intervalo_minutos" INTEGER NOT NULL DEFAULT 30 CHECK ("intervalo_minutos" >= 0),
    "ativo" BOOLEAN NOT NULL DEFAULT TRUE,
    "profissional_id" BIGINT NOT NULL REFERENCES "pessoas_profissional" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("profissional_id", "dia_semana", "hora_inicio")
);
CREATE INDEX IF NOT EXISTS "pessoas_horariotrabalho_profissional_id_idx" ON "pessoas_horariotrabalho" ("profissional_id");

-- Tabela de Consultas
CREATE TABLE IF NOT EXISTS "pessoas_consulta" (
    "id" BIGSERIAL PRIMARY KEY,
    "data_hora" TIMESTAMP WITH TIME ZONE NOT NULL,
    "status" VARCHAR(15) NOT NULL DEFAULT 'agendada',
    "relatorio" TEXT NULL,
    "observacoes" TEXT NULL,
    "criado_em" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "atualizado_em" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "paciente_id" INTEGER NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "medico_id" INTEGER NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "profissional_id" BIGINT NULL REFERENCES "pessoas_profissional" ("id") DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT "pessoas_consulta_status_check" CHECK ("status" IN ('agendada', 'confirmada', 'concluida', 'cancelada'))
);
CREATE INDEX IF NOT EXISTS "pessoas_consulta_paciente_id_idx" ON "pessoas_consulta" ("paciente_id");
CREATE INDEX IF NOT EXISTS "pessoas_consulta_medico_id_idx" ON "pessoas_consulta" ("medico_id");
CREATE INDEX IF NOT EXISTS "pessoas_consulta_profissional_id_idx" ON "pessoas_consulta" ("profissional_id");

-- Tabela de Medicamentos
CREATE TABLE IF NOT EXISTS "pessoas_medicamento" (
    "id" BIGSERIAL PRIMARY KEY,
    "nome" VARCHAR(200) NOT NULL UNIQUE,
    "principio_ativo" VARCHAR(200) NULL,
    "foto" VARCHAR(100) NULL,
    "valor" NUMERIC(10, 2) NOT NULL CHECK ("valor" > 0),
    "necessita_receita" BOOLEAN NOT NULL DEFAULT TRUE,
    "descricao" TEXT NULL,
    "estoque" INTEGER NOT NULL DEFAULT 0 CHECK ("estoque" >= 0)
);
CREATE INDEX IF NOT EXISTS "pessoas_medicamento_nome_like" ON "pessoas_medicamento" ("nome" varchar_pattern_ops);

-- Tabela de Comentários de Pacientes
CREATE TABLE IF NOT EXISTS "pessoas_comentariopaciente" (
    "id" BIGSERIAL PRIMARY KEY,
    "texto" TEXT NOT NULL,
    "avaliacao" INTEGER NOT NULL DEFAULT 5 CHECK ("avaliacao" >= 1 AND "avaliacao" <= 5),
    "status" VARCHAR(10) NOT NULL DEFAULT 'pendente',
    "criado_em" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "atualizado_em" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "data_aprovacao" TIMESTAMP WITH TIME ZONE NULL,
    "paciente_id" INTEGER NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "aprovado_por_id" INTEGER NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT "pessoas_comentariopaciente_status_check" CHECK ("status" IN ('pendente', 'aprovado', 'reprovado'))
);
CREATE INDEX IF NOT EXISTS "pessoas_comentariopaciente_paciente_id_idx" ON "pessoas_comentariopaciente" ("paciente_id");
CREATE INDEX IF NOT EXISTS "pessoas_comentariopaciente_aprovado_por_id_idx" ON "pessoas_comentariopaciente" ("aprovado_por_id");

-- ============================================================
-- PARTE 5: DADOS INICIAIS OBRIGATÓRIOS
-- ============================================================

-- Inserir site padrão (necessário para django.contrib.sites)
INSERT INTO "django_site" ("id", "domain", "name") 
VALUES (1, 'simed.railway.app', 'SIMED - Serviço Integrado de Medicina')
ON CONFLICT ("id") DO UPDATE SET 
    "domain" = EXCLUDED."domain",
    "name" = EXCLUDED."name";

-- Inserir especialidades médicas padrão
INSERT INTO "pessoas_especialidade" ("nome", "descricao", "icone") VALUES
    ('Clínica Geral', 'Atendimento médico geral para adultos', 'fa-user-md'),
    ('Pediatria', 'Atendimento especializado para crianças', 'fa-baby'),
    ('Cardiologia', 'Especialidade do coração e sistema cardiovascular', 'fa-heartbeat'),
    ('Dermatologia', 'Especialidade da pele, cabelos e unhas', 'fa-hand-sparkles'),
    ('Ortopedia', 'Especialidade dos ossos, articulações e músculos', 'fa-bone'),
    ('Ginecologia', 'Saúde da mulher', 'fa-venus'),
    ('Oftalmologia', 'Especialidade dos olhos e visão', 'fa-eye'),
    ('Neurologia', 'Especialidade do sistema nervoso', 'fa-brain'),
    ('Psiquiatria', 'Saúde mental e transtornos psiquiátricos', 'fa-comments'),
    ('Endocrinologia', 'Especialidade das glândulas e hormônios', 'fa-syringe')
ON CONFLICT ("nome") DO NOTHING;

-- ============================================================
-- PARTE 6: TRIGGERS E FUNÇÕES ÚTEIS
-- ============================================================

-- Função para atualizar automaticamente o campo atualizado_em
CREATE OR REPLACE FUNCTION update_atualizado_em_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para consultas
DROP TRIGGER IF EXISTS update_pessoas_consulta_atualizado_em ON pessoas_consulta;
CREATE TRIGGER update_pessoas_consulta_atualizado_em
    BEFORE UPDATE ON pessoas_consulta
    FOR EACH ROW
    EXECUTE FUNCTION update_atualizado_em_column();

-- Trigger para comentários
DROP TRIGGER IF EXISTS update_pessoas_comentariopaciente_atualizado_em ON pessoas_comentariopaciente;
CREATE TRIGGER update_pessoas_comentariopaciente_atualizado_em
    BEFORE UPDATE ON pessoas_comentariopaciente
    FOR EACH ROW
    EXECUTE FUNCTION update_atualizado_em_column();

-- ============================================================
-- FIM DO SCRIPT
-- ============================================================
