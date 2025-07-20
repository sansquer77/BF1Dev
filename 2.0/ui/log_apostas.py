import streamlit as st
import pandas as pd
from db.db_utils import db_connect

def carregar_log_apostas():
    """
    Retorna o log detalhado de apostas como DataFrame.
    """
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM log_apostas', conn)
    conn.close()
    return df

def main():
    st.title("📝 Log de Apostas")

    perfil = st.session_state.get("user_role", "participante")
    if perfil not in ("admin", "master"):
        st.info("Acesso restrito. Essa área está disponível apenas para administradores.")
        return

    df = carregar_log_apostas()
    if df.empty:
        st.info("Nenhum log de aposta registrado até o momento.")
        return

    # Filtragem por participante, prova ou tipo de aposta
    st.markdown("### Filtros")
    col1, col2, col3 = st.columns(3)

    with col1:
        apostadores = sorted(df["apostador"].unique().tolist())
        apostador_filtro = st.selectbox("Participante", ["Todos"] + apostadores)
    with col2:
        provas = sorted(df["nome_prova"].unique().tolist())
        prova_filtro = st.selectbox("Prova", ["Todas"] + provas)
    with col3:
        tipos_map = {0: "Válida", 1: "Fora do prazo", 2: "Automática"}
        tipo_filtro = st.selectbox("Tipo de Aposta", ["Todas"] + list(tipos_map.values()))

    # Aplicação dos filtros
    filtro = df.copy()
    if apostador_filtro != "Todos":
        filtro = filtro[filtro["apostador"] == apostador_filtro]
    if prova_filtro != "Todas":
        filtro = filtro[filtro["nome_prova"] == prova_filtro]
    if tipo_filtro != "Todas":
        inv_tipos_map = {v: k for k, v in tipos_map.items()}
        filtro = filtro[filtro["tipo_aposta"] == inv_tipos_map[tipo_filtro]]

    # Exibição do log filtrado
    if filtro.empty:
        st.info("Nenhum registro encontrado para o filtro aplicado.")
    else:
        # Ordena por data/hora (mais recente primeiro)
        filtro = filtro.sort_values(by=["data", "horario"], ascending=[False, False])

        # Renomeia as colunas principais para exibição
        filtro_show = filtro[[
            "apostador", "data", "horario", "aposta", "piloto_11", "nome_prova",
            "tipo_aposta", "automatica"
        ]].copy()
        filtro_show.columns = [
            "Participante", "Data", "Horário", "Aposta", "11º Colocado", "Prova", "Tipo", "Automática"
        ]
        filtro_show["Tipo"] = filtro["tipo_aposta"].map(tipos_map)
        filtro_show["Automática"] = filtro["automatica"].map({0: "Não", 1: "Sim"})
        st.dataframe(filtro_show, use_container_width=True)

        # Opção de download do log filtrado
        csv = filtro_show.to_csv(index=False)
        st.download_button(
            label="⬇️ Baixar log filtrado (.csv)",
            data=csv,
            file_name="log_apostas_filtrado.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
