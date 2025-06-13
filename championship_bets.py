import streamlit as st
from championship_utils import save_championship_bet, get_championship_bet

def main():
    st.title("Apostas no Campeonato")
    user_id = st.session_state.get("user_id")
    
    if not user_id:
        st.error("Faça login para apostar.")
        return

    # Carregar pilotos e equipes (ajuste conforme seu sistema)
    pilotos = ["Max Verstappen", "Geroge Russell", "Leclerc"]  
    equipes = ["Red Bull", "Mercedes", "Ferrari"]  

    # Carregar apostas existentes
    campeao_apostado, vice_apostado, equipe_apostada = get_championship_bet(user_id)

    # Formulário de apostas
    with st.form("championship_bet_form"):
        campeao = st.selectbox("Campeão", pilotos, index=pilotos.index(campeao_apostado) if campeao_apostado else 0)
        vice = st.selectbox("Vice", pilotos, index=pilotos.index(vice_apostado) if vice_apostado else 1)
        equipe = st.selectbox("Equipe Campeã", equipes, index=equipes.index(equipe_apostada) if equipe_apostada else 0)
        
        if st.form_submit_button("Salvar Aposta"):
            save_championship_bet(user_id, campeao, vice, equipe)
            st.success("Aposta registrada!")
