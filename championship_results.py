import streamlit as st
from championship_utils import save_final_results

def main():
    if st.session_state.get("user_role") != "Master":
        st.error("Acesso restrito ao Master.")
        return

    st.title("Definir Resultado Oficial")
    pilotos = ["Max Verstappen", "Lewis Hamilton", ...]  
    equipes = ["Red Bull", "Mercedes", ...]  

    with st.form("final_results_form"):
        campeao = st.selectbox("Campeão", pilotos)
        vice = st.selectbox("Vice", pilotos)
        equipe = st.selectbox("Equipe Campeã", equipes)
        
        if st.form_submit_button("Salvar Resultado"):
            save_final_results(campeao, vice, equipe)
            st.success("Resultado oficial atualizado!")
