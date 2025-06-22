import pandas as pd
from db_utils import championship_db_connect
from datetime import datetime, timedelta, UTC

def init_championship_db():
    """Cria as tabelas necessárias para apostas e resultado do campeonato."""
    conn = championship_db_connect()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS championship_bets (
            user_id INTEGER PRIMARY KEY,
            champion TEXT NOT NULL,
            vice TEXT NOT NULL,
            team TEXT NOT NULL,
            bet_time TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS championship_bets_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            champion TEXT NOT NULL,
            vice TEXT NOT NULL,
            team TEXT NOT NULL,
            bet_time TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS championship_results (
            season INTEGER PRIMARY KEY DEFAULT 2025,
            champion TEXT NOT NULL,
            vice TEXT NOT NULL,
            team TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_championship_bet(user_id, champion, vice, team):
    """Salva ou atualiza a aposta do usuário para o campeonato e registra no log."""
    init_championship_db()
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
    conn = championship_db_connect()
    cursor = conn.cursor()
    # Atualiza aposta válida (última)
    cursor.execute('''
        INSERT OR REPLACE INTO championship_bets (user_id, champion, vice, team, bet_time)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, champion, vice, team, now))
    # Registra log de apostas
    cursor.execute('''
        INSERT INTO championship_bets_log (user_id, champion, vice, team, bet_time)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, champion, vice, team, now))
    conn.commit()
    conn.close()

def get_championship_bet(user_id):
    """Retorna a última aposta válida do usuário no campeonato."""
    init_championship_db()
    conn = championship_db_connect()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT champion, vice, team, bet_time FROM championship_bets WHERE user_id = ?
    ''', (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"champion": result[0], "vice": result[1], "team": result[2], "bet_time": result[3]}
    return None

def get_championship_bet_log(user_id):
    """Retorna o histórico de apostas do usuário no campeonato (mais recente primeiro)."""
    init_championship_db()
    conn = championship_db_connect()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT champion, vice, team, bet_time
        FROM championship_bets_log
        WHERE user_id = ?
        ORDER BY bet_time DESC
    ''', (user_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def save_final_results(champion, vice, team, season=2025):
    """Salva ou atualiza o resultado oficial do campeonato."""
    init_championship_db()
    conn = championship_db_connect()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO championship_results (season, champion, vice, team)
        VALUES (?, ?, ?, ?)
    ''', (season, champion, vice, team))
    conn.commit()
    conn.close()

def get_final_results(season=2025):
    """Retorna o resultado oficial do campeonato."""
    init_championship_db()
    conn = championship_db_connect()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT champion, vice, team FROM championship_results WHERE season = ?
    ''', (season,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"champion": result[0], "vice": result[1], "team": result[2]}
    return None

def calcular_pontuacao_campeonato(user_id, season=2025):
    """Calcula a pontuação bônus do participante com base nas apostas e resultado final."""
    aposta = get_championship_bet(user_id)
    resultado = get_final_results(season)
    pontos = 0
    if aposta and resultado:
        if aposta["champion"] == resultado["champion"]:
            pontos += 150
        if aposta["vice"] == resultado["vice"]:
            pontos += 100
        if aposta["team"] == resultado["team"]:
            pontos += 80
    return pontos

def get_apostas_df():
    """
    Retorna um DataFrame com todas as apostas.
    Colunas: usuario_id, prova_id, pilotos, fichas, piloto_11, data_envio, automatica
    """
    try:
        conn = db_connect()
        query = """
            SELECT usuario_id, prova_id, pilotos, fichas, piloto_11, data_envio, automatica
            FROM apostas
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        # Garante que todas as colunas existem
        for col in ['usuario_id', 'prova_id', 'pilotos', 'fichas', 'piloto_11', 'data_envio', 'automatica']:
            if col not in df.columns:
                df[col] = None
        return df
    except Exception as e:
        print(f"Erro ao buscar apostas: {e}")
        return pd.DataFrame(columns=[
            'usuario_id', 'prova_id', 'pilotos', 'fichas', 'piloto_11', 'data_envio', 'automatica'
        ])

def get_usuarios_df():
    """
    Retorna um DataFrame com todos os usuários.
    Colunas: id, nome, email, status, perfil, faltas
    """
    try:
        conn = db_connect()
        query = """
            SELECT id, nome, email, status, perfil, faltas
            FROM usuarios
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        # Garante que todas as colunas existem
        for col in ['id', 'nome', 'email', 'status', 'perfil', 'faltas']:
            if col not in df.columns:
                df[col] = None
        return df
    except Exception as e:
        print(f"Erro ao buscar usuários: {e}")
        return pd.DataFrame(columns=[
            'id', 'nome', 'email', 'status', 'perfil', 'faltas'
        ])

def get_provas_df():
    """
    Retorna um DataFrame com todas as provas.
    Colunas: id, nome, data, horario_prova
    """
    try:
        conn = db_connect()
        query = """
            SELECT id, nome, data, horario_prova
            FROM provas
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        # Garante que todas as colunas existem
        for col in ['id', 'nome', 'data', 'horario_prova']:
            if col not in df.columns:
                df[col] = None
        return df
    except Exception as e:
        print(f"Erro ao buscar provas: {e}")
        return pd.DataFrame(columns=[
            'id', 'nome', 'data', 'horario_prova'
        ])
