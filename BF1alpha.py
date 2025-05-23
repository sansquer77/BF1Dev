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

def ler_regulamento(arquivo="Regulamento.txt"):
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
def get_faltas_usuario(user_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('SELECT faltas FROM usuarios WHERE id=?', (user_id,))
    faltas = c.fetchone()
    conn.close()
    return faltas[0] if faltas else 0
def set_faltas_usuario(user_id, faltas):
    conn = db_connect()
    c = conn.cursor()
    c.execute('UPDATE usuarios SET faltas=? WHERE id=?', (faltas, user_id))
    conn.commit()
    conn.close()
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
def autenticar_usuario(email, senha):
    user = get_user_by_email(email)
    if user and check_password(senha, user[3]):
        return user
    return None
def listar_usuarios():
    conn = db_connect()
    df = pd.read_sql('SELECT id, nome, email, perfil, status, faltas FROM usuarios', conn)
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

def listar_pilotos():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM pilotos', conn)
    conn.close()
    return df
def adicionar_piloto(nome, equipe):
    conn = db_connect()
    c = conn.cursor()
    c.execute('INSERT INTO pilotos (nome, equipe) VALUES (?, ?)', (nome, equipe))
    conn.commit()
    conn.close()
def editar_piloto(piloto_id, novo_nome, nova_equipe):
    conn = db_connect()
    c = conn.cursor()
    c.execute('UPDATE pilotos SET nome=?, equipe=? WHERE id=?', (novo_nome, nova_equipe, piloto_id))
    conn.commit()
    conn.close()
def excluir_piloto(piloto_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('DELETE FROM pilotos WHERE id=?', (piloto_id,))
    conn.commit()
    conn.close()

def listar_provas():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM provas', conn)
    conn.close()
    return df
def adicionar_prova(nome, data):
    conn = db_connect()
    c = conn.cursor()
    c.execute('INSERT INTO provas (nome, data) VALUES (?, ?)', (nome, data))
    conn.commit()
    conn.close()
def editar_prova(prova_id, novo_nome, nova_data):
    conn = db_connect()
    c = conn.cursor()
    c.execute('UPDATE provas SET nome=?, data=? WHERE id=?', (novo_nome, nova_data, prova_id))
    conn.commit()
    conn.close()
def excluir_prova(prova_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('DELETE FROM provas WHERE id=?', (prova_id,))
    conn.commit()
    conn.close()

def salvar_resultado_manual(prova_id, posicoes_dict):
    conn = db_connect()
    c = conn.cursor()
    c.execute('REPLACE INTO resultados (prova_id, posicoes) VALUES (?, ?)',
              (prova_id, str(posicoes_dict)))
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

def exibir_log_apostas(user_id=None, is_master=False):
    conn = db_connect()
    if is_master:
        df = pd.read_sql('SELECT * FROM log_apostas', conn)
    else:
        nome = get_user_by_id(user_id)[1]
        df = pd.read_sql('SELECT * FROM log_apostas WHERE apostador=?', conn, params=(nome,))
    conn.close()
    st.subheader("Log de Apostas")
    st.dataframe(df)

def salvar_aposta(usuario_id, prova_id, pilotos, fichas, piloto_11, nome_prova, automatica=0):
    conn = db_connect()
    c = conn.cursor()
    data_envio = datetime.now().isoformat()
    c.execute('DELETE FROM apostas WHERE usuario_id=? AND prova_id=?', (usuario_id, prova_id))
    c.execute('INSERT INTO apostas (usuario_id, prova_id, data_envio, pilotos, fichas, piloto_11, nome_prova, automatica) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
              (usuario_id, prova_id, data_envio, ','.join(pilotos), ','.join(map(str, fichas)), piloto_11, nome_prova, automatica))
    conn.commit()
    conn.close()

def consultar_apostas(usuario_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('SELECT rowid, nome_prova, prova_id, data_envio, pilotos, fichas, piloto_11, automatica FROM apostas WHERE usuario_id=?', (usuario_id,))
    apostas = c.fetchall()
    conn.close()
    return apostas
def consultar_aposta_usuario_prova(usuario_id, prova_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('SELECT pilotos, fichas, piloto_11, automatica FROM apostas WHERE usuario_id=? AND prova_id=?', (usuario_id, prova_id))
    aposta = c.fetchone()
    conn.close()
    return aposta

def consultar_resultado_prova(prova_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('SELECT posicoes FROM resultados WHERE prova_id=?', (prova_id,))
    res = c.fetchone()
    conn.close()
    if res:
        return ast.literal_eval(res[0])
    return None

def calcular_pontuacao_aposta(prova_id, pilotos_apostados, fichas_apostadas, piloto_11_apostado, faltas=0, automatica=0):
    resultado = consultar_resultado_prova(prova_id)
    if not resultado:
        return None
    pontos_f1 = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
    pontos = 0
    for idx, (piloto, ficha) in enumerate(zip(pilotos_apostados, fichas_apostadas)):
        for pos, nome_resultado in resultado.items():
            pos_int = int(pos)
            if pos_int <= 10 and nome_resultado == piloto:
                pontos += ficha * pontos_f1[pos_int-1]
    if '11' in resultado and resultado['11'] == piloto_11_apostado:
        pontos += 25
    # Desconto para faltas a partir da segunda aposta automática
    if automatica >= 2:
        pontos = int(pontos * 0.75)
    return pontos

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

# --- Login, Esqueceu a Senha e Criar Usuário Inativo ---
# (bloco igual ao anterior)

# --- Menu lateral dinâmico ---
# (bloco igual ao anterior)

# --- Gestão de Usuários (apenas master) ---
if st.session_state['pagina'] == "Gestão de Usuários" and st.session_state['token']:
    payload = get_payload()
    if payload['perfil'] == 'master':
        st.title("Gestão de Usuários")
        usuarios = listar_usuarios()
        if len(usuarios) == 0:
            st.info("Nenhum usuário cadastrado.")
        else:
            st.dataframe(usuarios)
            st.write("Selecione um usuário para editar, excluir ou alterar status/perfil:")
            usuario_id = st.selectbox("Usuário", usuarios['id'])
            usuario = usuarios[usuarios['id'] == usuario_id].iloc[0]
            novo_nome = st.text_input("Nome", value=usuario['nome'], key="edit_nome")
            novo_email = st.text_input("Email", value=usuario['email'], key="edit_email")
            novo_status = st.selectbox("Status", ["Ativo", "Inativo"], index=0 if usuario['status'] == "Ativo" else 1, key="edit_status")
            novo_perfil = st.selectbox("Perfil", ["participante", "admin"], index=0 if usuario['perfil'] == "participante" else 1, key="edit_perfil")
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

# --- Gestão do Campeonato (Pilotos e Provas) ---
# (bloco igual ao anterior)

# --- Gestão de Apostas (apenas master/admin) ---
if st.session_state['pagina'] == "Gestão de Apostas" and st.session_state['token']:
    payload = get_payload()
    if payload['perfil'] in ['master', 'admin']:
        st.title("Gestão de Apostas")
        provas = listar_provas()
        usuarios = listar_usuarios()
        participantes = usuarios[usuarios['status'] == 'Ativo']
        provas = provas.sort_values('data')
        tabs = st.tabs(participantes['nome'].tolist())
        for idx, part in enumerate(participantes.itertuples()):
            with tabs[idx]:
                st.subheader(f"Apostas de {part.nome}")
                apostas = consultar_apostas(part.id)
                apostas_dict = {int(ap[2]): ap for ap in apostas}  # prova_id: aposta
                faltas = 0
                for _, prova in provas.iterrows():
                    st.write(f"**Prova:** {prova['nome']} ({prova['data']})")
                    if prova['id'] in apostas_dict:
                        ap = apostas_dict[prova['id']]
                        st.success(f"Aposta registrada em {ap[3][:16]}: Pilotos: {ap[4]}, Fichas: {ap[5]}, 11º: {ap[6]}")
                    else:
                        faltas += 1
                        st.warning("Sem aposta registrada.")
                        if st.button(f"Gerar aposta automática para {prova['nome']}", key=f"auto_{part.id}_{prova['id']}"):
                            idx_prova = provas[provas['id']==prova['id']].index[0]
                            if idx_prova == 0:
                                st.error("Não há prova anterior para copiar a aposta.")
                            else:
                                prova_ant_id = provas.iloc[idx_prova-1]['id']
                                ap_ant = apostas_dict.get(prova_ant_id)
                                if not ap_ant:
                                    st.error("Participante não tem aposta anterior para copiar.")
                                else:
                                    pilotos_ant = ap_ant[4].split(",")
                                    fichas_ant = list(map(int, ap_ant[5].split(",")))
                                    piloto_11_ant = ap_ant[6]
                                    # Conta apostas automáticas já feitas
                                    num_auto = len([a for a in apostas if a[7] and int(a[7]) == 1])
                                    salvar_aposta(part.id, prova['id'], pilotos_ant, fichas_ant, piloto_11_ant, prova['nome'], automatica=num_auto+1)
                                    set_faltas_usuario(part.id, faltas)
                                    st.success("Aposta automática gerada!")
    else:
        st.warning("Acesso restrito ao administrador/master.")

# --- Painel do Participante (com destaque para apostas automáticas) ---
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
            nome_prova = provas[provas['id']==prova_id]['nome'].values[0]
            aposta_existente = consultar_aposta_usuario_prova(user[0], prova_id)
            pilotos_apostados_ant = []
            fichas_ant = []
            piloto_11_ant = ""
            if aposta_existente:
                pilotos_ant, fichas_ant_list, piloto_11_ant, _ = aposta_existente
                pilotos_apostados_ant = pilotos_ant.split(",")
                fichas_ant = list(map(int, fichas_ant_list.split(",")))
            else:
                fichas_ant = []
                piloto_11_ant = ""
            st.write("Escolha seus pilotos e distribua 15 fichas entre eles (mínimo 3 pilotos de equipes diferentes):")
            pilotos = pilotos_df['nome'].tolist()
            equipes = pilotos_df['equipe'].tolist()
            pilotos_equipe = dict(zip(pilotos, equipes))
            max_linhas = 5
            pilotos_aposta = []
            fichas_aposta = []
            for i in range(max_linhas):
                mostrar = False
                if i < 3:
                    mostrar = True
                elif i == 3 and len([p for p in pilotos_aposta if p != "Nenhum"]) == 3 and sum(fichas_aposta) < 15:
                    mostrar = True
                elif i == 4 and len([p for p in pilotos_aposta if p != "Nenhum"]) == 4 and sum(fichas_aposta) < 15:
                    mostrar = True
                if mostrar:
                    col1, col2 = st.columns([3,1])
                    with col1:
                        piloto_sel = st.selectbox(
                            f"Piloto {i+1}",
                            ["Nenhum"] + pilotos,
                            index=(pilotos.index(pilotos_apostados_ant[i]) + 1) if len(pilotos_apostados_ant) > i and pilotos_apostados_ant[i] in pilotos else 0,
                            key=f"piloto_aposta_{i}"
                        )
                    with col2:
                        if piloto_sel != "Nenhum":
                            valor_ficha = st.number_input(
                                f"Fichas para {piloto_sel}", min_value=0, max_value=15,
                                value=fichas_ant[i] if len(fichas_ant) > i else 0,
                                key=f"fichas_aposta_{i}"
                            )
                            pilotos_aposta.append(piloto_sel)
                            fichas_aposta.append(valor_ficha)
                        else:
                            pilotos_aposta.append("Nenhum")
                            fichas_aposta.append(0)
            pilotos_validos = [p for p in pilotos_aposta if p != "Nenhum"]
            fichas_validas = [f for i, f in enumerate(fichas_aposta) if pilotos_aposta[i] != "Nenhum"]
            equipes_apostadas = [pilotos_equipe[p] for p in pilotos_validos]
            total_fichas = sum(fichas_validas)
            pilotos_11_opcoes = [p for p in pilotos if p not in pilotos_validos]
            if not pilotos_11_opcoes:
                pilotos_11_opcoes = pilotos
            piloto_11 = st.selectbox(
                "Palpite para 11º colocado", pilotos_11_opcoes,
                index=pilotos_11_opcoes.index(piloto_11_ant) if piloto_11_ant in pilotos_11_opcoes else 0
            )
            erro = None
            if st.button("Efetivar Aposta"):
                if len(set(pilotos_validos)) != len(pilotos_validos):
                    erro = "Não é permitido apostar em dois pilotos iguais."
                elif len(set(equipes_apostadas)) != len(equipes_apostadas):
                    erro = "Não é permitido apostar em dois pilotos da mesma equipe."
                elif len(pilotos_validos) < 3:
                    erro = "Você deve apostar em pelo menos 3 pilotos de equipes diferentes."
                elif total_fichas != 15:
                    erro = "A soma das fichas deve ser exatamente 15."
                elif piloto_11 in pilotos_validos:
                    erro = "O 11º colocado não pode ser um dos pilotos apostados."
                if erro:
                    st.error(erro)
                else:
                    salvar_aposta(
                        user[0], prova_id, pilotos_validos,
                        fichas_validas,
                        piloto_11, nome_prova, automatica=0
                    )
                    aposta_str = f"Prova: {nome_prova}, Pilotos: {pilotos_validos}, Fichas: {fichas_validas}, 11º: {piloto_11}"
                    registrar_log_aposta(user[1], aposta_str, nome_prova)
                    st.success("Aposta registrada/atualizada!")
        else:
            st.warning("Administração deve cadastrar provas e pilotos antes das apostas.")
    else:
        st.info("Usuário inativo: você só pode visualizar suas apostas anteriores.")
    st.subheader("Minhas apostas")
    apostas = consultar_apostas(user[0])
    if apostas:
        apostas_lista = []
        provas = listar_provas().sort_values('data')
        auto_count = 0
        for idx, (rowid, nome_prova, prova_id, data_envio, pilotos, fichas, piloto_11, automatica) in enumerate(apostas, start=1):
            pilotos_lst = pilotos.split(",")
            fichas_lst = list(map(int, fichas.split(",")))
            pontos = calcular_pontuacao_aposta(prova_id, pilotos_lst, fichas_lst, piloto_11, faltas=auto_count, automatica=int(automatica))
            cor = ""
            if int(automatica) == 1:
                auto_count += 1
                cor = "background-color: yellow"
            elif int(automatica) >= 2:
                auto_count += 1
                cor = "background-color: red"
            apostas_lista.append({
                "#": idx,
                "Prova": nome_prova,
                "Data Envio": data_envio,
                "Pilotos": pilotos,
                "Fichas": fichas,
                "11º": piloto_11,
                "Pontuação": pontos if pontos is not None else "Aguardando resultado",
                "Cor": cor
            })
        df_apostas = pd.DataFrame(apostas_lista)
        def colorir_linha(row):
            return [row["Cor"]] * len(row)
        st.dataframe(df_apostas[["#", "Prova", "Data Envio", "Pilotos", "Fichas", "11º", "Pontuação"]].style.apply(colorir_linha, axis=1))
    else:
        st.info("Nenhuma aposta registrada.")

# --- Classificação ---
if st.session_state['pagina'] == "Classificação" and st.session_state['token']:
    st.title("Classificação Geral do Bolão")
    usuarios = listar_usuarios()
    provas = listar_provas()
    participantes = usuarios[usuarios['status'] == 'Ativo']
    participantes = participantes.reset_index(drop=True)
    provas = provas.sort_values('data')
    tabela_classificacao = []
    tabela_detalhada = []

    for idx, part in participantes.iterrows():
        total = 0
        pontos_por_prova = []
        auto_count = 0
        for _, prova in provas.iterrows():
            apostas = consultar_apostas(part['id'])
            pontos = 0
            for ap in apostas:
                _, nome_prova, prova_id, _, pilotos, fichas, piloto_11, automatica = ap
                if prova_id == prova['id']:
                    pilotos_lst = pilotos.split(",")
                    fichas_lst = list(map(int, fichas.split(",")))
                    p = calcular_pontuacao_aposta(prova_id, pilotos_lst, fichas_lst, piloto_11, faltas=auto_count, automatica=int(automatica))
                    if int(automatica) >= 1:
                        auto_count += 1
                    pontos = p if p is not None else 0
                    break
            pontos_por_prova.append(pontos)
            total += pontos
        tabela_classificacao.append({
            "Participante": part['nome'],
            "Total de Pontos": total
        })
        tabela_detalhada.append({
            "Participante": part['nome'],
            "Pontos por Prova": pontos_por_prova
        })

    df_class = pd.DataFrame(tabela_classificacao).sort_values("Total de Pontos", ascending=False).reset_index(drop=True)
    st.subheader("Classificação Geral")
    st.table(df_class)

    # 2. Tabela cruzada: provas x participantes
    st.subheader("Pontuação por Prova")
    provas_nomes = provas['nome'].tolist()
    participantes_nomes = [p['Participante'] for p in tabela_detalhada]
    dados_cruzados = {}
    for idx, prova in enumerate(provas_nomes):
        linha = {}
        for part in tabela_detalhada:
            linha[part['Participante']] = part['Pontos por Prova'][idx] if idx < len(part['Pontos por Prova']) else 0
        dados_cruzados[prova] = linha
    df_cruzada = pd.DataFrame(dados_cruzados).T
    df_cruzada = df_cruzada.reindex(columns=participantes_nomes, fill_value=0)
    st.dataframe(df_cruzada)

    # 3. Gráfico de evolução (corrigido para participantes com zero)
    st.subheader("Evolução da Pontuação Acumulada")
    fig, ax = plt.subplots()
    for participante in participantes_nomes:
        pontos = df_cruzada[participante].cumsum()
        ax.plot(provas_nomes, pontos, marker='o', label=participante)
    ax.set_xlabel("Prova")
    ax.set_ylabel("Pontuação Acumulada")
    ax.legend()
    st.pyplot(fig)

# --- Atualização de resultados (apenas manual, tabela de posições) ---
# (bloco igual ao anterior)

# --- Log de apostas (visível para todos, mas com filtros) ---
# (bloco igual ao anterior)

# --- Regulamento ---
if st.session_state['pagina'] == "Regulamento":
    st.title("Regulamento BF1-2025")
    st.markdown(ler_regulamento())

# --- Logout ---
if st.session_state['pagina'] == "Logout" and st.session_state['token']:
    logout()
