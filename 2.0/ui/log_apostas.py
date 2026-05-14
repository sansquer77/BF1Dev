import streamlit as st
import pandas as pd
from db.db_utils import db_connect
import extra_streamlit_components as stx
import jwt
import os


def carregar_logs():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM log_apostas ORDER BY id DESC', conn)
    conn.close()
    return df


def get_nome_from_cookie():
    cookie_manager = stx.CookieManager()
    cookies = cookie_manager.get_all()
    token = cookies.get("session_token")
    nome_do_cookie = None
    if token:
        try:
            JWT_SECRET = st.secrets["JWT_SECRET"] or os.environ.get(
                "JWT_SECRET")
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            nome_do_cookie = payload.get("nome")
        except Exception:
            pass
    return nome_do_cookie


def main():
    st.title("📜 Log de Apostas")

    perfil = st.session_state.get("user_role", "participante")

    # Usa o nome do cookie se não for perfil admin/master
    nome_usuario = None
    if perfil not in ("admin", "master"):
        nome_usuario = get_nome_from_cookie()
    else:
        # ou pode não usar, depende dos filtros
        nome_usuario = st.session_state.get("user_name")

    df = carregar_logs()
    if df.empty:
        st.warning("Nenhum registro no log de apostas.")
        return

    tipos_map = {0: "Dentro do Prazo", 1: "Fora do Prazo"}

    st.markdown("### Filtros")
    colunas_filtro = []
    if perfil in ("admin", "master"):
        colunas_filtro.append("apostador")
    cols = st.columns(3)
    idx_filtro = 0

    if "apostador" in colunas_filtro:
        apostador_opcoes = ["Todos"] + sorted(df["apostador"].unique())
        apostador_sel = cols[idx_filtro].selectbox(
            "Apostador", apostador_opcoes)
        idx_filtro += 1
    else:
        apostador_sel = nome_usuario

    tipo_filtro = cols[idx_filtro].selectbox(
        "Tipo de Aposta", ["Todas"] + list(tipos_map.values())
    )
    idx_filtro += 1
    data_sel = cols[idx_filtro].selectbox(
        "Data", ["Todas"] + sorted(df["data"].unique(), reverse=True)
    )

    mostrar_automaticas = st.checkbox(
        "Mostrar apenas apostas automáticas (automatica > 0)", value=False)

    filtro = df.copy()
    # st.write("nome_usuario do cookie:", nome_usuario)
    # st.write("Valores únicos de apostador no log:", df['apostador'].unique())

    if perfil in ("admin", "master"):
        if apostador_sel != "Todos":
            filtro = filtro[filtro["apostador"] == apostador_sel]
    else:
        if nome_usuario:  # Só filtra se cookie está correto
            filtro = filtro[filtro["apostador"] == nome_usuario]
        else:
            st.info("Sessão inválida ou expirada. Faça login novamente.")
            return

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

    filtro_show = filtro.copy()
    filtro_show["Tipo de Aposta"] = filtro["tipo_aposta"].map(tipos_map)
    filtro_show["Automática"] = filtro["automatica"].apply(
        lambda x: "Sim" if x > 0 else "Não")

    colunas_exibir = [
        "data",
        "horario",
        "apostador",
        "nome_prova",
        "aposta",
        "piloto_11",
        "Tipo de Aposta",
        "Automática"]
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

    st.caption(
        "*O campo 'Automática' indica apostas geradas automaticamente pelo sistema (qualquer valor > 0 no campo).*")


if __name__ == "__main__":
    main()
