import pandas as pd
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

from services.email_service import enviar_email_confirmacao_aposta
from db.db_utils import (
    get_user_by_id,
    get_horario_prova,
    db_connect,
    get_pilotos_df
)

def salvar_aposta(
    usuario_id, prova_id, pilotos, fichas, piloto_11, nome_prova,
    automatica=0, horario_forcado=None
):
    nome_prova_bd, data_prova, horario_prova = get_horario_prova(prova_id)
    if not horario_prova:
        st.error("Prova não encontrada ou horário não cadastrado.")
        return False

    horario_limite = datetime.strptime(
        f"{data_prova} {horario_prova}", '%Y-%m-%d %H:%M:%S'
    ).replace(tzinfo=ZoneInfo("America/Sao_Paulo"))

    agora_sp = horario_forcado or datetime.now(ZoneInfo("America/Sao_Paulo"))
    tipo_aposta = 0 if agora_sp <= horario_limite else 1
    dados_aposta = f"Pilotos: {', '.join(pilotos)} | Fichas: {', '.join(map(str, fichas))}"

    usuario = get_user_by_id(usuario_id)
    if not usuario:
        return False

    # Duplicidade apenas no prazo
    if tipo_aposta == 0 and log_aposta_existe(usuario[1], nome_prova_bd, tipo_aposta, automatica, dados_aposta):
        return True

    conn = db_connect()
    try:
        c = conn.cursor()
        c.execute(
            'DELETE FROM apostas WHERE usuario_id=? AND prova_id=?',
            (usuario_id, prova_id)
        )

        if tipo_aposta == 0:
            data_envio = agora_sp.isoformat()
            c.execute(
                '''
                INSERT INTO apostas
                (usuario_id, prova_id, data_envio, pilotos, fichas, piloto_11, nome_prova, automatica)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    usuario_id, prova_id, data_envio,
                    ','.join(pilotos),
                    ','.join(map(str, fichas)),
                    piloto_11, nome_prova_bd, automatica
                )
            )
            conn.commit()
            try:
                enviar_email_confirmacao_aposta(
                    email_usuario=usuario[2],
                    nome_prova=nome_prova_bd,
                    pilotos=pilotos,
                    fichas=fichas,
                    piloto_11=piloto_11,
                    data_envio=data_envio
                )
            except Exception as e:
                st.error(f"Falha no envio de e-mail: {str(e)}")
    except Exception as e:
        st.error(f"Erro ao salvar aposta: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

    # REGISTRO DE LOG: sempre
    registrar_log_aposta(
        apostador=usuario[1],
        aposta=dados_aposta,
        nome_prova=nome_prova_bd,
        piloto_11=piloto_11,
        tipo_aposta=tipo_aposta,
        automatica=automatica,
        horario=agora_sp
    )

    # CONTABILIZA FALTA para aposta automática
    if automatica:
        conn = db_connect()
        c = conn.cursor()
        c.execute('SELECT faltas FROM usuarios WHERE id=?', (usuario_id,))
        faltas_atual = c.fetchone()
        faltas_novo = (faltas_atual[0] if faltas_atual and faltas_atual[0] else 0) + 1
        c.execute('UPDATE usuarios SET faltas=? WHERE id=?', (faltas_novo, usuario_id))
        conn.commit()
        conn.close()

    return True

def log_aposta_existe(apostador: str, nome_prova: str, tipo_aposta: int, automatica: int, dados_aposta: str) -> bool:
    conn = db_connect()
    c = conn.cursor()
    c.execute(
        '''SELECT COUNT(*) FROM log_apostas
           WHERE apostador=? AND nome_prova=? AND tipo_aposta=? AND automatica=? AND aposta=?''',
        (apostador, nome_prova, tipo_aposta, automatica, dados_aposta)
    )
    count = c.fetchone()[0]
    conn.close()
    return count > 0

def registrar_log_aposta(
    apostador: str, aposta: str, nome_prova: str, piloto_11: str, tipo_aposta: int,
    automatica: int = 0, horario: datetime = None
):
    if horario is None:
        horario = datetime.now(ZoneInfo("America/Sao_Paulo"))
    data = horario.strftime('%Y-%m-%d')
    hora = horario.strftime('%H:%M:%S')

    conn = db_connect()
    c = conn.cursor()
    c.execute(
        '''
        INSERT INTO log_apostas
        (apostador, data, horario, aposta, nome_prova, piloto_11, tipo_aposta, automatica)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (apostador, data, hora, aposta, nome_prova, piloto_11, tipo_aposta, automatica)
    )
    conn.commit()
    conn.close()

def gerar_aposta_aleatoria(pilotos_df: pd.DataFrame):
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
        if total_fichas <= 0: break
        adicionais = min(random.randint(0, total_fichas), 9)
        fichas[i] += adicionais
        total_fichas -= adicionais
    todos_pilotos = pilotos_df['nome'].tolist()
    candidatos_11 = [p for p in todos_pilotos if p not in pilotos_selecionados]
    piloto_11 = random.choice(candidatos_11) if candidatos_11 else random.choice(todos_pilotos)
    return pilotos_selecionados, fichas, piloto_11

def gerar_aposta_automatica(usuario_id, prova_id, nome_prova, apostas_df, provas_df):
    prova_atual = provas_df[provas_df['id'] == prova_id]
    if prova_atual.empty:
        return False, "Prova não encontrada."

    data_prova = prova_atual['data'].iloc[0]
    horario_prova = prova_atual['horario_prova'].iloc[0]
    horario_limite = datetime.strptime(f"{data_prova} {horario_prova}", '%Y-%m-%d %H:%M:%S').replace(tzinfo=ZoneInfo("America/Sao_Paulo"))
    pilotos_df = get_pilotos_df()

    # Busca aposta da prova anterior, se houver. Senão, gera aleatória.
    prova_ant_id = prova_id - 1
    pilotos_ant, fichas_ant, piloto_11_ant = None, None, None
    prova_ant = provas_df[provas_df['id'] == prova_ant_id]
    if not prova_ant.empty:
        ap_ant = apostas_df[(apostas_df['usuario_id'] == usuario_id) & (apostas_df['prova_id'] == prova_ant_id)]
        if not ap_ant.empty:
            ap_ant = ap_ant.iloc[0]
            pilotos_ant = ap_ant['pilotos'].split(",")
            fichas_ant = list(map(int, ap_ant['fichas'].split(",")))
            piloto_11_ant = ap_ant['piloto_11']
    if not pilotos_ant:
        pilotos_ant, fichas_ant, piloto_11_ant = gerar_aposta_aleatoria(pilotos_df)

    conn = db_connect()
    c = conn.cursor()
    c.execute('SELECT MAX(automatica) FROM apostas WHERE usuario_id=?', (usuario_id,))
    max_automatica = c.fetchone()[0]
    conn.close()
    nova_automatica = 1 if max_automatica is None else max_automatica + 1

    sucesso = salvar_aposta(
        usuario_id, prova_id, pilotos_ant, fichas_ant,
        piloto_11_ant, nome_prova, automatica=nova_automatica, horario_forcado=horario_limite
    )
    if sucesso:
        return True, "Aposta automática gerada com sucesso!"
    else:
        return False, "Falha ao salvar aposta automática."
