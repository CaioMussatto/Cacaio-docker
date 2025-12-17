#!/bin/bash

set -e  

echo "🚀 Configurando projeto Shiny..."


if ! command -v uv &> /dev/null; then
    echo "📦 Instalando UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc
fi


echo "📦 Instalando dependências com UV..."
uv sync


if [ ! -f .env ]; then
    echo "⚙️ Criando arquivo .env..."
    cp .env.example .env
    echo "⚠️  Edite o arquivo .env com suas configurações"
fi


echo "📁 Criando estrutura de diretórios..."
mkdir -p logs data 


echo "📊 Verificando dados..."
if [ -f "data/degs.pkl" ] && [ -f "data/sc_samples.pkl" ]; then
    echo "✅ Dados encontrados"
else
    echo "⚠️  Arquivos .pkl não encontrados na pasta data/"
    echo "   Coloque degs.pkl e sc_samples.pkl em data/"
fi

echo "✅ Setup completo!"
echo ""
echo "Comandos disponíveis:"
echo "  uv run start     - Inicia a aplicação"
echo "  make docker-up   - Inicia com Docker Compose"
echo "  make deploy-gcp  - Deploy no Google Cloud Run"
