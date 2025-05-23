import streamlit as st
import sqlite3
import bcrypt
import jwt as pyjwt
import pandas as pd
from datetime import datetime, timedelta
import ast
import matplotlib.pyplot as plt

DB_PATH = 'bolao_f1alpha.db'
JWT_SECRET = 'sua_chave_secreta_supersegura'
JWT_EXP_MINUTES = 120

def ler_regulamento(arquivo="regulamento.txt"):
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Erro ao carregar o regulamento: {e}"

def db_connect():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = db_connect()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    email TEXT UNIQUE,
                    senha_hash TEXT,
                    perfil TEXT,
                    status TEXT DEFAULT 'Ativo',
                    faltas INTEGER DEFAULT 0)''')
    senha_hash = bcrypt.hashpw('ADMIN'.encode(), bcrypt.gensalt())
    c.execute('''INSERT OR IGNORE INTO usuarios (nome, email, senha_hash, perfil, status, faltas)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              ('Password', 'master@bolao.com', senha_hash, 'master', 'Ativo', 0))
    c.execute('''CREATE TABLE IF NOT EXISTS pilotos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    equipe TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS provas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    data TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS apostas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER,
                    prova_id INTEGER,
                    data_envio TEXT,
                    pilotos TEXT,
                    fichas TEXT,
                    piloto_11 TEXT,
                    nome_prova TEXT,
                    automatica INTEGER DEFAULT 0,
                    FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
                    FOREIGN KEY(prova_id) REFERENCES provas(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS resultados (
                    prova_id INTEGER PRIMARY KEY,
                    posicoes TEXT,
                    FOREIGN KEY(prova_id) REFERENCES provas(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS log_apostas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    apostador TEXT,
                    data TEXT,
                    horario TEXT,
                    aposta TEXT,
                    nome_prova TEXT)''')
    conn.commit()
    conn.close()

# --- Funções utilitárias com cache para leitura ---
@st.cache_data
def get_usuarios_df():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM usuarios', conn)
    conn.close()
    return df

@st.cache_data
def get_pilotos_df():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM pilotos', conn)
    conn.close()
    return df

@st.cache_data
def get_provas_df():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM provas', conn)
    conn.close()
    return df

@st.cache_data
def get_apostas_df():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM apostas', conn)
    conn.close()
    return df

@st.cache_data
def get_resultados_df():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM resultados', conn)
    conn.close()
    return df

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())
def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)
def generate_token(user_id, perfil, status):
    payload = {
        'user_id': user_id,
        'perfil': perfil,
        'status': status,
        'exp': datetime.utcnow() + timedelta(minutes=JWT_EXP_MINUTES)
    }
    token = pyjwt.encode(payload, JWT_SECRET, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token
def decode_token(token):
    try:
        payload = pyjwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except pyjwt.ExpiredSignatureError:
        return None
    except Exception:
        return None

def cadastrar_usuario(nome, email, senha, perfil='participante', status='Ativo'):
    conn = db_connect()
    c = conn.cursor()
    try:
        senha_hash = hash_password(senha)
        c.execute('INSERT INTO usuarios (nome, email, senha_hash, perfil, status, faltas) VALUES (?, ?, ?, ?, ?, ?)', 
                  (nome, email, senha_hash, perfil, status, 0))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_by_email(email):
    conn = db_connect()
    c = conn.cursor()
    c.execute('SELECT id, nome, email, senha_hash, perfil, status, faltas FROM usuarios WHERE email=?', (email,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('SELECT id, nome, email, perfil, status, faltas FROM usuarios WHERE id=?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def autenticar_usuario(email, senha):
    user = get_user_by_email(email)
    if user and check_password(senha, user[3]):
        return user
    return None

def salvar_aposta(usuario_id, prova_id, pilotos, fichas, piloto_11, nome_prova, automatica=0):
    conn = db_connect()
    c = conn.cursor()
    data_envio = datetime.now().isoformat()
    c.execute('DELETE FROM apostas WHERE usuario_id=? AND prova_id=?', (usuario_id, prova_id))
    c.execute('INSERT INTO apostas (usuario_id, prova_id, data_envio, pilotos, fichas, piloto_11, nome_prova, automatica) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
              (usuario_id, prova_id, data_envio, ','.join(pilotos), ','.join(map(str, fichas)), piloto_11, nome_prova, automatica))
    conn.commit()
    conn.close()

def registrar_log_aposta(apostador, aposta, nome_prova):
    conn = db_connect()
    c = conn.cursor()
    agora = datetime.now()
    data = agora.strftime('%Y-%m-%d')
    horario = agora.strftime('%H:%M:%S')
    c.execute('INSERT INTO log_apostas (apostador, data, horario, aposta, nome_prova) VALUES (?, ?, ?, ?, ?)',
              (apostador, data, horario, aposta, nome_prova))
    conn.commit()
    conn.close()

def calcular_pontuacao_lote(apostas_df, resultados_df):
    pontos_f1 = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
    resultados = {}
    for _, row in resultados_df.iterrows():
        resultados[row['prova_id']] = ast.literal_eval(row['posicoes'])
    pontos = []
    for _, aposta in apostas_df.iterrows():
        prova_id = aposta['prova_id']
        if prova_id not in resultados:
            pontos.append(None)
            continue
        res = resultados[prova_id]
        pilotos = aposta['pilotos'].split(",")
        fichas = list(map(int, aposta['fichas'].split(",")))
        piloto_11 = aposta['piloto_11']
        automatica = int(aposta['automatica'])
        pt = 0
        for p, f in zip(pilotos, fichas):
            for pos, nome in res.items():
                pos_int = int(pos)
                if pos_int <= 10 and nome == p:
                    pt += f * pontos_f1[pos_int-1]
        if '11' in res and res['11'] == piloto_11:
            pt += 25
        if automatica >= 2:
            pt = int(pt * 0.75)
        pontos.append(pt)
    return pontos

def gerar_aposta_automatica(usuario_id, prova_id, nome_prova, apostas_df, provas_df):
    provas_df = provas_df.sort_values('data')
    idx_prova = provas_df[provas_df['id'] == prova_id].index[0]
    if idx_prova == 0:
        return False, "Não há prova anterior para copiar a aposta."
    prova_ant_id = provas_df.iloc[idx_prova-1]['id']
    ap_ant = apostas_df[(apostas_df['usuario_id'] == usuario_id) & (apostas_df['prova_id'] == prova_ant_id)]
    if ap_ant.empty:
        return False, "Participante não tem aposta anterior para copiar."
    ap_ant = ap_ant.iloc[0]
    pilotos_ant = ap_ant['pilotos'].split(",")
    fichas_ant = list(map(int, ap_ant['fichas'].split(",")))
    piloto_11_ant = ap_ant['piloto_11']
    num_auto = len(apostas_df[(apostas_df['usuario_id'] == usuario_id) & (apostas_df['automatica'] >= 1)])
    salvar_aposta(usuario_id, prova_id, pilotos_ant, fichas_ant, piloto_11_ant, nome_prova, automatica=num_auto+1)
    return True, "Aposta automática gerada!"

# --- Streamlit setup ---
st.set_page_config(page_title="Bolão F1 2025", layout="wide")
init_db()

if 'pagina' not in st.session_state:
    st.session_state['pagina'] = "Login"
if 'token' not in st.session_state:
    st.session_state['token'] = None

def menu_master():
    return [
        "Painel do Participante",
        "Gestão de Usuários",
        "Cadastro de novo participante",
        "Gestão do campeonato",
        "Gestão de Apostas",
        "Atualização de resultados",
        "Log de Apostas",
        "Classificação",
        "Regulamento",
        "Logout"
    ]
def menu_admin():
    return [
        "Painel do Participante",
        "Gestão de Apostas",
        "Atualização de resultados",
        "Log de Apostas",
        "Classificação",
        "Regulamento",
        "Logout"
    ]
def menu_participante():
    return [
        "Painel do Participante",
        "Log de Apostas",
        "Classificação",
        "Regulamento",
        "Logout"
    ]

def get_payload():
    token = st.session_state.get('token')
    if not token:
        st.session_state['pagina'] = "Login"
        st.stop()
    payload = decode_token(token)
    if not payload:
        st.session_state['pagina'] = "Login"
        st.session_state['token'] = None
        st.stop()
    return payload

# --- Login, Menu lateral, Gestão de Usuários, Cadastro de novo participante, Gestão do Campeonato, Atualização de resultados, Log de apostas ---
# (Blocos iguais aos já fornecidos anteriormente, utilize as funções e widgets já revisados)

# --- Painel do Participante ---
# (Bloco igual ao já fornecido, usando get_pilotos_df(), get_provas_df(), get_apostas_df() para carregar dados)

# --- Gestão de Apostas ---
if st.session_state['pagina'] == "Gestão de Apostas" and st.session_state['token']:
    payload = get_payload()
    if payload['perfil'] in ['master', 'admin']:
        st.title("Gestão de Apostas")
        provas_df = get_provas_df()
        usuarios_df = get_usuarios_df()
        apostas_df = get_apostas_df()
        participantes = usuarios_df[usuarios_df['status'] == 'Ativo']
        provas_df = provas_df.sort_values('data')
        tabs = st.tabs(participantes['nome'].tolist())
        for idx, part in enumerate(participantes.itertuples()):
            with tabs[idx]:
                st.subheader(f"Apostas de {part.nome}")
                apostas_part = apostas_df[apostas_df['usuario_id'] == part.id]
                apostas_dict = dict(zip(apostas_part['prova_id'], apostas_part.itertuples()))
                faltas = 0
                for _, prova in provas_df.iterrows():
                    st.write(f"**Prova:** {prova['nome']} ({prova['data']})")
                    if prova['id'] in apostas_dict:
                        ap = apostas_dict[prova['id']]
                        st.success(f"Aposta registrada em {ap.data_envio[:16]}: Pilotos: {ap.pilotos}, Fichas: {ap.fichas}, 11º: {ap.piloto_11}")
                    else:
                        faltas += 1
                        st.warning("Sem aposta registrada.")
                        if st.button(f"Gerar aposta automática para {prova['nome']}", key=f"auto_{part.id}_{prova['id']}"):
                            ok, msg = gerar_aposta_automatica(part.id, prova['id'], prova['nome'], apostas_df, provas_df)
                            st.success(msg) if ok else st.error(msg)
    else:
        st.warning("Acesso restrito ao administrador/master.")

# --- Classificação ---
if st.session_state['pagina'] == "Classificação" and st.session_state['token']:
    st.title("Classificação Geral do Bolão")
    usuarios_df = get_usuarios_df()
    provas_df = get_provas_df()
    apostas_df = get_apostas_df()
    resultados_df = get_resultados_df()
    participantes = usuarios_df[usuarios_df['status'] == 'Ativo']
    provas_df = provas_df.sort_values('data')
    tabela_classificacao = []
    tabela_detalhada = []
    for idx, part in participantes.iterrows():
        apostas_part = apostas_df[apostas_df['usuario_id'] == part['id']].sort_values('prova_id')
        pontos_part = calcular_pontuacao_lote(apostas_part, resultados_df)
        total = sum([p for p in pontos_part if p is not None])
        tabela_classificacao.append({
            "Participante": part['nome'],
            "Total de Pontos": total
        })
        tabela_detalhada.append({
            "Participante": part['nome'],
            "Pontos por Prova": pontos_part
        })
    df_class = pd.DataFrame(tabela_classificacao).sort_values("Total de Pontos", ascending=False).reset_index(drop=True)
    st.subheader("Classificação Geral")
    st.table(df_class)

    st.subheader("Pontuação por Prova")
    provas_nomes = provas_df['nome'].tolist()
    participantes_nomes = [p['Participante'] for p in tabela_detalhada]
    dados_cruzados = {}
    for idx, prova in enumerate(provas_nomes):
        linha = {}
        for part in tabela_detalhada:
            linha[part['Participante']] = part['Pontos por Prova'][idx] if idx < len(part['Pontos por Prova']) and part['Pontos por Prova'][idx] is not None else 0
        dados_cruzados[prova] = linha
    df_cruzada = pd.DataFrame(dados_cruzados).T
    df_cruzada = df_cruzada.reindex(columns=participantes_nomes, fill_value=0)
    st.dataframe(df_cruzada)

    st.subheader("Evolução da Pontuação Acumulada")
    if not df_cruzada.empty:
        fig, ax = plt.subplots()
        for participante in participantes_nomes:
            pontos = df_cruzada[participante].cumsum()
            ax.plot(provas_nomes, pontos, marker='o', label=participante)
        ax.set_xlabel("Prova")
        ax.set_ylabel("Pontuação Acumulada")
        ax.legend()
        st.pyplot(fig)
    else:
        st.info("Sem dados para exibir o gráfico de evolução.")

# --- Regulamento (arquivo externo) ---
if st.session_state['pagina'] == "Regulamento":
    st.title("Regulamento BF1-2025")
    st.markdown(ler_regulamento())

# --- Logout ---
if st.session_state['pagina'] == "Logout" and st.session_state['token']:
    st.session_state['token'] = None
    st.session_state['pagina'] = "Login"
    st.success("Logout realizado com sucesso!")

