import streamlit as st
import sqlite3
import bcrypt
import jwt
import pandas as pd
from datetime import datetime, timedelta
import requests

DB_PATH = 'bolao_f1.db'
JWT_SECRET = 'sua_chave_secreta_supersegura'
JWT_EXP_MINUTES = 120

def db_connect():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = db_connect()
    c = conn.cursor()
    # Usuários
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    email TEXT UNIQUE,
                    senha_hash TEXT,
                    perfil TEXT,
                    status TEXT DEFAULT 'Ativo')''')
    # Usuário master
    c.execute('SELECT * FROM usuarios WHERE nome=?', ('Password',))
    if not c.fetchone():
        senha_hash = bcrypt.hashpw('ADMIN'.encode(), bcrypt.gensalt())
        c.execute('INSERT INTO usuarios (nome, email, senha_hash, perfil, status) VALUES (?, ?, ?, ?, ?)',
                  ('Password', 'master@bolao.com', senha_hash, 'master', 'Ativo'))
    # Equipes
    c.execute('''CREATE TABLE IF NOT EXISTS equipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE)''')
    # Pilotos
    c.execute('''CREATE TABLE IF NOT EXISTS pilotos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    equipe_id INTEGER,
                    FOREIGN KEY(equipe_id) REFERENCES equipes(id))''')
    # Provas
    c.execute('''CREATE TABLE IF NOT EXISTS provas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    data TEXT,
                    session_key INTEGER)''')
    # Apostas
    c.execute('''CREATE TABLE IF NOT EXISTS apostas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER,
                    prova_id INTEGER,
                    data_envio TEXT,
                    pilotos TEXT,
                    fichas TEXT,
                    piloto_11 TEXT,
                    FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
                    FOREIGN KEY(prova_id) REFERENCES provas(id))''')
    # Resultados
    c.execute('''CREATE TABLE IF NOT EXISTS resultados (
                    prova_id INTEGER PRIMARY KEY,
                    pontos_pilotos TEXT,
                    piloto_11 TEXT,
                    FOREIGN KEY(prova_id) REFERENCES provas(id))''')
    # Log de apostas
    c.execute('''CREATE TABLE IF NOT EXISTS log_apostas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    apostador TEXT,
                    ip TEXT,
                    data TEXT,
                    horario TEXT,
                    aposta TEXT)''')
    conn.commit()
    conn.close()

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
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def decode_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None

def get_user_by_email(email):
    conn = db_connect()
    c = conn.cursor()
    c.execute('SELECT id, nome, email, senha_hash, perfil, status FROM usuarios WHERE email=?', (email,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('SELECT id, nome, email, perfil, status FROM usuarios WHERE id=?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def require_auth():
    token = st.session_state.get('token')
    if not token:
        st.error("Faça login para acessar esta área.")
        st.stop()
    payload = decode_token(token)
    if not payload:
        st.error("Sessão expirada. Faça login novamente.")
        st.session_state['token'] = None
        st.stop()
    return payload

def require_admin():
    payload = require_auth()
    if payload['perfil'] not in ['admin', 'master']:
        st.error("Acesso restrito ao administrador.")
        st.stop()
    return payload

def cadastrar_usuario(nome, email, senha, perfil='participante'):
    conn = db_connect()
    c = conn.cursor()
    try:
        senha_hash = hash_password(senha)
        c.execute('INSERT INTO usuarios (nome, email, senha_hash, perfil, status) VALUES (?, ?, ?, ?, ?)', 
                  (nome, email, senha_hash, perfil, 'Ativo'))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def autenticar_usuario(email, senha):
    user = get_user_by_email(email)
    if user and check_password(senha, user[3]):
        return user
    return None

def listar_usuarios():
    conn = db_connect()
    df = pd.read_sql('SELECT id, nome, email, perfil, status FROM usuarios', conn)
    conn.close()
    return df

def alterar_status_usuario(user_id, novo_status):
    conn = db_connect()
    c = conn.cursor()
    c.execute('UPDATE usuarios SET status=? WHERE id=?', (novo_status, user_id))
    conn.commit()
    conn.close()

def alterar_perfil_usuario(user_id, novo_perfil):
    conn = db_connect()
    c = conn.cursor()
    c.execute('UPDATE usuarios SET perfil=? WHERE id=?', (novo_perfil, user_id))
    conn.commit()
    conn.close()

def listar_equipes():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM equipes', conn)
    conn.close()
    return df

def listar_pilotos():
    conn = db_connect()
    df = pd.read_sql('SELECT p.id, p.nome, e.nome as equipe FROM pilotos p LEFT JOIN equipes e ON p.equipe_id=e.id', conn)
    conn.close()
    return df

def listar_provas():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM provas', conn)
    conn.close()
    return df

def adicionar_equipe(nome):
    conn = db_connect()
    c = conn.cursor()
    c.execute('INSERT INTO equipes (nome) VALUES (?)', (nome,))
    conn.commit()
    conn.close()

def adicionar_piloto(nome, equipe_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('INSERT INTO pilotos (nome, equipe_id) VALUES (?, ?)', (nome, equipe_id))
    conn.commit()
    conn.close()

def adicionar_prova(nome, data, session_key):
    conn = db_connect()
    c = conn.cursor()
    c.execute('INSERT INTO provas (nome, data, session_key) VALUES (?, ?, ?)', (nome, data, session_key))
    conn.commit()
    conn.close()

def atualizar_resultado_openf1(session_key):
    url = f"https://api.openf1.org/v1/classification?session_key={session_key}"
    resp = requests.get(url)
    if resp.status_code != 200:
        st.error("Erro ao buscar dados da OpenF1.")
        return None, None
    data = resp.json()
    pontos_pilotos = {str(item['driver_number']): item['points'] for item in data}
    piloto_11 = data[10]['driver_number'] if len(data) > 10 else None
    return pontos_pilotos, piloto_11

def salvar_resultado(prova_id, pontos_pilotos, piloto_11):
    conn = db_connect()
    c = conn.cursor()
    c.execute('REPLACE INTO resultados (prova_id, pontos_pilotos, piloto_11) VALUES (?, ?, ?)',
              (prova_id, str(pontos_pilotos), str(piloto_11)))
    conn.commit()
    conn.close()

def get_client_ip():
    try:
        return st.context.ip_address
    except Exception:
        try:
            from streamlit.runtime.scriptrunner import get_script_run_ctx
            from streamlit import runtime
            ctx = get_script_run_ctx()
            if ctx is not None:
                session_info = runtime.get_instance().get_client(ctx.session_id)
                if session_info is not None:
                    return session_info.request.remote_ip
        except Exception:
            return "N/A"
    return "N/A"

def registrar_log_aposta(apostador, ip, aposta):
    conn = db_connect()
    c = conn.cursor()
    agora = datetime.now()
    data = agora.strftime('%Y-%m-%d')
    horario = agora.strftime('%H:%M:%S')
    c.execute('INSERT INTO log_apostas (apostador, ip, data, horario, aposta) VALUES (?, ?, ?, ?, ?)',
              (apostador, ip, data, horario, aposta))
    conn.commit()
    conn.close()

def exibir_log_apostas():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM log_apostas', conn)
    conn.close()
    st.subheader("Log de Apostas")
    st.dataframe(df)

def salvar_aposta(usuario_id, prova_id, pilotos, fichas, piloto_11):
    conn = db_connect()
    c = conn.cursor()
    data_envio = datetime.now().isoformat()
    c.execute('DELETE FROM apostas WHERE usuario_id=? AND prova_id=?', (usuario_id, prova_id))
    c.execute('INSERT INTO apostas (usuario_id, prova_id, data_envio, pilotos, fichas, piloto_11) VALUES (?, ?, ?, ?, ?, ?)',
              (usuario_id, prova_id, data_envio, ','.join(pilotos), ','.join(map(str, fichas)), piloto_11))
    conn.commit()
    conn.close()

def consultar_apostas(usuario_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('SELECT prova_id, data_envio, pilotos, fichas, piloto_11 FROM apostas WHERE usuario_id=?', (usuario_id,))
    apostas = c.fetchall()
    conn.close()
    return apostas

st.set_page_config(page_title="Bolão F1 2025", layout="wide")
init_db()

menu = st.sidebar.selectbox("Menu", ["Login", "Cadastro", "Painel", "Gestão Usuários", "Gestão Campeonato", "Atualizar Resultado", "Log de Apostas"])

if menu == "Login":
    st.title("Login")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        user = autenticar_usuario(email, senha)
        if user:
            token = generate_token(user[0], user[4], user[5])
            st.session_state['token'] = token
            st.success(f"Bem-vindo, {user[1]}!")
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha inválidos.")

elif menu == "Cadastro":
    st.title("Cadastro de novo participante")
    nome = st.text_input("Nome")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Cadastrar"):
        if cadastrar_usuario(nome, email, senha):
            st.success("Usuário cadastrado com sucesso!")
        else:
            st.error("Email já cadastrado.")

elif menu == "Painel":
    payload = require_auth()
    user = get_user_by_id(payload['user_id'])
    st.title("Painel do Participante")
    st.write(f"Bem-vindo, {user[1]} ({user[3]}) - Status: {user[4]}")
    provas = listar_provas()
    pilotos_df = listar_pilotos()
    if user[4] == "Ativo":
        if len(provas) > 0 and len(pilotos_df) > 2:
            prova_id = st.selectbox("Escolha a prova", provas['id'])
            pilotos = pilotos_df['nome'].tolist()
            fichas = []
            st.write("Distribua 15 fichas entre no mínimo 3 pilotos de equipes diferentes:")
            for piloto in pilotos:
                fichas.append(st.number_input(f"Fichas para {piloto}", min_value=0, max_value=15, value=0, key=piloto))
            piloto_11 = st.selectbox("Palpite para 11º colocado", pilotos)
            if st.button("Enviar aposta"):
                if sum(fichas) == 15 and len([f for f in fichas if f > 0]) >= 3:
                    salvar_aposta(user[0], prova_id, pilotos, fichas, piloto_11)
                    ip = get_client_ip()
                    aposta_str = f"Prova: {prova_id}, Pilotos: {pilotos}, Fichas: {fichas}, 11º: {piloto_11}"
                    registrar_log_aposta(user[1], ip, aposta_str)
                    st.success("Aposta registrada e logada!")
                else:
                    st.error("Distribua exatamente 15 fichas entre pelo menos 3 pilotos diferentes.")
        else:
            st.warning("Administração deve cadastrar provas e pilotos antes das apostas.")
    else:
        st.info("Usuário inativo: você só pode visualizar suas apostas anteriores.")
    st.subheader("Minhas apostas")
    apostas = consultar_apostas(user[0])
    st.table(pd.DataFrame(apostas, columns=["Prova", "Data Envio", "Pilotos", "Fichas", "11º"]))

elif menu == "Gestão Usuários":
    payload = require_admin()
    st.title("Gestão de Usuários")
    usuarios = listar_usuarios()
    st.dataframe(usuarios)
    st.write("Selecione um usuário para alterar status ou perfil:")
    usuario_id = st.selectbox("Usuário", usuarios['id'])
    usuario = usuarios[usuarios['id'] == usuario_id].iloc[0]
    novo_status = st.selectbox("Status", ["Ativo", "Inativo"], index=0 if usuario['status'] == "Ativo" else 1)
    novo_perfil = st.selectbox("Perfil", ["participante", "admin"], index=0 if usuario['perfil'] == "participante" else 1)
    if st.button("Atualizar usuário"):
        if usuario['nome'] == "Password":
            st.warning("Não é permitido alterar o status ou perfil do usuário master.")
        else:
            alterar_status_usuario(usuario_id, novo_status)
            alterar_perfil_usuario(usuario_id, novo_perfil)
            st.success("Usuário atualizado!")
            st.experimental_rerun()

elif menu == "Gestão Campeonato":
    require_admin()
    st.title("Gestão do Campeonato")
    tab1, tab2, tab3 = st.tabs(["Equipes", "Pilotos", "Provas"])

    with tab1:
        st.subheader("Equipes")
        equipes = listar_equipes()
        st.dataframe(equipes)
        nome_equipe = st.text_input("Nome da nova equipe")
        if st.button("Adicionar equipe"):
            adicionar_equipe(nome_equipe)
            st.success("Equipe adicionada!")
            st.experimental_rerun()

    with tab2:
        st.subheader("Pilotos")
        pilotos = listar_pilotos()
        st.dataframe(pilotos)
        nome_piloto = st.text_input("Nome do piloto")
        equipes = listar_equipes()
        equipe_id = st.selectbox("Equipe", equipes['id'])
        if st.button("Adicionar piloto"):
            adicionar_piloto(nome_piloto, equipe_id)
            st.success("Piloto adicionado!")
            st.experimental_rerun()

    with tab3:
        st.subheader("Provas")
        provas = listar_provas()
        st.dataframe(provas)
        nome_prova = st.text_input("Nome da prova")
        data_prova = st.date_input("Data da prova")
        session_key = st.number_input("Session Key OpenF1", min_value=0, step=1)
        if st.button("Adicionar prova"):
            adicionar_prova(nome_prova, data_prova.isoformat(), session_key)
            st.success("Prova adicionada!")
            st.experimental_rerun()

elif menu == "Atualizar Resultado":
    require_admin()
    st.title("Atualizar Resultado via OpenF1")
    provas = listar_provas()
    if len(provas) > 0:
        prova_id = st.selectbox("Selecione a prova", provas['id'])
        session_key = provas[provas['id'] == prova_id]['session_key'].values[0]
        if st.button("Buscar e salvar resultado"):
            pontos_pilotos, piloto_11 = atualizar_resultado_openf1(session_key)
            if pontos_pilotos:
                salvar_resultado(prova_id, pontos_pilotos, piloto_11)
                st.success("Resultado atualizado com sucesso!")
    else:
        st.warning("Nenhuma prova cadastrada.")

elif menu == "Log de Apostas":
    payload = require_admin()
    exibir_log_apostas()
