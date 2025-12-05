#!/bin/bash

# Script de configuração do Google OAuth para o Sistema de Consultas

echo "=========================================="
echo "Setup do Google OAuth - Sistema de Consultas"
echo "=========================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar se está no diretório correto
if [ ! -f "manage.py" ]; then
    echo -e "${RED}Erro: Execute este script no diretório raiz do projeto Django${NC}"
    exit 1
fi

echo -e "${YELLOW}1. Instalando dependências...${NC}"
pip3 install django-allauth mysqlclient PyJWT cryptography

echo ""
echo -e "${YELLOW}2. Executando migrações do banco de dados...${NC}"
python3.11 manage.py migrate

echo ""
echo -e "${GREEN}✓ Instalação concluída!${NC}"
echo ""
echo "=========================================="
echo "Próximos passos:"
echo "=========================================="
echo ""
echo "1. Inicie o servidor:"
echo "   python3.11 manage.py runserver 0.0.0.0:8000"
echo ""
echo "2. Acesse o admin: http://localhost:8000/admin/"
echo ""
echo "3. Configure o Google OAuth no admin:"
echo "   - Sites: Edite o site padrão"
echo "   - Social applications: Adicione Google OAuth"
echo ""
echo "4. Configure as URLs no Google Cloud Console:"
echo "   - URI de redirecionamento:"
echo "     http://localhost:8000/accounts/google/login/callback/"
echo ""
echo "Leia INSTALACAO_GOOGLE_OAUTH.md para mais detalhes"
echo ""
