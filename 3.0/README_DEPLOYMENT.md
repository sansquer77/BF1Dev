# 🚀 BF1Dev 3.0 - Guia de Deployment

## Digital Ocean App Platform

### 1️⃣ Preparação Inicial

#### Pré-requisitos
- Conta Digital Ocean ativa
- GitHub repository com o código (público ou privado)
- Variáveis de ambiente configuradas

### 2️⃣ Configurar Variáveis de Ambiente no Digital Ocean

1. Acesse **Digital Ocean Console**
2. Vá para **Apps** > **Create App**
3. Conecte seu repositório GitHub
4. Na seção **Environment Variables**, adicione:

```
JWT_SECRET=<sua_chave_secreta_jwt>
EMAIL_REMETENTE=<seu_email@gmail.com>
SENHA_EMAIL=<sua_senha_ou_token>
EMAIL_ADMIN=<email_admin@seudominio.com>
usuario_master=Administrator
email_master=master@sistema.local
senha_master=<sua_senha_master>
DATABASE_PATH=/app/data/bolao_f1.db
```

### 3️⃣ Deploy via app.yaml

O arquivo `app.yaml` na raiz do projeto define:
- ✅ Build command: Instala dependências
- ✅ Run command: Executa Streamlit
- ✅ Volume persistente para dados
- ✅ Health check
- ✅ Port mapping

**Digital Ocean lerá automaticamente o `app.yaml` e fará deploy!**

### 4️⃣ Deploy Local com Docker

#### Teste local antes de deployar:

```bash
# Copiar variáveis de ambiente
cp .env.example .env
# Editar .env com seus valores
nano .env

# Build e run com Docker Compose
docker-compose up --build
```

Acesse: `http://localhost:8501`

### 5️⃣ Deploy Manual com Docker

```bash
# Build da imagem
docker build -t bf1dev:latest .

# Run do container
docker run -d \
  -p 8501:8501 \
  -v bf1dev_data:/app/data \
  -v bf1dev_backups:/app/backups \
  -v bf1dev_logs:/app/logs \
  -e DATABASE_PATH=/app/data/bolao_f1.db \
  -e JWT_SECRET=your_secret_key \
  -e EMAIL_REMETENTE=your_email \
  -e SENHA_EMAIL=your_password \
  --name bf1dev \
  bf1dev:latest
```

### 6️⃣ Estrutura de Deployment

```
BF1Dev/3.0/
├── app.yaml                 # Configuração Digital Ocean
├── Dockerfile              # Para containerização
├── docker-compose.yml      # Para desenvolvimento local
├── entrypoint.sh          # Script de inicialização
├── .env.example           # Variáveis de exemplo
├── .streamlit/
│   └── config.toml        # Configurações Streamlit
├── requirements.txt       # Dependências Python
├── main.py               # Aplicação principal
├── db/
│   ├── db_config.py      # Suporta env vars
│   └── ...
└── data/                 # Diretório persistente (criado automaticamente)
```

### 7️⃣ Persistent Storage

O Digital Ocean App Platform mantém os dados em um volume:
- **Volume Name**: `db-volume`
- **Mount Path**: `/app/data`
- **Tamanho**: 1GB (ajustável em app.yaml)

Os arquivos do banco de dados são preservados entre deploys.

### 8️⃣ Monitoramento

#### Logs em Digital Ocean
- Vá para **Apps** > **bf1dev** > **Logs**
- Filtre por aplicação ou componente

#### Health Check
- Endpoint: `/_stcore/health`
- Intervalo: 30s
- Timeout: 10s

### 9️⃣ Troubleshooting

#### App não inicia
```bash
# Verificar logs
docker logs bf1dev

# Verificar variáveis
env | grep DATABASE_PATH
```

#### Banco de dados vazio após deploy
- Verifique se o volume foi criado corretamente
- Confirme permissões do diretório `/app/data`
- Reinicie a aplicação

#### Email não é enviado
- Valide `EMAIL_REMETENTE` e `SENHA_EMAIL`
- Para Gmail, use [App Passwords](https://support.google.com/accounts/answer/185833)
- Verifique firewall/SMTP

#### JWT_SECRET não definido
- Adicione em Digital Ocean Environment Variables
- Ou exporte localmente: `export JWT_SECRET=sua_chave`

### 🔟 Atualizar Aplicação

**No Digital Ocean:**
1. Push código para GitHub
2. App Platform detecta automaticamente
3. Faz rebuild e redeploy

**Ou manualmente:**
```bash
docker-compose down
docker-compose up --build -d
```

### 📋 Checklist Pre-Deployment

- [ ] `.env.example` preenchido com variáveis corretas
- [ ] `requirements.txt` atualizado
- [ ] `app.yaml` configurado corretamente
- [ ] Database path validado
- [ ] Email credentials testados
- [ ] JWT_SECRET gerado e seguro
- [ ] Volume de armazenamento configurado
- [ ] Health check testado localmente
- [ ] Backups configurados
- [ ] Logs habilitados

### 🔐 Segurança

- ✅ Never commit `.env` (use `.env.example`)
- ✅ Secrets em Digital Ocean Environment Variables
- ✅ HTTPS habilitado automaticamente
- ✅ CORS configurado
- ✅ XSRF Protection ativada
- ✅ Passwords com bcrypt

### 📞 Suporte

Para mais informações:
- [Digital Ocean Apps Docs](https://docs.digitalocean.com/products/app-platform/)
- [Streamlit Deployment](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)
- Issues no GitHub
