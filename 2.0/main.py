import streamlit as st

# Importação dos módulos de interface
from ui.login import login_view
from ui.dashboard import dashboard_view
from ui.backup import backup_view
from ui.analysis import analysis_view
from ui.championship_bets import championship_bets_view
from ui.championship_results import championship_results_view

# Configuração geral da página
st.set_page_config(
    page_title="BF1",
    page_icon="🏁",
    layout="wide"
)

# Dicionário de rotas/páginas
PAGES = {
    "Login": login_view,
    "Painel do Participante": dashboard_view,
    "Backup dos Bancos de Dados": backup_view,
    "Análise de Apostas": analysis_view,
    "Apostas Campeonato": championship_bets_view,
    "Resultado Campeonato": championship_results_view,
    # ...adicione novas páginas conforme necessário
}

# Inicialização do estado da sessão
if "pagina" not in st.session_state:
    st.session_state["pagina"] = "Login"
if "token" not in st.session_state:
    st.session_state["token"] = None

def sidebar_menu():
    """Cria o menu lateral com base no perfil do usuário logado"""
    menu_items = []
    token = st.session_state.get("token")

    if not token:
        menu_items = ["Login"]
    else:
        # Exemplo de controle de menu por perfil (usuário pode customizar)
        perfil = st.session_state.get("user_role", "participante")
        if perfil == "master":
            menu_items = [
                "Painel do Participante",
                "Backup dos Bancos de Dados",
                "Análise de Apostas",
                "Apostas Campeonato",
                "Resultado Campeonato",
                "Logout"
            ]
        elif perfil == "admin":
            menu_items = [
                "Painel do Participante",
                "Análise de Apostas",
                "Apostas Campeonato",
                "Resultado Campeonato",
                "Logout"
            ]
        else:
            menu_items = [
                "Painel do Participante",
                "Apostas Campeonato",
                "Resultado Campeonato",
                "Análise de Apostas",
                "Logout"
            ]
    escolha = st.sidebar.radio("Menu", menu_items)
    st.session_state["pagina"] = escolha

def main():
    # Exibe o menu lateral
    sidebar_menu()
    pagina = st.session_state["pagina"]

    # Logout
    if pagina == "Logout":
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.sidebar.success("Logout realizado com sucesso.")
        st.rerun()
        return

    # Chama a view/página correspondente
    if pagina in PAGES:
        PAGES[pagina]()
    else:
        st.error("Página não encontrada.")

if __name__ == "__main__":
    main()
