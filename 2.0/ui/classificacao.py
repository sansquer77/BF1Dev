import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from db.db_utils import db_connect, get_usuarios_df, get_provas_df, get_apostas_df, get_resultados_df
from services.championship_service import (
    get_final_results, get_championship_bet
)
from services.bets_service import calcular_pontuacao_lote

def main():
    col1, col2 = st.columns([1, 16])  # Proporção ajustável conforme aparência desejada
    with col1:
        st.image("BF1.jpg", width=75)
    with col2:
        st.title("Classificação Geral do Bolão")

    # Dados principais
    usuarios_df = get_usuarios_df()
    provas_df = get_provas_df()
    apostas_df = get_apostas_df()
    resultados_df = get_resultados_df()
    participantes = usuarios_df[usuarios_df['status'] == 'Ativo']
    provas_df = provas_df.sort_values('data')

    # 1. Pontuação das provas
    tabela_classificacao = []
    tabela_detalhada = []

    for idx, part in participantes.iterrows():
        apostas_part = apostas_df[apostas_df['usuario_id'] == part['id']].sort_values('prova_id')
        pontos_part = calcular_pontuacao_lote(apostas_part, resultados_df, provas_df)
        total = sum([p for p in pontos_part if p is not None])
        tabela_classificacao.append({
            "Participante": part['nome'],
            "usuario_id": part['id'],
            "Pontos Provas": total
        })
        tabela_detalhada.append({
            "Participante": part['nome'],
            "Pontos por Prova": pontos_part
        })

    df_class = pd.DataFrame(tabela_classificacao)
    df_class = df_class.sort_values("Pontos Provas", ascending=False).reset_index(drop=True)
    df_class["Pontos Provas"] = df_class["Pontos Provas"].apply(lambda x: f"{x:.2f}")
    df_class['Posição'] = df_class.index + 1

    # 2. Movimentação de posições
    provas_realizadas = provas_df[provas_df['id'].isin(resultados_df['prova_id'])]
    if len(provas_realizadas) > 1:
        penultima_prova_id = provas_realizadas.iloc[-2]['id']
        provas_ate_penultima = provas_realizadas[provas_realizadas['id'] <= penultima_prova_id]['id'].tolist()
        tabela_anterior = []
        for idx, part in participantes.iterrows():
            apostas_anteriores = apostas_df[
                (apostas_df['usuario_id'] == part['id']) &
                (apostas_df['prova_id'].isin(provas_ate_penultima))
            ].sort_values('prova_id')
            pontos_anteriores = calcular_pontuacao_lote(apostas_anteriores, resultados_df, provas_df)
            total_anteriores = sum([p for p in pontos_anteriores if p is not None])
            tabela_anterior.append({
                "Participante": part['nome'],
                "usuario_id": part['id'],
                "Pontos Provas": total_anteriores
            })
        df_class_anterior = pd.DataFrame(tabela_anterior)
        df_class_anterior = df_class_anterior.sort_values("Pontos Provas", ascending=False).reset_index(drop=True)
        df_class_anterior['Posição Anterior'] = df_class_anterior.index + 1
        df_class = df_class.merge(
            df_class_anterior[['usuario_id', 'Posição Anterior']],
            on='usuario_id',
            how='left'
        )
        def movimento(row):
            if pd.isnull(row['Posição Anterior']):
                return "Novo"
            diff = int(row['Posição Anterior']) - int(row['Posição'])
            if diff > 0:
                return f"Subiu {diff}"
            elif diff < 0:
                return f"Caiu {abs(diff)}"
            else:
                return "Permaneceu"
        df_class['Movimentação'] = df_class.apply(movimento, axis=1)
    else:
        df_class['Movimentação'] = "Novo"

    # 3. Diferença de pontos para cada linha (exceto a primeira)
    pontos_float = [float(x) for x in df_class["Pontos Provas"]]
    diferencas = [0]
    for i in range(1, len(pontos_float)):
        diferencas.append(pontos_float[i-1] - pontos_float[i])
    df_class["Diferença"] = ["-" if i == 0 else f"{d:.2f}" for i, d in enumerate(diferencas)]

    colunas_ordem = ["Posição", "Participante", "Pontos Provas", "Diferença", "Movimentação"]

    st.subheader("Classificação Geral - Apenas Provas")
    st.table(df_class[colunas_ordem])

    # 4. Pontuação final (Provas + Campeonato)
    resultado_campeonato = get_final_results()
    tabela_classificacao_completa = []

    for idx, part in participantes.iterrows():
        apostas_part = apostas_df[apostas_df['usuario_id'] == part['id']].sort_values('prova_id')
        pontos_part = calcular_pontuacao_lote(apostas_part, resultados_df, provas_df)
        pontos_provas = sum([p for p in pontos_part if p is not None])
        aposta = get_championship_bet(part['id'])
        pontos_campeonato = 0
        acertos = []
        if resultado_campeonato and aposta:
            if resultado_campeonato.get("champion") == aposta.get("champion"):
                pontos_campeonato += 150
                acertos.append("Campeão")
            if resultado_campeonato.get("vice") == aposta.get("vice"):
                pontos_campeonato += 100
                acertos.append("Vice")
            if resultado_campeonato.get("team") == aposta.get("team"):
                pontos_campeonato += 80
                acertos.append("Equipe")
        total_geral = pontos_provas + pontos_campeonato
        tabela_classificacao_completa.append({
            "Participante": part['nome'],
            "Pontos Provas": pontos_provas,
            "Pontos Campeonato": pontos_campeonato,
            "Total Geral": total_geral,
            "Acertos Campeonato": ", ".join(acertos) if acertos else "-"
        })

    df_class_completo = pd.DataFrame(tabela_classificacao_completa)
    df_class_completo = df_class_completo.sort_values("Total Geral", ascending=False).reset_index(drop=True)
    for col in ["Pontos Provas", "Pontos Campeonato", "Total Geral"]:
        df_class_completo[col] = df_class_completo[col].apply(lambda x: f"{x:.2f}")
    st.subheader("Classificação Final (Provas + Campeonato)")
    st.table(df_class_completo)

    # 5. Pontuação por Prova (detalhe)
    st.subheader("Pontuação por Prova")
    provas_df_ord = provas_df.sort_values('id')
    provas_nomes = provas_df_ord['nome'].tolist()
    provas_ids_ordenados = provas_df_ord['id'].tolist()
    dados_cruzados = {prova_nome: {} for prova_nome in provas_nomes}
    for part in tabela_detalhada:
        participante = part['Participante']
        pontos_por_prova = {}
        usuario_id = participantes[participantes['nome'] == participante].iloc[0]['id']
        apostas_part = apostas_df[apostas_df['usuario_id'] == usuario_id]
        for _, aposta in apostas_part.iterrows():
            pontos = calcular_pontuacao_lote(pd.DataFrame([aposta]), resultados_df, provas_df)
            if pontos:
                pontos_por_prova[aposta['prova_id']] = pontos[0]
        for prova_id, prova_nome in zip(provas_ids_ordenados, provas_nomes):
            pontos = pontos_por_prova.get(prova_id, 0)
            dados_cruzados[prova_nome][participante] = pontos if pontos is not None else 0
    df_cruzada = pd.DataFrame(dados_cruzados).T
    df_cruzada = df_cruzada.reindex(columns=[p['nome'] for _, p in participantes.iterrows()], fill_value=0)
    df_cruzada = df_cruzada.applymap(lambda x: f"{x:.2f}")
    st.dataframe(df_cruzada)

    # 6. Gráfico de evolução da pontuação acumulada
    st.subheader("Evolução da Pontuação Acumulada")
    if not df_cruzada.empty:
        import plotly.graph_objects as go
        fig = go.Figure()
        for participante in df_cruzada.columns:
            pontos_acumulados = df_cruzada[participante].astype(float).cumsum()
            fig.add_trace(go.Scatter(
                x=df_cruzada.index.tolist(),
                y=pontos_acumulados,
                mode='lines+markers',
                name=participante
            ))
        fig.update_layout(
            title="Evolução da Pontuação Acumulada",
            xaxis_title="Prova",
            yaxis_title="Pontuação Acumulada",
            xaxis_tickangle=-45,
            margin=dict(l=40, r=20, t=60, b=80),
            plot_bgcolor='rgba(240,240,255,0.9)',
            yaxis=dict(tickformat=',.0f')
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados para exibir o gráfico de evolução.")

    # 7. Gráfico geral de posições de todos
    st.subheader("Classificação de Cada Participante ao Longo do Campeonato")
    conn = db_connect()
    df_posicoes = pd.read_sql('SELECT * FROM posicoes_participantes', conn)
    conn.close()
    fig_all = go.Figure()
    for part in participantes['nome']:
        usuario_id = participantes[participantes['nome'] == part].iloc[0]['id']
        posicoes_part = df_posicoes[df_posicoes['usuario_id'] == usuario_id].sort_values('prova_id')
        if not posicoes_part.empty:
            fig_all.add_trace(go.Scatter(
                x=[provas_df[provas_df['id']==pid]['nome'].values[0] for pid in posicoes_part['prova_id']],
                y=posicoes_part['posicao'],
                mode='lines+markers',
                name=part
            ))
    fig_all.update_yaxes(autorange="reversed")
    fig_all.update_layout(
        xaxis_title="Prova",
        yaxis_title="Posição",
        legend_title="Participante"
    )
    st.plotly_chart(fig_all, use_container_width=True)

if __name__ == "__main__":
    main()
