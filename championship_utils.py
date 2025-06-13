# championship_utils.py

from db_utils import championship_db_connect  # Certifique-se de que esta função está em db_utils.py

def init_championship_db():
    """Cria as tabelas necessárias para apostas e resultado do campeonato."""
    conn = championship_db_connect()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS championship_bets (
            user_id INTEGER PRIMARY KEY,
            champion TEXT NOT NULL,
            vice TEXT NOT NULL,
            team TEXT NOT NULL
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
    """Salva ou atualiza a aposta do usuário para o campeonato."""
    init_championship_db()
    conn = championship_db_connect()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO championship_bets (user_id, champion, vice, team)
        VALUES (?, ?, ?, ?)
    ''', (user_id, champion, vice, team))
    conn.commit()
    conn.close()

def get_championship_bet(user_id):
    """Retorna a aposta do usuário no campeonato."""
    init_championship_db()
    conn = championship_db_connect()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT champion, vice, team FROM championship_bets WHERE user_id = ?
    ''', (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"champion": result[0], "vice": result[1], "team": result[2]}
    return None

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
