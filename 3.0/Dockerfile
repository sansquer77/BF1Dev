FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicação
COPY . .

# Criar diretórios de dados
RUN mkdir -p /app/data /app/backups /app/logs

# Fazer entrypoint executável
RUN chmod +x entrypoint.sh

# Exposer porta
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Executar entrypoint
ENTRYPOINT ["./entrypoint.sh"]
