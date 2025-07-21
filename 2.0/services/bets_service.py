import pandas as pd
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

from db.db_utils import (
    get_user_by_id, get_horario_prova, db_connect, get_pilotos_df, 
    registrar_log_aposta, log_aposta_existe, get_apostas_df, get_provas_df, get_resultados_df
)

def salvar_aposta(
    usuario_id, prova_id, pilotos, fichas, piloto_11, nome_prova,
    automatica=0, horario_forcado=None
):
    nome_prova_bd, data_prova, horario_prova = get_horario_prova(prova_id)
    if not horario_prova:
        st.error("Prova não encontrada ou horário não cadastrado.")
        return False

    if not pilotos or not fichas or not piloto_11 or len(pilotos) < 3 or sum(fichas) != 15:
        st.error("Dados insuficientes para gerar aposta automática. Revise cadastro de pilotos e equipes.")
        return False

    horario_limite = datetime.strptime(f"{data_prova} {horario_prova}", '%Y-%m-%d %H:%M:%S').replace(tzinfo=ZoneInfo("America/Sao_Paulo"))
    agora_sp = horario_forcado or datetime.now(ZoneInfo("America/Sao_Paulo"))
    tipo_aposta = 0 if agora_sp <= horario_limite else 1
    dados_aposta = f"Pilotos: {', '.join(pilotos)} | Fichas: {', '.join(map(str, fichas))}"
    usuario = get_user_by_id(usuario_id)
    if not usuario:
        st.error(f"Usuário não encontrado: id={usuario_id}")
        return False

    if tipo_aposta == 0 and log_aposta_existe(usuario[1], nome_prova_bd, tipo_aposta, automatica, dados_aposta):
        return True

    conn = db_connect()
    try:
        c = conn.cursor()
        c.execute('DELETE FROM apostas WHERE usuario_id=? AND prova_id=?', (usuario_id, prova_id))
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
    except Exception as e:
        st.error(f"Erro ao salvar aposta: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

    registrar_log_aposta(
        apostador=usuario[1],
        aposta=dados_aposta,
        nome_prova=nome_prova_bd,
        piloto_11=piloto_11,
        tipo_aposta=tipo_aposta,
        automatica=automatica,
        horario=agora_sp
    )
    if automatica:
        conn = db_connect()
        c = conn.cursor()
        c.execute('UPDATE usuarios SET faltas = faltas + 1 WHERE id=?', (usuario_id,))
        conn.commit()
        conn.close()
    return True

def gerar_aposta_aleatoria(pilotos_df):
    import random
    # Garante que há ao menos 3 equipes diferentes e pilotos suficientes
    equipes_unicas = [e for e in pilotos_df['equipe'].unique().tolist() if e]
    if len(equipes_unicas) < 3 or pilotos_df.empty or len(pilotos_df['nome'].unique()) < 3:
        return [], [], None
    equipes_selecionadas = random.sample(equipes_unicas, 3)
    pilotos_sel = []
    for equipe in equipes_selecionadas:
        pilotos_equipe = pilotos_df[pilotos_df['equipe'] == equipe]['nome'].tolist()
        if pilotos_equipe:
            piloto_escolhido = random.choice(pilotos_equipe)
            if piloto_escolhido not in pilotos_sel:
                pilotos_sel.append(piloto_escolhido)
    # Se não conseguir pilotos suficientes, aborta
    if len(pilotos_sel) < 3:
        return [], [], None
    n_pilotos = len(pilotos_sel)
    fichas = [1] * n_pilotos
    total_fichas = 15 - n_pilotos
    for i in range(n_pilotos):
        if total_fichas <= 0:
            break
        max_for_this = min(9, total_fichas)
        add = random.randint(0, max_for_this)
        fichas[i] += add
        total_fichas -= add
    todos_pilotos = pilotos_df['nome'].tolist()
    candidatos_11 = [p for p in todos_pilotos if p not in pilotos_sel]
    piloto_11 = random.choice(candidatos_11) if candidatos_11 else random.choice(todos_pilotos)
    return pilotos_sel, fichas, piloto_11

def gerar_aposta_automatica(usuario_id, prova_id, nome_prova, apostas_df, provas_df):
    prova_atual = provas_df[provas_df['id'] == prova_id]
    if prova_atual.empty:
        return False, "Prova não encontrada."
    data_prova = prova_atual['data'].iloc[0]
    horario_prova = prova_atual['horario_prova'].iloc[0]
    horario_limite = datetime.strptime(f"{data_prova} {horario_prova}", '%Y-%m-%d %H:%M:%S').replace(tzinfo=ZoneInfo("America/Sao_Paulo"))
    pilotos_df = get_pilotos_df()
    # Checa aposta manual existente
    aposta_existente = apostas_df[
        (apostas_df["usuario_id"] == usuario_id) &
        (apostas_df["prova_id"] == prova_id) &
        ((apostas_df["automatica"].isnull()) | (apostas_df["automatica"] == 0))
    ]
    if not aposta_existente.empty:
        return False, "Já existe aposta manual para esta prova."
    # Tenta copiar da anterior, senão gera aleatória
    prova_ant_id = prova_id - 1
    pilotos_ant, fichas_ant, piloto_11_ant = None, None, None
    prova_ant = provas_df[provas_df['id'] == prova_ant_id]
    if not prova_ant.empty:
        ap_ant = apostas_df[
            (apostas_df['usuario_id'] == usuario_id) &
            (apostas_df['prova_id'] == prova_ant_id)
        ]
        if not ap_ant.empty:
            ap_ant = ap_ant.iloc[0]
            pilotos_ant = ap_ant['pilotos'].split(",")
            fichas_ant = list(map(int, ap_ant['fichas'].split(",")))
            piloto_11_ant = ap_ant['piloto_11']
    if not pilotos_ant or not fichas_ant or not piloto_11_ant:
        pilotos_ant, fichas_ant, piloto_11_ant = gerar_aposta_aleatoria(pilotos_df)
    # Validação crítica
    if not pilotos_ant or not fichas_ant or not piloto_11_ant:
        return False, "Não há dados válidos para gerar aposta automática: revise o cadastro de pilotos/equipes."
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
    return (True, "Aposta automática gerada com sucesso!") if sucesso else (False, "Falha ao salvar aposta automática.")
