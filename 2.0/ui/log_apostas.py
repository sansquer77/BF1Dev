import streamlit as st
import pandas as pd
from db.db_utils import db_connect

def carregar_logs():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM log_apostas ORDER BY id DESC', conn)
    conn.close()
    return df

def main():
    st.title("📜 Log de Apostas")

    df = carregar_logs()
    if df.empty:
        st.warning("Nenhum registro no log de apostas.")
        return

    # Dicionário para tipo_aposta
    tipos_map = {0: "Dentro do Prazo", 1: "Fora do Prazo"}

    st.markdown("### Filtros")
    col1, col2, col3 = st.columns(3)
    with col1:
        apostador_sel = st.selectbox("Apostador", ["Todos"] + sorted(df["apostador"].unique()))
    with col2:
        tipo_filtro = st.selectbox("Tipo de Aposta", ["Todas"] + list(tipos_map.values()))
    with col3:
        data_sel = st.selectbox("Data", ["Todas"] + sorted(df["data"].unique(), reverse=True))

    mostrar_automaticas = st.checkbox("Mostrar apenas apostas automáticas (automatica > 0)", value=False)

    filtro = df.copy()
    if apostador_sel != "Todos":
        filtro = filtro[filtro["apostador"] == apostador_sel]
    if tipo_filtro != "Todas":
        inv_tipos_map = {v: k for k, v in tipos_map.items()}
        filtro = filtro[filtro["tipo_aposta"] == inv_tipos_map[tipo_filtro]]
    if data_sel != "Todas":
        filtro = filtro[filtro["data"] == data_sel]
    if mostrar_automaticas:
        filtro = filtro[filtro["automatica"] > 0]

    if filtro.empty:
        st.info("Nenhum registro encontrado com os filtros selecionados.")
        return

    # Ajusta as colunas exibidas e o título do tipo de aposta
    filtro_show = filtro.copy()
    filtro_show["Tipo de Aposta"] = filtro["tipo_aposta"].map(tipos_map)
    filtro_show["Automática"] = filtro["automatica"].apply(lambda x: "Sim" if x > 0 else "Não")

    colunas_exibir = ["data", "horario", "apostador", "nome_prova", "aposta", "piloto_11", "Tipo de Aposta", "Automática"]
    if "automatica" in filtro_show.columns and "tipo_aposta" in filtro_show.columns:
        st.dataframe(
            filtro_show[colunas_exibir].rename(columns={
                "data": "Data",
                "horario": "Horário",
                "apostador": "Apostador",
                "nome_prova": "Prova",
                "aposta": "Pilotos/Fichas",
                "piloto_11": "11º Colocado"
            }),
            use_container_width=True
        )
    else:
        st.dataframe(filtro_show, use_container_width=True)

    st.caption("*O campo 'Automática' indica apostas geradas automaticamente pelo sistema (qualquer valor > 0 no campo).*")

if __name__ == "__main__":
    main()
