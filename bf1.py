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
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    email TEXT UNIQUE,
                    senha_hash TEXT,
                    perfil TEXT,
                    status TEXT DEFAULT 'Ativo')''')
    c.execute('SELECT * FROM usuarios WHERE nome=?', ('Password',))
    if not c.fetchone():
        senha_hash = bcrypt.hashpw('ADMIN'.encode(), bcrypt.gensalt())
        c.execute('INSERT INTO usuarios (nome, email, senha_hash, perfil, status) VALUES (?, ?, ?, ?, ?)',
                  ('Gaspar', 'sansquer@gmail.com', senha_hash, 'master', 'Ativo'))
    c.execute('''CREATE TABLE IF NOT EXISTS equipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS pilotos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    equipe_id INTEGER,
                    FOREIGN KEY(equipe_id) REFERENCES equipes(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS provas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    data TEXT,
                    session_key INTEGER)''')
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
    c.execute('''CREATE TABLE IF NOT EXISTS resultados (
                    prova_id INTEGER PRIMARY KEY,
                    pontos_pilotos TEXT,
                    piloto_11 TEXT,
                    FOREIGN KEY(prova_id) REFERENCES provas(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS log_apostas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    apostador TEXT,
                    ip TEXT,
                    data TEXT,
                    horario TEXT,
                    aposta TEXT)''')
    conn.commit()
    conn.close()

# --- Funções de autenticação e usuários ---
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
def editar_usuario(user_id, nome, email):
    conn = db_connect()
    c = conn.cursor()
    c.execute('UPDATE usuarios SET nome=?, email=? WHERE id=?', (nome, email, user_id))
    conn.commit()
    conn.close()
def excluir_usuario(user_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('DELETE FROM usuarios WHERE id=?', (user_id,))
    conn.commit()
    conn.close()

# --- CRUD Equipes ---
def listar_equipes():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM equipes', conn)
    conn.close()
    return df
def adicionar_equipe(nome):
    conn = db_connect()
    c = conn.cursor()
    c.execute('INSERT INTO equipes (nome) VALUES (?)', (nome,))
    conn.commit()
    conn.close()
def editar_equipe(equipe_id, novo_nome):
    conn = db_connect()
    c = conn.cursor()
    c.execute('UPDATE equipes SET nome=? WHERE id=?', (novo_nome, equipe_id))
    conn.commit()
    conn.close()
def excluir_equipe(equipe_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('DELETE FROM equipes WHERE id=?', (equipe_id,))
    conn.commit()
    conn.close()

# --- CRUD Pilotos ---
def listar_pilotos():
    conn = db_connect()
    df = pd.read_sql('SELECT p.id, p.nome, e.nome as equipe, p.equipe_id FROM pilotos p LEFT JOIN equipes e ON p.equipe_id=e.id', conn)
    conn.close()
    return df
def adicionar_piloto(nome, equipe_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('INSERT INTO pilotos (nome, equipe_id) VALUES (?, ?)', (nome, equipe_id))
    conn.commit()
    conn.close()
def editar_piloto(piloto_id, novo_nome, nova_equipe_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('UPDATE pilotos SET nome=?, equipe_id=? WHERE id=?', (novo_nome, nova_equipe_id, piloto_id))
    conn.commit()
    conn.close()
def excluir_piloto(piloto_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('DELETE FROM pilotos WHERE id=?', (piloto_id,))
    conn.commit()
    conn.close()

# --- CRUD Provas ---
def listar_provas():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM provas', conn)
    conn.close()
    return df
def adicionar_prova(nome, data, session_key):
    conn = db_connect()
    c = conn.cursor()
    c.execute('INSERT INTO provas (nome, data, session_key) VALUES (?, ?, ?)', (nome, data, session_key))
    conn.commit()
    conn.close()
def editar_prova(prova_id, novo_nome, nova_data, nova_session_key):
    conn = db_connect()
    c = conn.cursor()
    c.execute('UPDATE provas SET nome=?, data=?, session_key=? WHERE id=?', (novo_nome, nova_data, nova_session_key, prova_id))
    conn.commit()
    conn.close()
def excluir_prova(prova_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('DELETE FROM provas WHERE id=?', (prova_id,))
    conn.commit()
    conn.close()

# --- CRUD Resultados ---
def salvar_resultado(prova_id, pontos_pilotos, piloto_11):
    conn = db_connect()
    c = conn.cursor()
    c.execute('REPLACE INTO resultados (prova_id, pontos_pilotos, piloto_11) VALUES (?, ?, ?)',
              (prova_id, str(pontos_pilotos), str(piloto_11)))
    conn.commit()
    conn.close()

# --- Log de apostas ---
def get_client_ip():
    try:
        return st.context.ip_address
    except Exception:
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
def consultar_aposta_usuario_prova(usuario_id, prova_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('SELECT pilotos, fichas, piloto_11 FROM apostas WHERE usuario_id=? AND prova_id=?', (usuario_id, prova_id))
    aposta = c.fetchone()
    conn.close()
    return aposta

# --- Navegação por estado ---
st.set_page_config(page_title="Bolão F1 2025", layout="wide")
init_db()

if 'pagina' not in st.session_state:
    st.session_state['pagina'] = "Login"
if 'token' not in st.session_state:
    st.session_state['token'] = None

def logout():
    st.session_state['token'] = None
    st.session_state['pagina'] = "Login"
    st.success("Logout realizado com sucesso!")

def menu_master():
    return [
        "Painel do Participante",
        "Gestão de Usuários",
        "Cadastro de novo participante",
        "Gestão do campeonato",
        "Atualização de resultados",
        "Log de Apostas",
        "Logout"
    ]
def menu_participante():
    return [
        "Painel do Participante",
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

# --- Login e Esqueceu a Senha ---
if st.session_state['pagina'] == "Login":
    st.title("Login")
    if 'esqueceu_senha' not in st.session_state:
        st.session_state['esqueceu_senha'] = False

    if not st.session_state['esqueceu_senha']:
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        col1, col2 = st.columns([2,1])
        with col1:
            if st.button("Entrar"):
                user = autenticar_usuario(email, senha)
                if user:
                    token = generate_token(user[0], user[4], user[5])
                    st.session_state['token'] = token
                    st.session_state['pagina'] = "Painel do Participante"
                    st.success(f"Bem-vindo, {user[1]}!")
                else:
                    st.error("Usuário ou senha inválidos.")
        with col2:
            if st.button("Esqueceu a senha?"):
                st.session_state['esqueceu_senha'] = True
                st.experimental_rerun()
    else:
        st.subheader("Redefinir senha")
        email_reset = st.text_input("Email cadastrado")
        nova_senha = st.text_input("Nova senha", type="password")
        if st.button("Salvar nova senha"):
            user = get_user_by_email(email_reset)
            if user:
                conn = db_connect()
                c = conn.cursor()
                nova_hash = hash_password(nova_senha)
                c.execute('UPDATE usuarios SET senha_hash=? WHERE email=?', (nova_hash, email_reset))
                conn.commit()
                conn.close()
                st.success("Senha redefinida com sucesso! Faça login com a nova senha.")
                st.session_state['esqueceu_senha'] = False
            else:
                st.error("Email não cadastrado.")
        if st.button("Voltar para login"):
            st.session_state['esqueceu_senha'] = False


# --- Menu lateral dinâmico ---
if st.session_state['token']:
    payload = get_payload()
    perfil = payload['perfil']
    if perfil == 'master':
        menu = menu_master()
    else:
        menu = menu_participante()
    escolha = st.sidebar.radio("Menu", menu)
    st.session_state['pagina'] = escolha

# --- Painel do Participante (inclusão/alteração de apostas) ---
if st.session_state['pagina'] == "Painel do Participante" and st.session_state['token']:
    payload = get_payload()
    user = get_user_by_id(payload['user_id'])
    st.title("Painel do Participante")
    st.write(f"Bem-vindo, {user[1]} ({user[3]}) - Status: {user[4]}")
    provas = listar_provas()
    pilotos_df = listar_pilotos()
    if user[4] == "Ativo":
        if len(provas) > 0 and len(pilotos_df) > 2:
            prova_id = st.selectbox("Escolha a prova", provas['id'], format_func=lambda x: provas[provas['id']==x]['nome'].values[0])
            pilotos = pilotos_df['nome'].tolist()
            aposta_existente = consultar_aposta_usuario_prova(user[0], prova_id)
            if aposta_existente:
                pilotos_ant, fichas_ant, piloto_11_ant = aposta_existente
                fichas_ant = list(map(int, fichas_ant.split(',')))
                st.info("Você já apostou nesta prova. Altere e salve para atualizar sua aposta.")
            else:
                fichas_ant = [0]*len(pilotos)
                piloto_11_ant = pilotos[0]
            fichas = []
            st.write("Distribua 15 fichas entre no mínimo 3 pilotos de equipes diferentes:")
            for i, piloto in enumerate(pilotos):
                fichas.append(st.number_input(f"Fichas para {piloto}", min_value=0, max_value=15, value=fichas_ant[i], key=f"fichas_{piloto}"))
            piloto_11 = st.selectbox("Palpite para 11º colocado", pilotos, index=pilotos.index(piloto_11_ant) if aposta_existente else 0)
            if st.button("Salvar aposta"):
                if sum(fichas) == 15 and len([f for f in fichas if f > 0]) >= 3:
                    salvar_aposta(user[0], prova_id, pilotos, fichas, piloto_11)
                    ip = get_client_ip()
                    aposta_str = f"Prova: {prova_id}, Pilotos: {pilotos}, Fichas: {fichas}, 11º: {piloto_11}"
                    registrar_log_aposta(user[1], ip, aposta_str)
                    st.success("Aposta registrada/atualizada!")
                else:
                    st.error("Distribua exatamente 15 fichas entre pelo menos 3 pilotos diferentes.")
        else:
            st.warning("Administração deve cadastrar provas e pilotos antes das apostas.")
    else:
        st.info("Usuário inativo: você só pode visualizar suas apostas anteriores.")
    st.subheader("Minhas apostas")
    apostas = consultar_apostas(user[0])
    st.table(pd.DataFrame(apostas, columns=["Prova", "Data Envio", "Pilotos", "Fichas", "11º"]))

# --- Gestão de Usuários (apenas master) ---
if st.session_state['pagina'] == "Gestão de Usuários" and st.session_state['token']:
    payload = get_payload()
    if payload['perfil'] == 'master':
        st.title("Gestão de Usuários")
        usuarios = listar_usuarios()
        st.dataframe(usuarios)
        st.write("Selecione um usuário para editar, excluir ou alterar status/perfil:")
        usuario_id = st.selectbox("Usuário", usuarios['id'])
        usuario = usuarios[usuarios['id'] == usuario_id].iloc[0]
        novo_nome = st.text_input("Nome", value=usuario['nome'])
        novo_email = st.text_input("Email", value=usuario['email'])
        novo_status = st.selectbox("Status", ["Ativo", "Inativo"], index=0 if usuario['status'] == "Ativo" else 1)
        novo_perfil = st.selectbox("Perfil", ["participante", "admin"], index=0 if usuario['perfil'] == "participante" else 1)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Atualizar usuário"):
                if usuario['nome'] == "Password":
                    st.warning("Não é permitido alterar o status ou perfil do usuário master.")
                else:
                    editar_usuario(usuario_id, novo_nome, novo_email)
                    alterar_status_usuario(usuario_id, novo_status)
                    alterar_perfil_usuario(usuario_id, novo_perfil)
                    st.success("Usuário atualizado!")
        with col2:
            if st.button("Excluir usuário"):
                if usuario['nome'] == "Password":
                    st.warning("Não é permitido excluir o usuário master.")
                else:
                    excluir_usuario(usuario_id)
                    st.success("Usuário excluído!")
        with col3:
            if st.button("Logout"):
                logout()
    else:
        st.warning("Acesso restrito ao usuário master.")

# --- Cadastro de novo participante (apenas master) ---
if st.session_state['pagina'] == "Cadastro de novo participante" and st.session_state['token']:
    payload = get_payload()
    if payload['perfil'] == 'master':
        st.title("Cadastro de novo participante")
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        if st.button("Cadastrar"):
            if cadastrar_usuario(nome, email, senha):
                st.success("Usuário cadastrado com sucesso!")
            else:
                st.error("Email já cadastrado.")
    else:
        st.warning("Acesso restrito ao usuário master.")

# --- Gestão do campeonato (apenas master) ---
if st.session_state['pagina'] == "Gestão do campeonato" and st.session_state['token']:
    payload = get_payload()
    if payload['perfil'] == 'master':
        st.title("Gestão do Campeonato")
        tab1, tab2, tab3 = st.tabs(["Equipes", "Pilotos", "Provas"])

        with tab1:
            st.subheader("Equipes")
            equipes = listar_equipes()
            for idx, row in equipes.iterrows():
                col1, col2, col3 = st.columns([4,2,2])
                with col1:
                    novo_nome = st.text_input(f"Nome equipe {row['id']}", value=row['nome'], key=f"eq_nome{row['id']}")
                with col2:
                    if st.button("Editar", key=f"eq_edit{row['id']}"):
                        editar_equipe(row['id'], novo_nome)
                        st.success("Equipe editada!")
                with col3:
                    if st.button("Excluir", key=f"eq_del{row['id']}"):
                        excluir_equipe(row['id'])
                        st.success("Equipe excluída!")
            nome_equipe = st.text_input("Nome da nova equipe")
            if st.button("Adicionar equipe"):
                adicionar_equipe(nome_equipe)
                st.success("Equipe adicionada!")

        with tab2:
            st.subheader("Pilotos")
            pilotos = listar_pilotos()
            equipes = listar_equipes()
            equipe_nomes = equipes['nome'].tolist()
            for idx, row in pilotos.iterrows():
                col1, col2, col3, col4 = st.columns([4,2,2,2])
                with col1:
                    novo_nome = st.text_input(f"Nome piloto {row['id']}", value=row['nome'], key=f"pl_nome{row['id']}")
                with col2:
                    nova_equipe_nome = st.selectbox(f"Equipe piloto {row['id']}", equipe_nomes, index=equipe_nomes.index(row['equipe']), key=f"pl_eq{row['id']}")
                    nova_equipe_id = equipes[equipes['nome']==nova_equipe_nome]['id'].values[0]
                with col3:
                    if st.button("Editar", key=f"pl_edit{row['id']}"):
                        editar_piloto(row['id'], novo_nome, nova_equipe_id)
                        st.success("Piloto editado!")
                with col4:
                    if st.button("Excluir", key=f"pl_del{row['id']}"):
                        excluir_piloto(row['id'])
                        st.success("Piloto excluído!")
            nome_piloto = st.text_input("Nome do novo piloto")
            equipe_nome = st.selectbox("Equipe do novo piloto", equipe_nomes)
            equipe_id = equipes[equipes['nome']==equipe_nome]['id'].values[0] if equipe_nomes else 1
            if st.button("Adicionar piloto"):
                adicionar_piloto(nome_piloto, equipe_id)
                st.success("Piloto adicionado!")

        with tab3:
            st.subheader("Provas")
            provas = listar_provas()
            for idx, row in provas.iterrows():
                col1, col2, col3, col4, col5 = st.columns([3,3,2,2,2])
                with col1:
                    novo_nome = st.text_input(f"Nome prova {row['id']}", value=row['nome'], key=f"pr_nome{row['id']}")
                with col2:
                    nova_data = st.date_input(f"Data prova {row['id']}", value=pd.to_datetime(row['data']), key=f"pr_data{row['id']}")
                with col3:
                    nova_session_key = st.number_input(f"Session Key {row['id']}", min_value=0, value=row['session_key'], key=f"pr_sk{row['id']}")
                with col4:
                    if st.button("Editar", key=f"pr_edit{row['id']}"):
                        editar_prova(row['id'], novo_nome, nova_data.isoformat(), nova_session_key)
                        st.success("Prova editada!")
                with col5:
                    if st.button("Excluir", key=f"pr_del{row['id']}"):
                        excluir_prova(row['id'])
                        st.success("Prova excluída!")
            nome_prova = st.text_input("Nome da nova prova")
            data_prova = st.date_input("Data da nova prova")
            session_key = st.number_input("Session Key OpenF1", min_value=0, step=1)
            if st.button("Adicionar prova"):
                adicionar_prova(nome_prova, data_prova.isoformat(), session_key)
                st.success("Prova adicionada!")
    else:
        st.warning("Acesso restrito ao usuário master.")

# --- Atualização de resultados (apenas master) ---
if st.session_state['pagina'] == "Atualização de resultados" and st.session_state['token']:
    payload = get_payload()
    if payload['perfil'] == 'master':
        st.title("Atualizar Resultado")
        provas = listar_provas()
        if len(provas) > 0:
            prova_id = st.selectbox("Selecione a prova", provas['id'], format_func=lambda x: provas[provas['id']==x]['nome'].values[0])
            st.write("Você pode buscar automaticamente ou cadastrar manualmente o resultado.")
            if st.button("Buscar resultado OpenF1"):
                session_key = provas[provas['id'] == prova_id]['session_key'].values[0]
                url = f"https://api.openf1.org/v1/classification?session_key={session_key}"
                resp = requests.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    pontos_pilotos = {str(item['driver_number']): item['points'] for item in data}
                    piloto_11 = data[10]['driver_number'] if len(data) > 10 else None
                    salvar_resultado(prova_id, pontos_pilotos, piloto_11)
                    st.success("Resultado atualizado via OpenF1!")
                else:
                    st.error("Erro ao buscar dados da OpenF1.")
            st.write("Ou preencha manualmente:")
            pontos_pilotos = st.text_area("Pontos dos pilotos (ex: {'44':25, '33':18, ...})")
            piloto_11 = st.text_input("Piloto 11º colocado (número)")
            if st.button("Salvar resultado manualmente"):
                try:
                    pontos_dict = eval(pontos_pilotos)
                    salvar_resultado(prova_id, pontos_dict, piloto_11)
                    st.success("Resultado manual salvo!")
                except Exception:
                    st.error("Erro no formato dos pontos dos pilotos.")
        else:
            st.warning("Nenhuma prova cadastrada.")
    else:
        st.warning("Acesso restrito ao usuário master.")

# --- Log de apostas (apenas master) ---
if st.session_state['pagina'] == "Log de Apostas" and st.session_state['token']:
    payload = get_payload()
    if payload['perfil'] == 'master':
        exibir_log_apostas()
    else:
        st.warning("Acesso restrito ao usuário master.")

# --- Logout ---
if st.session_state['pagina'] == "Logout" and st.session_state['token']:
    logout()
