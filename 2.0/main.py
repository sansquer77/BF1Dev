import streamlit as st

# INICIALIZAÇÃO DO BANCO
from db.db_utils import init_db
init_db()

# IMPORTAÇÃO DAS VIEWS/MÓDULOS DE INTERFACE
from ui.login import login_view
from ui.painel import participante_view
from ui.usuarios import main as usuarios_view
from ui.championship_bets import main as championship_bets_view
from ui.championship_results import main as championship_results_view
from ui.gestao_apostas import main as gestao_apostas_view
from ui.analysis import main as analysis_view
from ui.regulamento import main as regulamento_view
from ui.classificacao import main as classificacao_view
from ui.log_apostas import main as log_apostas_view
from ui.gestao_provas import main as gestao_provas_view
from ui.gestao_pilotos import main as gestao_pilotos_view
from ui.backup import main as backup_view
from ui.dashboard import main as dashboard_view
from ui.sobre import main as sobre_view

from utils.security import decode_token

# ESTADO INICIAL DA SESSÃO
if 'pagina' not in st.session_state:
    st.session_state['pagina'] = "Login"
if 'token' not in st.session_state:
    st.session_state['token'] = None

# MENUS POR PERFIL
def menu_master():
    return [
        "Painel do Participante",
        "Gestão de Usuários",
        "Gestão de Pilotos",
        "Gestão de Provas",
        "Gestão de Apostas",
        "Análise de Apostas",
        "Atualização de resultados",
        "Apostas Campeonato",
        "Resultado Campeonato",
        "Log de Apostas",
        "Classificação",
        "Dashboard F1",
        "Exportar/Importar Excel",
        "Backup dos Bancos de Dados",
        "Regulamento",
        "Sobre",
        "Logout"
    ]
def menu_admin():
    return [
        "Painel do Participante",
        "Gestão de Apostas",
        "Gestão de Pilotos",
        "Gestão de Provas",
        "Análise de Apostas",
        "Atualização de resultados",
        "Apostas Campeonato",
        "Resultado Campeonato",
        "Log de Apostas",
        "Classificação",
        "Dashboard F1",
        "Regulamento",
        "Sobre",
        "Logout"
    ]
def menu_participante():
    return [
        "Painel do Participante",
        "Apostas Campeonato",
        "Análise de Apostas",
        "Log de Apostas",
        "Classificação",
        "Dashboard F1",
        "Regulamento",
        "Sobre",
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

# DICIONÁRIO DE ROTAS
PAGES = {
    "Login": login_view,
    "Painel do Participante": participante_view,
    "Gestão de Usuários": usuarios_view,
    "Gestão de Pilotos": gestao_pilotos_view,
    "Gestão de Provas": gestao_provas_view,
    "Gestão de Apostas": gestao_apostas_view,
    "Análise de Apostas": analysis_view,
    "Atualização de resultados": championship_results_view,
    "Apostas Campeonato": championship_bets_view,
    "Resultado Campeonato": championship_results_view,
    "Log de Apostas": log_apostas_view,
    "Classificação": classificacao_view,
    "Dashboard F1": dashboard_view,
    "Exportar/Importar Excel": backup_view,
    "Backup dos Bancos de Dados": backup_view,
    "Regulamento": regulamento_view,
    "Sobre": sobre_view,
}

# MENU LATERAL POR PERFIL
def sidebar_menu():
    token = st.session_state.get("token")
    if not token:
        menu_items = ["Login"]
    else:
        perfil = st.session_state.get("user_role", "participante")
        if perfil == "master":
            menu_items = menu_master()
        elif perfil == "admin":
            menu_items = menu_admin()
        else:
            menu_items = menu_participante()
    escolha = st.sidebar.radio("Menu", menu_items, key="menu_lateral")
    st.session_state["pagina"] = escolha

# APP PRINCIPAL
def main():
    st.set_page_config(
        page_title="BF1Dev",
        page_icon="🏁",
        layout="wide"
    )
    sidebar_menu()
    pagina = st.session_state["pagina"]

    # LOGOUT
    if pagina == "Logout":
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.sidebar.success("Logout realizado com sucesso.")
        st.rerun()
        return

    # EXECUTA A VIEW DA PÁGINA ESCOLHIDA
    if pagina in PAGES:
        PAGES[pagina]()
    else:
        st.error("Página não encontrada.")

if __name__ == "__main__":
    main()
