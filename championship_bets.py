import streamlit as st
from championship_utils import save_championship_bet, get_championship_bet, get_championship_bet_log

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
    aposta = get_championship_bet(user_id)
    if aposta:
        campeao_apostado = aposta.get('champion')
        vice_apostado = aposta.get('vice')
        equipe_apostada = aposta.get('team')
    else:
        campeao_apostado = vice_apostado = equipe_apostada = None

    # Formulário de apostas
    with st.form("championship_bet_form"):
        campeao = st.selectbox("Campeão", pilotos, index=pilotos.index(campeao_apostado) if campeao_apostado else 0)
        vice = st.selectbox("Vice", pilotos, index=pilotos.index(vice_apostado) if vice_apostado else 1)
        equipe = st.selectbox("Equipe Campeã", equipes, index=equipes.index(equipe_apostada) if equipe_apostada else 0)
        
        if st.form_submit_button("Salvar Aposta"):
            save_championship_bet(user_id, campeao, vice, equipe)
            st.success("Aposta registrada!")

    # Log de apostas
    log = get_championship_bet_log(user_id)

    # Garante que log é uma lista e que cada entrada tem 4 elementos
    if log and all(len(entry) == 4 for entry in log):
        df_log = pd.DataFrame(log, columns=["Campeão", "Vice", "Equipe", "Data/Hora"])
        st.dataframe(df_log)
    elif log:
        st.warning("Há apostas registradas, mas alguns registros estão inconsistentes.")
    else:
        st.info("Nenhuma aposta registrada ainda.")
