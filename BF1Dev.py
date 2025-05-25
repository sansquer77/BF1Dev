import streamlit as st
import sqlite3
import bcrypt
import jwt as pyjwt
import pandas as pd
from datetime import datetime, timedelta
import ast
import matplotlib.pyplot as plt

DB_PATH = 'bolao_f1Dev.db'
JWT_SECRET = 'sua_chave_secreta_supersegura'
JWT_EXP_MINUTES = 120

REGULAMENTO = """
REGULAMENTO BF1-2025

O BF1-2025 terá início, oficialmente, em 16 de março, no dia do GP da Austrália e término em 07 de dezembro, quando será disputado o último GP, o de Abu Dhabi.

Inscrições para o BF1 estão liberadas a partir de qualquer etapa.
A inscrição é de R$200,00 a ser pago no ato da inscrição via PIX.
Em caso de desistência da participação durante o campeonato a taxa de inscrição não será devolvida.
Cabe ressaltar, que a pontuação do novo participante será 80% da pontuação do participante mais mal colocado no bolão no momento da inscrição e terá 0 pontos na aposta de campeão, caso ocorra após o início do campeonato.

As apostas dos participantes devem ser efetuadas até o horário programado da corrida e compartilhadas via formulário padrão que está no grupo do WhatsApp. Fica facultado ao participante a geração de um print da tela do aplicativo com a aposta e o horário da mensagem para futuras validações, mas cabe ressaltar que a ferramenta possui um Time Stamp do horário de envio das mensagens.

a. O participante pode enviar quantas apostas quiser até o horário limite, sendo válida a última enviada.  
b. Apostas registradas após o horário da largada, por exemplo 09:01 sendo a corrida às 09h serão desconsideradas.  
c. Os horários das corridas deste ano são:

Grande Prêmio | Data | Horário  
--- | --- | ---  
1  Grande Prêmio da Austrália           | 16 de março         | 01:00  
2  Grande Prêmio da China Sprint        | 22 de março         | 00:00  
3  Grande Prêmio da China               | 23 de março         | 04:00  
4  Grande Prêmio do Japão               | 6 de abril          | 02:00  
5  Grande Prêmio do Bahrain             | 13 de abril         | 12:00  
6  Grande Prêmio da Arábia Saudita      | 20 de abril         | 14:00  
7  Grande Prêmio de Miami Sprint        | 3 de maio           | 13:00  
8  Grande Prêmio de Miami               | 4 de maio           | 17:00  
9  Grande Prêmio da Emília-Romanha      | 18 de maio          | 10:00  
10 Grande Prêmio de Mônaco              | 25 de maio          | 10:00  
11 Grande Prêmio da Espanha             | 1 de junho          | 10:00  
12 Grande Prêmio do Canadá              | 15 de junho         | 15:00  
13 Grande Prêmio da Áustria             | 29 de junho         | 10:00  
14 Grande Prêmio da Grã-Bretanha        | 6 de julho          | 11:00  
15 Grande Prêmio da Bélgica Sprint      | 26 de julho         | 07:00  
16 Grande Prêmio da Bélgica             | 27 de julho         | 10:00  
17 Grande Prêmio da Hungria             | 3 de agosto         | 10:00  
18 Grande Prêmio dos Países Baixos      | 31 de agosto        | 10:00  
19 Grande Prêmio da Itália              | 7 de setembro       | 10:00  
20 Grande Prêmio do Azerbaijão          | 21 de setembro      | 08:00  
21 Grande Prêmio de Singapura           | 5 de outubro        | 09:00  
22 Grande Prêmio dos EUA Sprint         | 18 de outubro       | 14:00  
23 Grande Prêmio dos EUA                | 19 de outubro       | 16:00  
24 Grande Prêmio da Cidade do México    | 26 de outubro       | 17:00  
25 Grande Prêmio de São Paulo Sprint    | 8 de novembro       | 11:00  
26 Grande Prêmio de São Paulo           | 9 de novembro       | 14:00  
27 Grande Prêmio de Las Vegas           | 22 de novembro      | 01:00  
28 Grande Prêmio do Catar Sprint        | 29 de novembro      | 11:00  
29 Grande Prêmio do Catar               | 30 de novembro      | 13:00  
30 Grande Prêmio de Abu Dhabi           | 7 de dezembro       | 10:00  

O participante que não efetuar a sua aposta ATÉ O PRAZO DEFINIDO DO ITEM-3, irá concorrer com a mesma aposta da última corrida.  
Quando se tratar da primeira vez que a aposta não for feita, e apenas neste caso, será computado 100% dos pontos.  
Caso o apostador não aposte na primeira corrida do campeonato, como não haverá base para repetição da aposta a pontuação será 80% do pior pontuador para esta corrida e o benefício do item “a” deste tópico será mantido.  
Para o segundo atraso em diante os pontos sofrerão um desconto de 25%.

Pontuação

Cada participante deve indicar o campeão e o vice do campeonato de pilotos e a equipe vencedora do campeonato de construtores ANTES do início da primeira prova do ano em formulário específico.  
A pontuação será 150 pontos se acertar o campeão, 100 se acertar o vice, 80 acertando equipe – Que serão somados à pontuação ao final do campeonato.

Cada participante possui 15 (quinze) fichas para serem apostadas a cada corrida da seguinte maneira:  
A aposta deve conter no mínimo 3 pilotos de equipes diferentes (Apostou no Hamilton, não pode apostar no Leclerc por ex.)  
Sem limite de ficha por piloto, vale 13 / 1 / 1, desde que respeitada a regra acima.  
As corridas Sprint seguem a mesma regra, sendo consideradas provas válidas para a pontuação.  
Deve ser indicado o piloto que irá chegar em 11º lugar em todas as provas e em caso de acerto será computado 25 pontos.

A pontuação do participante será a multiplicação das fichas apostadas em cada piloto pelo número de pontos que ele obteve na prova (fichas x pontos) + pontuação do 11º lugar.  
As apostas serão lançadas na planilha de controle que está hospedada no OneDrive, sendo que o placar atualizado será publicado na página do grupo e no WhatsApp após as corridas.

Critérios de Desempate

Caso haja empate de pontos na classificação final, as posições serão definidas pelos seguintes critérios, na ordem:  
Quem tiver apostado antes mais vezes no ano  
Quem mais vezes acertou o 11º lugar  
Quem acertou o campeão  
Quem acertou a equipe campeã  
Quem acertou o vice

Forma de pagamento e premiação

A premiação será um voucher de 50% do fundo arrecadado das inscrições para o primeiro colocado, 30% para o segundo e 20% para o terceiro gastarem nas bebidas de sua escolha a serem adquiridas após a definição dos vencedores e escolha dos prêmios.

A premiação será realizada em um Happy-Hour a ser agendado entre os participantes em data e local a serem definidos posteriormente ao final do campeonato.
"""

# --- BANCO E FUNÇÕES DE DADOS ---
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

# --- INICIALIZAÇÃO E MENU ---
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

# --- Login, Esqueceu a Senha e Criar Usuário Inativo ---
if st.session_state['pagina'] == "Login":
    st.title("Login")
    if 'esqueceu_senha' not in st.session_state:
        st.session_state['esqueceu_senha'] = False
    if 'criar_usuario' not in st.session_state:
        st.session_state['criar_usuario'] = False

    if not st.session_state['esqueceu_senha'] and not st.session_state['criar_usuario']:
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        col1, col2, col3 = st.columns([2,1,1])
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
        with col3:
            if st.button("Criar usuário"):
                st.session_state['criar_usuario'] = True

    elif st.session_state['esqueceu_senha']:
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

    elif st.session_state['criar_usuario']:
        st.subheader("Criar novo usuário")
        nome_novo = st.text_input("Nome completo")
        email_novo = st.text_input("Email")
        senha_novo = st.text_input("Senha", type="password")
        if st.button("Cadastrar usuário"):
            if cadastrar_usuario(nome_novo, email_novo, senha_novo, perfil='participante', status='Inativo'):
                st.success("Usuário criado com sucesso! Aguarde aprovação do administrador.")
                st.session_state['criar_usuario'] = False
            else:
                st.error("Email já cadastrado.")
        if st.button("Voltar para login", key="voltar_login_criar"):
            st.session_state['criar_usuario'] = False

# ---------------- MENU LATERAL ----------------
if st.session_state['token']:
    payload = get_payload()
    perfil = payload['perfil']
    if perfil == 'master':
        menu = menu_master()
    elif perfil == 'admin':
        menu = menu_admin()
    else:
        menu = menu_participante()
    escolha = st.sidebar.radio("Menu", menu)
    st.session_state['pagina'] = escolha

# ---------------- PAINEL DO PARTICIPANTE ----------------
if st.session_state['pagina'] == "Painel do Participante" and st.session_state['token']:
    payload = get_payload()
    user = get_user_by_id(payload['user_id'])
    st.title("Painel do Participante")
    st.write(f"Bem-vindo, {user[1]} ({user[3]}) - Status: {user[4]}")
    st.cache_data.clear()
    provas = get_provas_df()
    pilotos_df = get_pilotos_df()
    if user[4] == "Ativo":
        if len(provas) > 0 and len(pilotos_df) > 2:
            prova_id = st.selectbox("Escolha a prova", provas['id'], format_func=lambda x: provas[provas['id']==x]['nome'].values[0])
            nome_prova = provas[provas['id']==prova_id]['nome'].values[0]
            apostas_df = get_apostas_df()
            aposta_existente = apostas_df[(apostas_df['usuario_id'] == user[0]) & (apostas_df['prova_id'] == prova_id)]
            pilotos_apostados_ant = []
            fichas_ant = []
            piloto_11_ant = ""
            if not aposta_existente.empty:
                aposta_existente = aposta_existente.iloc[0]
                pilotos_apostados_ant = aposta_existente['pilotos'].split(",")
                fichas_ant = list(map(int, aposta_existente['fichas'].split(",")))
                piloto_11_ant = aposta_existente['piloto_11']
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
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.warning("Administração deve cadastrar provas e pilotos antes das apostas.")
    else:
        st.info("Usuário inativo: você só pode visualizar suas apostas anteriores.")
    st.subheader("Minhas apostas")
    apostas_df = get_apostas_df()
    apostas = apostas_df[apostas_df['usuario_id'] == user[0]].sort_values('prova_id')
    if not apostas.empty:
        apostas_lista = []
        auto_count = 0
        resultados_df = get_resultados_df()
        for idx, ap in enumerate(apostas.itertuples(), start=1):
            pilotos_lst = ap.pilotos.split(",")
            fichas_lst = list(map(int, ap.fichas.split(",")))
            pontos = calcular_pontuacao_lote(pd.DataFrame([ap]), resultados_df)[0]
            cor = ""
            if int(ap.automatica) == 1:
                auto_count += 1
                cor = "background-color: yellow"
            elif int(ap.automatica) >= 2:
                auto_count += 1
                cor = "background-color: red"
            apostas_lista.append({
                "#": idx,
                "Prova": ap.nome_prova,
                "Data Envio": ap.data_envio,
                "Pilotos": ap.pilotos,
                "Fichas": ap.fichas,
                "11º": ap.piloto_11,
                "Pontuação": pontos if pontos is not None else "Aguardando resultado",
                "Cor": cor
            })
        df_apostas = pd.DataFrame(apostas_lista)
        def colorir_linha(row):
            return [row["Cor"]] * len(row)
        colunas_visiveis = ["#", "Prova", "Data Envio", "Pilotos", "Fichas", "11º", "Pontuação"]
        
        def colorir_linha(row):
            cor = row.get("Cor", "")
            return [cor] * len(colunas_visiveis)
        
        st.dataframe(
            df_apostas[colunas_visiveis].style.apply(colorir_linha, axis=1)
        )
    else:
        st.info("Nenhuma aposta registrada.")

# --- GESTÃO DE USUÁRIOS (apenas master) ---
if st.session_state['pagina'] == "Gestão de Usuários" and st.session_state['token']:
    payload = get_payload()
    if payload['perfil'] == 'master':
        st.title("Gestão de Usuários")
        st.cache_data.clear()
        usuarios = get_usuarios_df()

        # Remove a coluna de hash de senha se existir
        if 'senha_hash' in usuarios.columns:
            usuarios = usuarios.drop(columns=['senha_hash'])

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
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Atualizar usuário"):
                    if usuario['nome'] == "Password":
                        st.warning("Não é permitido alterar o status ou perfil do usuário master.")
                    else:
                        conn = db_connect()
                        c = conn.cursor()
                        c.execute('UPDATE usuarios SET nome=?, email=?, status=?, perfil=? WHERE id=?',
                                  (novo_nome, novo_email, novo_status, novo_perfil, usuario_id))
                        conn.commit()
                        conn.close()
                        st.success("Usuário atualizado!")
                        st.cache_data.clear()
                        st.rerun()

            with col2:
                if st.button("Excluir usuário"):
                    if usuario['nome'] == "Password":
                        st.warning("Não é permitido excluir o usuário master.")
                    else:
                        conn = db_connect()
                        c = conn.cursor()
                        c.execute('DELETE FROM usuarios WHERE id=?', (usuario_id,))
                        conn.commit()
                        conn.close()
                        st.success("Usuário excluído!")
                        st.cache_data.clear()
                        st.rerun()
    else:
        st.warning("Acesso restrito ao usuário master.")

# --- CADASTRO DE NOVO PARTICIPANTE (apenas master) ---
if st.session_state['pagina'] == "Cadastro de novo participante" and st.session_state['token']:
    payload = get_payload()
    if payload['perfil'] == 'master':
        st.cache_data.clear()
        st.title("Cadastro de novo participante")
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        if st.button("Cadastrar"):
            if cadastrar_usuario(nome, email, senha):
                st.success("Usuário cadastrado com sucesso!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Email já cadastrado.")
    else:
        st.warning("Acesso restrito ao usuário master.")

# --- GESTÃO DO CAMPEONATO (Pilotos e Provas) ---
if st.session_state['pagina'] == "Gestão do campeonato" and st.session_state['token']:
    payload = get_payload()
    if payload['perfil'] == 'master':
        st.cache_data.clear()
        st.title("Gestão do Campeonato")
        tab1, tab2 = st.tabs(["Pilotos", "Provas"])
        with tab1:
            st.subheader("Adicionar novo piloto")
            if 'nome_novo_piloto' not in st.session_state:
                st.session_state['nome_novo_piloto'] = ""
            if 'equipe_novo_piloto' not in st.session_state:
                st.session_state['equipe_novo_piloto'] = ""
            nome_piloto = st.text_input("Nome do novo piloto", key="nome_novo_piloto")
            equipe_piloto = st.text_input("Nome da equipe do piloto", key="equipe_novo_piloto")
            def cadastrar_piloto():
                if not nome_piloto.strip():
                    st.session_state['erro_piloto'] = "Informe o nome do piloto."
                elif not equipe_piloto.strip():
                    st.session_state['erro_piloto'] = "Informe o nome da equipe."
                else:
                    conn = db_connect()
                    c = conn.cursor()
                    c.execute('INSERT INTO pilotos (nome, equipe) VALUES (?, ?)', (nome_piloto.strip(), equipe_piloto.strip()))
                    conn.commit()
                    conn.close()
                    st.session_state['sucesso_piloto'] = "Piloto adicionado!"
                    st.session_state['nome_novo_piloto'] = ""
                    st.session_state['equipe_novo_piloto'] = ""
            st.button("Adicionar piloto", key="btn_add_piloto", on_click=cadastrar_piloto)
            if st.session_state.get('erro_piloto'):
                st.error(st.session_state['erro_piloto'])
                st.session_state['erro_piloto'] = ""
            if st.session_state.get('sucesso_piloto'):
                st.success(st.session_state['sucesso_piloto'])
                st.session_state['sucesso_piloto'] = ""
                st.cache_data.clear()
                st.rerun()
            st.markdown("---")
            st.subheader("Pilotos cadastrados")
            pilotos = get_pilotos_df()
            if len(pilotos) == 0:
                st.info("Nenhum piloto cadastrado.")
            else:
                for idx, row in pilotos.iterrows():
                    col1, col2, col3, col4 = st.columns([4,3,2,2])
                    with col1:
                        novo_nome = st.text_input(f"Nome piloto {row['id']}", value=row['nome'], key=f"pl_nome{row['id']}")
                    with col2:
                        nova_equipe = st.text_input(f"Equipe piloto {row['id']}", value=row['equipe'], key=f"pl_eq{row['id']}")
                    with col3:
                        def editar_piloto_callback(row_id=row['id'], novo_nome=novo_nome, nova_equipe=nova_equipe):
                            conn = db_connect()
                            c = conn.cursor()
                            c.execute('UPDATE pilotos SET nome=?, equipe=? WHERE id=?', (novo_nome, nova_equipe, row_id))
                            conn.commit()
                            conn.close()
                            st.session_state[f'sucesso_pl_{row_id}'] = "Piloto editado!"
                        st.button("Editar piloto", key=f"pl_edit{row['id']}", on_click=editar_piloto_callback)
                        if st.session_state.get(f'sucesso_pl_{row["id"]}'):
                            st.success(st.session_state[f'sucesso_pl_{row["id"]}'])
                            st.session_state[f'sucesso_pl_{row["id"]}'] = ""
                    with col4:
                        def excluir_piloto_callback(row_id=row['id']):
                            conn = db_connect()
                            c = conn.cursor()
                            c.execute('DELETE FROM pilotos WHERE id=?', (row_id,))
                            conn.commit()
                            conn.close()
                            st.session_state[f'sucesso_pl_del_{row_id}'] = "Piloto excluído!"
                        st.button("Excluir piloto", key=f"pl_del{row['id']}", on_click=excluir_piloto_callback)
                        if st.session_state.get(f'sucesso_pl_del_{row["id"]}'):
                            st.success(st.session_state[f'sucesso_pl_del_{row["id"]}'])
                            st.session_state[f'sucesso_pl_del_{row["id"]}'] = ""
        with tab2:
            st.subheader("Adicionar nova prova")
            st.cache_data.clear()
            if 'nome_nova_prova' not in st.session_state:
                st.session_state['nome_nova_prova'] = ""
            nome_prova = st.text_input("Nome da nova prova", key="nome_nova_prova")
            data_prova = st.date_input("Data da nova prova", key="data_nova_prova")
            def cadastrar_prova():
                if not nome_prova.strip():
                    st.session_state['erro_prova'] = "Informe o nome da prova."
                else:
                    conn = db_connect()
                    c = conn.cursor()
                    c.execute('INSERT INTO provas (nome, data) VALUES (?, ?)', (nome_prova.strip(), data_prova.isoformat()))
                    conn.commit()
                    conn.close()
                    st.session_state['sucesso_prova'] = "Prova adicionada!"
                    st.session_state['nome_nova_prova'] = ""
            st.button("Adicionar prova", key="btn_add_prova", on_click=cadastrar_prova)
            if st.session_state.get('erro_prova'):
                st.error(st.session_state['erro_prova'])
                st.session_state['erro_prova'] = ""
            if st.session_state.get('sucesso_prova'):
                st.success(st.session_state['sucesso_prova'])
                st.session_state['sucesso_prova'] = ""
                st.cache_data.clear()
                st.rerun()
            st.markdown("---")
            st.subheader("Provas cadastradas")
            provas = get_provas_df()
            if len(provas) == 0:
                st.info("Nenhuma prova cadastrada.")
            else:
                for idx, row in provas.iterrows():
                    col1, col2, col3, col4 = st.columns([4,4,2,2])
                    with col1:
                        novo_nome = st.text_input(f"Nome prova {row['id']}", value=row['nome'], key=f"pr_nome{row['id']}")
                    with col2:
                        nova_data = st.date_input(f"Data prova {row['id']}", value=pd.to_datetime(row['data']), key=f"pr_data{row['id']}")
                    with col3:
                        def editar_prova_callback(row_id=row['id'], novo_nome=novo_nome, nova_data=nova_data):
                            conn = db_connect()
                            c = conn.cursor()
                            c.execute('UPDATE provas SET nome=?, data=? WHERE id=?', (novo_nome, nova_data.isoformat(), row_id))
                            conn.commit()
                            conn.close()
                            st.session_state[f'sucesso_pr_{row_id}'] = "Prova editada!"
                        st.button("Editar prova", key=f"pr_edit{row['id']}", on_click=editar_prova_callback)
                        if st.session_state.get(f'sucesso_pr_{row["id"]}'):
                            st.success(st.session_state[f'sucesso_pr_{row["id"]}'])
                            st.session_state[f'sucesso_pr_{row["id"]}'] = ""
                    with col4:
                        def excluir_prova_callback(row_id=row['id']):
                            conn = db_connect()
                            c = conn.cursor()
                            c.execute('DELETE FROM provas WHERE id=?', (row_id,))
                            conn.commit()
                            conn.close()
                            st.session_state[f'sucesso_pr_del_{row_id}'] = "Prova excluída!"
                        st.button("Excluir prova", key=f"pr_del{row['id']}", on_click=excluir_prova_callback)
                        if st.session_state.get(f'sucesso_pr_del_{row["id"]}'):
                            st.success(st.session_state[f'sucesso_pr_del_{row["id"]}'])
                            st.session_state[f'sucesso_pr_del_{row["id"]}'] = ""

# --- GESTÃO DE APOSTAS (apenas master/admin) ---
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

# --- CLASSIFICAÇÃO ---
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

# --- ATUALIZAÇÃO DE RESULTADOS (apenas master/admin) ---
if st.session_state['pagina'] == "Atualização de resultados" and st.session_state['token']:
    payload = get_payload()
    if payload['perfil'] in ['master', 'admin']:
        st.title("Atualizar Resultado Manualmente")
        provas = get_provas_df()
        pilotos_df = get_pilotos_df()
        if len(provas) > 0 and len(pilotos_df) > 0:
            prova_id = st.selectbox("Selecione a prova", provas['id'], format_func=lambda x: provas[provas['id']==x]['nome'].values[0])
            pilotos = pilotos_df['nome'].tolist()
            posicoes = {}
            st.markdown("**Informe o piloto para cada posição:**")
            for pos in range(1, 12):
                posicoes[pos] = st.selectbox(f"{pos}º colocado", pilotos, key=f"pos_{pos}")
            if st.button("Salvar resultado"):
                conn = db_connect()
                c = conn.cursor()
                c.execute('REPLACE INTO resultados (prova_id, posicoes) VALUES (?, ?)',
                          (prova_id, str(posicoes)))
                conn.commit()
                conn.close()
                st.success("Resultado salvo!")
        else:
            st.warning("Cadastre provas e pilotos antes de lançar resultados.")
    else:
        st.warning("Acesso restrito ao administrador/master.")

# --- LOG DE APOSTAS (visível para todos, mas com filtros) ---
if st.session_state['pagina'] == "Log de Apostas" and st.session_state['token']:
    payload = get_payload()
    conn = db_connect()
    if payload['perfil'] == 'master':
        df = pd.read_sql('SELECT * FROM log_apostas', conn)
    else:
        nome = get_user_by_id(payload['user_id'])[1]
        df = pd.read_sql('SELECT * FROM log_apostas WHERE apostador=?', conn, params=(nome,))
    conn.close()
    st.subheader("Log de Apostas")
    st.dataframe(df)

if st.session_state['pagina'] == "Regulamento":
    st.title("Regulamento BF1-2025")
    st.markdown(REGULAMENTO.replace('\n', '  \n'))

if st.session_state['pagina'] == "Logout" and st.session_state['token']:
    st.session_state['token'] = None
    st.session_state['pagina'] = "Login"
    st.success("Logout realizado com sucesso!")
