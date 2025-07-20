import pandas as pd
from db.db_utils import db_connect, get_user_by_id, get_horario_prova
from services.email_service import enviar_email_confirmacao_aposta
from datetime import datetime
from zoneinfo import ZoneInfo

def salvar_aposta(
    usuario_id: int,
    prova_id: int,
    pilotos: list[str],
    fichas: list[int],
    piloto_11: str,
    nome_prova: str,
    automatica: int = 0,
    horario_forcado: datetime = None
) -> bool:
    """
    Salva ou atualiza uma aposta para o usuário e uma prova. Gera log e, se dentro do prazo, envia email de confirmação.
    """
    from email_service import enviar_email_confirmacao_aposta

    # Obtenha informações do horário da prova
    nome_prova_bd, data_prova, horario_prova = get_horario_prova(prova_id)
    if not horario_prova:
        return False

    # Ajusta o horário limite para apostas
    horario_limite = datetime.strptime(f"{data_prova} {horario_prova}", '%Y-%m-%d %H:%M:%S')
    horario_limite = horario_limite.replace(tzinfo=ZoneInfo("America/Sao_Paulo"))
    agora_sp = horario_forcado or datetime.now(ZoneInfo("America/Sao_Paulo"))

    # Tipo de aposta: 0 = em dia, 1 = fora do prazo
    tipo_aposta = 0 if agora_sp <= horario_limite else 1

    # Dados da aposta para registrar log
    dados_aposta = f"Pilotos: {', '.join(pilotos)} | Fichas: {', '.join(map(str, fichas))}"

    # Busca usuário
    usuario = get_user_by_id(usuario_id)
    if not usuario:
        return False

    # Evita log duplicado
    if log_aposta_existe(usuario[1], nome_prova_bd, tipo_aposta, automatica, dados_aposta):
        return True

    conn = db_connect()
    try:
        c = conn.cursor()
        # Remove aposta anterior, se houver, para essa prova
        c.execute('DELETE FROM apostas WHERE usuario_id=? AND prova_id=?', (usuario_id, prova_id))

        # Só salva aposta se for até o horário limite
        if tipo_aposta == 0:
            data_envio = agora_sp.isoformat()
            c.execute('''INSERT INTO apostas
                (usuario_id, prova_id, data_envio, pilotos, fichas, piloto_11, nome_prova, automatica)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (usuario_id, prova_id, data_envio, ','.join(pilotos), ','.join(map(str, fichas)), piloto_11, nome_prova_bd, automatica))
            conn.commit()
            # Envia email de confirmação
            enviar_email_confirmacao_aposta(
                email_usuario=usuario[2],
                nome_prova=nome_prova_bd,
                pilotos=pilotos,
                fichas=fichas,
                piloto_11=piloto_11,
                data_envio=data_envio
            )
        # Registrar log
        registrar_log_aposta(
            apostador=usuario[1],
            aposta=dados_aposta,
            nome_prova=nome_prova_bd,
            piloto_11=piloto_11,
            tipo_aposta=tipo_aposta,
            automatica=automatica,
            horario=agora_sp
        )
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()

def log_aposta_existe(apostador: str, nome_prova: str, tipo_aposta: int, automatica: int, dados_aposta: str) -> bool:
    """
    Retorna True se já existir um registro idêntico de log de aposta para evitar duplicidade.
    """
    conn = db_connect()
    c = conn.cursor()
    c.execute('''SELECT COUNT(*) FROM log_apostas 
                 WHERE apostador=? AND nome_prova=? AND tipo_aposta=? AND automatica=? AND aposta=?''',
              (apostador, nome_prova, tipo_aposta, automatica, dados_aposta))
    count = c.fetchone()[0]
    conn.close()
    return count > 0

def registrar_log_aposta(apostador: str, aposta: str, nome_prova: str, piloto_11: str, tipo_aposta: int, automatica: int = 0, horario: datetime = None):
    """
    Registra cada aposta em um log detalhado.
    """
    if horario is None:
        horario = datetime.now(ZoneInfo("America/Sao_Paulo"))
    data = horario.strftime('%Y-%m-%d')
    hora = horario.strftime('%H:%M:%S')
    conn = db_connect()
    c = conn.cursor()
    c.execute('''INSERT INTO log_apostas 
                (apostador, data, horario, aposta, nome_prova, piloto_11, tipo_aposta, automatica) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (apostador, data, hora, aposta, nome_prova, piloto_11, tipo_aposta, automatica))
    conn.commit()
    conn.close()

def gerar_aposta_aleatoria(pilotos_df: pd.DataFrame):
    """
    Gera apostas necessárias e válidas para o regulamento (mínimo 3 equipes distintas e soma 15 fichas).
    """
    import random
    equipes_unicas = pilotos_df['equipe'].unique().tolist()
    if len(equipes_unicas) < 3:
        equipes_selecionadas = equipes_unicas.copy()
        while len(equipes_selecionadas) < 3:
            equipes_selecionadas.append(random.choice(equipes_unicas))
    else:
        equipes_selecionadas = random.sample(equipes_unicas, 3)
    pilotos_selecionados = []
    for equipe in equipes_selecionadas:
        pilotos_equipe = pilotos_df[pilotos_df['equipe'] == equipe]['nome'].tolist()
        if pilotos_equipe:
            pilotos_selecionados.append(random.choice(pilotos_equipe))
    n_pilotos = len(pilotos_selecionados)
    fichas = [1] * n_pilotos
    total_fichas = 15 - n_pilotos
    for i in range(n_pilotos):
        if total_fichas <= 0:
            break
        adicionais = min(random.randint(0, total_fichas), 9)
        fichas[i] += adicionais
        total_fichas -= adicionais
    todos_pilotos = pilotos_df['nome'].tolist()
    candidatos_11 = [p for p in todos_pilotos if p not in pilotos_selecionados]
    piloto_11 = random.choice(candidatos_11) if candidatos_11 else random.choice(todos_pilotos)
    return pilotos_selecionados, fichas, piloto_11

def gerar_aposta_automatica(usuario_id: int, prova_id: int, nome_prova: str, apostas_df: pd.DataFrame, provas_df: pd.DataFrame):
    """
    Gera aposta automática: replica a última ou gera aleatória se não houver anterior.
    """
    # Buscar aposta anterior
    prova_atual = provas_df[provas_df['id'] == prova_id]
    if prova_atual.empty:
        return False, "Prova não encontrada."
    data_prova = prova_atual['data'].iloc[0]
    horario_prova = prova_atual['horario_prova'].iloc[0]
    horario_limite = datetime.strptime(f"{data_prova} {horario_prova}", '%Y-%m-%d %H:%M:%S')
    horario_limite = horario_limite.replace(tzinfo=ZoneInfo("America/Sao_Paulo"))
    pilotos_df = get_pilotos_df()
    prova_ant_id = prova_id - 1
    prova_ant = provas_df[provas_df['id'] == prova_ant_id]
    if not prova_ant.empty:
        ap_ant = apostas_df[(apostas_df['usuario_id'] == usuario_id) & (apostas_df['prova_id'] == prova_ant_id)]
        if not ap_ant.empty:
            ap_ant = ap_ant.iloc[0]
            pilotos_ant = ap_ant['pilotos'].split(",")
            fichas_ant = list(map(int, ap_ant['fichas'].split(",")))
            piloto_11_ant = ap_ant['piloto_11']
        else:
            pilotos_ant, fichas_ant, piloto_11_ant = gerar_aposta_aleatoria(pilotos_df)
    else:
        pilotos_ant, fichas_ant, piloto_11_ant = gerar_aposta_aleatoria(pilotos_df)
    # Busca maior valor atual de 'automatica' para o usuário
    conn = db_connect()
    c = conn.cursor()
    c.execute('SELECT MAX(automatica) FROM apostas WHERE usuario_id=?', (usuario_id,))
    max_automatica = c.fetchone()[0]
    conn.close()
    nova_automatica = 1 if max_automatica is None else max_automatica + 1
    return salvar_aposta(
        usuario_id, prova_id, pilotos_ant, fichas_ant, piloto_11_ant, nome_prova, automatica=nova_automatica, horario_forcado=horario_limite
    ), "Aposta automática gerada com sucesso!"

def atualizar_classificacoes_todas_as_provas():
    """Calcula e salva a classificação de todas as provas já ocorridas com resultado cadastrado."""
    conn = db_connect()
    usuarios_df = pd.read_sql('SELECT * FROM usuarios WHERE status = "Ativo"', conn)
    provas_df = pd.read_sql('SELECT * FROM provas', conn)
    apostas_df = pd.read_sql('SELECT * FROM apostas', conn)
    resultados_df = pd.read_sql('SELECT * FROM resultados', conn)
    conn.close()

    for _, prova in provas_df.iterrows():
        prova_id = prova['id']
        if prova_id not in resultados_df['prova_id'].values:
            continue

        apostas_prova = apostas_df[apostas_df['prova_id'] == prova_id]
        if apostas_prova.empty:
            continue

        tabela = []
        for _, usuario in usuarios_df.iterrows():
            aposta = apostas_prova[apostas_prova['usuario_id'] == usuario['id']]
            if aposta.empty:
                pontos = 0
                data_envio = None
                acerto_11 = 0
            else:
                pontos = calcular_pontuacao_lote(aposta, resultados_df, provas_df)
                pontos = pontos[0] if pontos and pontos[0] is not None else 0
                data_envio = aposta.iloc[0]['data_envio'] if 'data_envio' in aposta.columns else None

                # Checa acerto do 11º colocado
                acerto_11 = 0
                if not aposta.empty and not resultados_df.empty:
                    resultado = resultados_df[resultados_df['prova_id'] == prova_id]
                    if not resultado.empty:
                        posicoes = ast.literal_eval(resultado.iloc[0]['posicoes'])
                        piloto_11_real = posicoes.get(11, "")
                        piloto_11_apostado = aposta.iloc[0]['piloto_11']
                        if piloto_11_apostado == piloto_11_real:
                            acerto_11 = 1

            tabela.append({
                'usuario_id': int(usuario['id']),
                'pontos': pontos,
                'data_envio': data_envio,
                'acerto_11': acerto_11
            })

        # Ordena por: pontos (desc), data_envio (asc), acerto_11 (desc)
        df_classificacao = pd.DataFrame(tabela)
        df_classificacao['data_envio'] = pd.to_datetime(df_classificacao['data_envio'], errors='coerce')
        df_classificacao = df_classificacao.sort_values(
            by=['pontos', 'acerto_11', 'data_envio'],
            ascending=[False, False, True]
        ).reset_index(drop=True)
        df_classificacao['posicao'] = df_classificacao.index + 1

        salvar_classificacao_prova(prova_id, df_classificacao)
