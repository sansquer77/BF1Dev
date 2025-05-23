import streamlit as st
import sqlite3
import bcrypt
import jwt as pyjwt
import pandas as pd
from datetime import datetime, timedelta

DB_PATH = 'bolao_f1.db'
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
O participante pode enviar quantas apostas quiser até o horário limite, sendo válida a última enviada.
Apostas registradas após o horário da largada, por exemplo 09:01 sendo a corrida às 09h serão desconsideradas.

O participante que não efetuar a sua aposta ATÉ O PRAZO DEFINO DO ITEM-3, irá concorrer com a mesma aposta da última corrida.
Quando se tratar da primeira vez que a aposta não for feita, e apenas neste caso, será computado 100% dos pontos.
Caso o apostador não aposte na primeira corrida do campeonato, como não haverá base para repetição da aposta a pontuação será 80% do pior pontuador para esta corrida e o benefício do item “a” deste tópico será mantido.
Para a segundo atraso em diante os pontos sofrerão um desconto de 25%.

Pontuação

Cada participante deve indicar o campeão e o vice do campeonato de pilotos e a equipe vencedora do campeonato de construtores ANTES do início da primeira prova do ano em formulário específico.
A pontuação será 150 pontos se acertar o campeão, 100 se acertar o vice, 80 acertando equipe – Que serão somados à pontuação ao final do campeonato.

Cada participante possui 15 (quinze) fichas para serem apostadas a cada corrida da seguinte maneira:
Aposta deve conter no mínimo 3 pilotos de equipes diferentes (Apostou no Hamilton, não pode apostar no Leclerc por ex.)
Sem limite de ficha por piloto, vale 13 / 1 / 1, desde que respeitada a regra acima.
As corridas Sprint seguem a mesma regra, sendo consideradas provas válidas para a pontuação.
Deve ser indicado o piloto que irá chegar em 11 lugar em todas as provas e em caso de acerto será computado 25 pontos

A pontuação do participante será a multiplicação das fichas apostadas em cada piloto pelo número de pontos que ele obteve na prova (fichas x pontos) + pontuação do 11 lugar.
As apostas serão lançadas na planilha de controle que está hospedada no OneDrive, sendo que o placar atualizado será publicado na página do grupo e no WhatsApp após as corridas.

Critérios de Desempate

Caso haja empate de pontos na classificação final, as posições serão definidas pelos seguintes critérios, na ordem:
Quem tiver apostado antes mais vezes no ano
Quem mais vezes acertou o 11 lugar
Quem acertou o campeão
Quem acertou a equipe campeã
Quem acertou o vice

Forma de pagamento e premiação

A premiação será um voucher de 50% do fundo arrecadado das inscrições para o primeiro colocado, 30% para o segundo e 20% para o terceiro gastarem nas bebidas de sua escolha a serem adquiridas após a definição dos vencedores e escolha dos prêmios.
 
A premiação será realizada em um Happy-Hour a ser agendado entre os participantes em data e local a serem definidos posteriormente ao final do campeonato.
"""

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
    senha_hash = bcrypt.hashpw('ADMIN'.encode(), bcrypt.gensalt())
    c.execute('''INSERT OR IGNORE INTO usuarios (nome, email, senha_hash, perfil, status)
                 VALUES (?, ?, ?, ?, ?)''',
              ('Password', 'master@bolao.com', senha_hash, 'master', 'Ativo'))
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
def cadastrar_usuario(nome, email, senha, perfil='participante', status='Ativo'):
    conn = db_connect()
    c = conn.cursor()
    try:
        senha_hash = hash_password(senha)
        c.execute('INSERT INTO usuarios (nome, email, senha_hash, perfil, status) VALUES (?, ?, ?, ?, ?)', 
                  (nome, email, senha_hash, perfil, status))
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

def salvar_aposta(usuario_id, prova_id, pilotos, fichas, piloto_11, nome_prova):
    conn = db_connect()
    c = conn.cursor()
    data_envio = datetime.now().isoformat()
    c.execute('DELETE FROM apostas WHERE usuario_id=? AND prova_id=?', (usuario_id, prova_id))
    c.execute('INSERT INTO apostas (usuario_id, prova_id, data_envio, pilotos, fichas, piloto_11, nome_prova) VALUES (?, ?, ?, ?, ?, ?, ?)',
              (usuario_id, prova_id, data_envio, ','.join(pilotos), ','.join(map(str, fichas)), piloto_11, nome_prova))
    conn.commit()
    conn.close()

def consultar_apostas(usuario_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('SELECT rowid, nome_prova, prova_id, data_envio, pilotos, fichas, piloto_11 FROM apostas WHERE usuario_id=?', (usuario_id,))
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

def consultar_resultado_prova(prova_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('SELECT posicoes FROM resultados WHERE prova_id=?', (prova_id,))
    res = c.fetchone()
    conn.close()
    if res:
        return ast.literal_eval(res[0])
    return None

def calcular_pontuacao_aposta(prova_id, pilotos_apostados, fichas_apostadas, piloto_11_apostado):
    resultado = consultar_resultado_prova(prova_id)
    if not resultado:
        return None  # Resultado ainda não lançado
    pontos_f1 = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
    pontos = 0
    for idx, (piloto, ficha) in enumerate(zip(pilotos_apostados, fichas_apostadas)):
        for pos, nome_resultado in resultado.items():
            pos_int = int(pos)
            if pos_int <= 10 and nome_resultado == piloto:
                pontos += ficha * pontos_f1[pos_int-1]
    if '11' in resultado and resultado['11'] == piloto_11_apostado:
        pontos += 25
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
        "Atualização de resultados",
        "Log de Apostas",
        "Classificação",
        "Regulamento",
        "Logout"
    ]
def menu_admin():
    return [
        "Painel do Participante",
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

# --- Menu lateral dinâmico ---
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

# --- Painel do Participante (corrigido, robusto, linhas dinâmicas, 11º diferente) ---
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
                pilotos_ant, fichas_ant_list, piloto_11_ant = aposta_existente
                pilotos_apostados_ant = pilotos_ant.split(",")
                fichas_ant = list(map(int, fichas_ant_list.split(",")))
            else:
                fichas_ant = []
                piloto_11_ant = ""
            st.write("Escolha seus pilotos e distribua 15 fichas entre eles (mínimo 3 pilotos de equipes diferentes):")
            pilotos = pilotos_df['nome'].tolist()
            equipes = pilotos_df['equipe'].tolist()
            pilotos_equipe = dict(zip(pilotos, equipes))
            # Formulário de aposta
            max_linhas = 5
            pilotos_aposta = []
            fichas_aposta = []
            linhas_visiveis = 3
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
            # 11º colocado não pode ser um dos pilotos apostados
            pilotos_validos = [p for p in pilotos_aposta if p != "Nenhum"]
            fichas_validas = [f for i, f in enumerate(fichas_aposta) if pilotos_aposta[i] != "Nenhum"]
            equipes_apostadas = [pilotos_equipe[p] for p in pilotos_validos]
            total_fichas = sum(fichas_validas)
            pilotos_11_opcoes = [p for p in pilotos if p not in pilotos_validos]
            if not pilotos_11_opcoes:
                pilotos_11_opcoes = pilotos  # fallback
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
                        piloto_11, nome_prova
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
        for idx, (rowid, nome_prova, prova_id, data_envio, pilotos, fichas, piloto_11) in enumerate(apostas, start=1):
            pilotos_lst = pilotos.split(",")
            fichas_lst = list(map(int, fichas.split(",")))
            pontos = calcular_pontuacao_aposta(prova_id, pilotos_lst, fichas_lst, piloto_11)
            apostas_lista.append({
                "#": idx,
                "Prova": nome_prova,
                "Data Envio": data_envio,
                "Pilotos": pilotos,
                "Fichas": fichas,
                "11º": piloto_11,
                "Pontuação": pontos if pontos is not None else "Aguardando resultado"
            })
        st.table(pd.DataFrame(apostas_lista))
    else:
        st.info("Nenhuma aposta registrada.")

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
if st.session_state['pagina'] == "Gestão do campeonato" and st.session_state['token']:
    payload = get_payload()
    if payload['perfil'] == 'master':
        st.title("Gestão do Campeonato")
        tab1, tab2 = st.tabs(["Pilotos", "Provas"])

        # --- Pilotos ---
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
                    adicionar_piloto(nome_piloto.strip(), equipe_piloto.strip())
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

            st.markdown("---")
            st.subheader("Pilotos cadastrados")
            pilotos = listar_pilotos()
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
                            editar_piloto(row_id, novo_nome, nova_equipe)
                            st.session_state[f'sucesso_pl_{row_id}'] = "Piloto editado!"
                        st.button("Editar piloto", key=f"pl_edit{row['id']}", on_click=editar_piloto_callback)
                        if st.session_state.get(f'sucesso_pl_{row["id"]}'):
                            st.success(st.session_state[f'sucesso_pl_{row["id"]}'])
                            st.session_state[f'sucesso_pl_{row["id"]}'] = ""
                    with col4:
                        def excluir_piloto_callback(row_id=row['id']):
                            excluir_piloto(row_id)
                            st.session_state[f'sucesso_pl_del_{row_id}'] = "Piloto excluído!"
                        st.button("Excluir piloto", key=f"pl_del{row['id']}", on_click=excluir_piloto_callback)
                        if st.session_state.get(f'sucesso_pl_del_{row["id"]}'):
                            st.success(st.session_state[f'sucesso_pl_del_{row["id"]}'])
                            st.session_state[f'sucesso_pl_del_{row["id"]}'] = ""

        # --- Provas ---
        with tab2:
            st.subheader("Adicionar nova prova")
            if 'nome_nova_prova' not in st.session_state:
                st.session_state['nome_nova_prova'] = ""
            nome_prova = st.text_input("Nome da nova prova", key="nome_nova_prova")
            data_prova = st.date_input("Data da nova prova", key="data_nova_prova")
            def cadastrar_prova():
                if not nome_prova.strip():
                    st.session_state['erro_prova'] = "Informe o nome da prova."
                else:
                    adicionar_prova(nome_prova.strip(), data_prova.isoformat())
                    st.session_state['sucesso_prova'] = "Prova adicionada!"
                    st.session_state['nome_nova_prova'] = ""
            st.button("Adicionar prova", key="btn_add_prova", on_click=cadastrar_prova)
            if st.session_state.get('erro_prova'):
                st.error(st.session_state['erro_prova'])
                st.session_state['erro_prova'] = ""
            if st.session_state.get('sucesso_prova'):
                st.success(st.session_state['sucesso_prova'])
                st.session_state['sucesso_prova'] = ""

            st.markdown("---")
            st.subheader("Provas cadastradas")
            provas = listar_provas()
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
                            editar_prova(row_id, novo_nome, nova_data.isoformat())
                            st.session_state[f'sucesso_pr_{row_id}'] = "Prova editada!"
                        st.button("Editar prova", key=f"pr_edit{row['id']}", on_click=editar_prova_callback)
                        if st.session_state.get(f'sucesso_pr_{row["id"]}'):
                            st.success(st.session_state[f'sucesso_pr_{row["id"]}'])
                            st.session_state[f'sucesso_pr_{row["id"]}'] = ""
                    with col4:
                        def excluir_prova_callback(row_id=row['id']):
                            excluir_prova(row_id)
                            st.session_state[f'sucesso_pr_del_{row_id}'] = "Prova excluída!"
                        st.button("Excluir prova", key=f"pr_del{row['id']}", on_click=excluir_prova_callback)
                        if st.session_state.get(f'sucesso_pr_del_{row["id"]}'):
                            st.success(st.session_state[f'sucesso_pr_del_{row["id"]}'])
                            st.session_state[f'sucesso_pr_del_{row["id"]}'] = ""
    else:
        st.warning("Acesso restrito ao usuário master.")

# --- Atualização de resultados (apenas manual, tabela de posições) ---
if st.session_state['pagina'] == "Atualização de resultados" and st.session_state['token']:
    payload = get_payload()
    if payload['perfil'] in ['master', 'admin']:
        st.title("Atualizar Resultado Manualmente")
        provas = listar_provas()
        pilotos_df = listar_pilotos()
        if len(provas) > 0 and len(pilotos_df) > 0:
            prova_id = st.selectbox("Selecione a prova", provas['id'], format_func=lambda x: provas[provas['id']==x]['nome'].values[0])
            pilotos = pilotos_df['nome'].tolist()
            posicoes = {}
            st.markdown("**Informe o piloto para cada posição:**")
            for pos in range(1, 12):
                posicoes[pos] = st.selectbox(f"{pos}º colocado", pilotos, key=f"pos_{pos}")
            if st.button("Salvar resultado"):
                salvar_resultado_manual(prova_id, posicoes)
                st.success("Resultado salvo!")
        else:
            st.warning("Cadastre provas e pilotos antes de lançar resultados.")
    else:
        st.warning("Acesso restrito ao administrador/master.")

# --- Log de apostas (visível para todos, mas com filtros) ---
if st.session_state['pagina'] == "Log de Apostas" and st.session_state['token']:
    payload = get_payload()
    if payload['perfil'] == 'master':
        exibir_log_apostas(is_master=True)
    else:
        exibir_log_apostas(user_id=payload['user_id'], is_master=False)

# --- Tabela de classificação geral ---
if st.session_state['pagina'] == "Classificação" and st.session_state['token']:
    st.title("Classificação Geral do Bolão")

    # 1. Tabela de classificação geral
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
        for _, prova in provas.iterrows():
            apostas = consultar_apostas(part['id'])
            pontos = 0
            for ap in apostas:
                _, nome_prova, prova_id, _, pilotos, fichas, piloto_11 = ap
                if prova_id == prova['id']:
                    pilotos_lst = pilotos.split(",")
                    fichas_lst = list(map(int, fichas.split(",")))
                    p = calcular_pontuacao_aposta(prova_id, pilotos_lst, fichas_lst, piloto_11)
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
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    for participante in participantes_nomes:
        pontos = df_cruzada[participante].cumsum()
        ax.plot(provas_nomes, pontos, marker='o', label=participante)
    ax.set_xlabel("Prova")
    ax.set_ylabel("Pontuação Acumulada")
    ax.legend()
    st.pyplot(fig)

# --- Regulamento ---
if st.session_state['pagina'] == "Regulamento":
    st.title("Regulamento BF1-2025")
    st.markdown(REGULAMENTO)

# --- Logout ---
if st.session_state['pagina'] == "Logout" and st.session_state['token']:
    logout()
