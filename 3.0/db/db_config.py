"""
Configurações Centralizadas do Banco de Dados
Facilita manutenção e padronização
"""

from pathlib import Path

# Caminho do banco de dados
DB_PATH = Path("bolao_f1.db")

# Configurações de Pool
POOL_SIZE = 5
DB_TIMEOUT = 30.0

# Configurações de Cache
CACHE_TTL_CURTO = 300  # 5 minutos
CACHE_TTL_MEDIO = 3600  # 1 hora
CACHE_TTL_LONGO = 86400  # 24 horas

# Índices para otimização (criados em migrations.py)
INDICES = {
    "usuarios": [
        "CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email)",
        "CREATE INDEX IF NOT EXISTS idx_usuarios_perfil ON usuarios(perfil)",
        "CREATE INDEX IF NOT EXISTS idx_usuarios_status ON usuarios(status)",
    ],
    "apostas": [
        "CREATE INDEX IF NOT EXISTS idx_apostas_usuario ON apostas(usuario_id)",
        "CREATE INDEX IF NOT EXISTS idx_apostas_prova ON apostas(prova_id)",
        "CREATE INDEX IF NOT EXISTS idx_apostas_timestamp ON apostas(timestamp)",
    ],
    "provas": [
        "CREATE INDEX IF NOT EXISTS idx_provas_data ON provas(data)",
        "CREATE INDEX IF NOT EXISTS idx_provas_status ON provas(status)",
    ],
    "resultados": [
        "CREATE INDEX IF NOT EXISTS idx_resultados_prova ON resultados(prova_id)",
        "CREATE INDEX IF NOT EXISTS idx_resultados_usuario ON resultados(usuario_id)",
    ],
}

# Configurações de Segurança
BCRYPT_ROUNDS = 12
SESSION_TIMEOUT = 3600  # 1 hora em segundos
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 900  # 15 minutos
