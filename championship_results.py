import streamlit as st
from championship_utils import save_final_results, get_final_results

def main():
    if st.session_state.get("user_role", "").strip().lower() != "master":
        st.error("Acesso restrito ao Master.")
        return

    st.title("🏆 Atualizar Resultado Final do Campeonato")

    # Exemplo: substitua pelos seus dados reais
    pilotos = [
    "Pierre Gasly", "Jack Doohan", "Fernando Alonso", "Lance Stroll",
    "Charles Leclerc", "Lewis Hamilton", "Esteban Ocon", "Oliver Bearman",
    "Lando Norris", "Oscar Piastri", "Kimi Antonelli", "George Russell",
    "Liam Lawson", "Isack Hadjar", "Max Verstappen", "Yuki Tsunoda",
    "Nico Hulkenberg", "Gabriel Bortoleto", "Alex Albon", "Carlos Sainz"
]
    equipes = ["Red Bull", "Mercedes", "Ferrari", "McLaren", "Alpine", "Aston Martin", "Haas", "Racing Bulls", "Sauber", "Williams"]

    with st.form("final_results_form"):
        campeao = st.selectbox("Piloto Campeão", pilotos)
        # Remove o campeão da lista de opções do vice
        vices_possiveis = [p for p in pilotos if p != campeao]
        vice = st.selectbox("Piloto Vice", vices_possiveis)
        equipe = st.selectbox("Equipe Campeã", equipes)
        submitted = st.form_submit_button("Salvar Resultado")
        if submitted:
            save_final_results(campeao, vice, equipe)
            st.success("Resultado oficial atualizado!")

    # Exibe o resultado atualmente armazenado
    resultado = get_final_results()
    st.subheader("Resultado Atual Armazenado")
    if resultado:
        st.markdown(f"""
        **Campeão:** {resultado['champion']}  
        **Vice:** {resultado['vice']}  
        **Equipe Campeã:** {resultado['team']}
        """)
    else:
        st.info("Nenhum resultado registrado ainda.")

    # --- TABELA COM TODAS AS APOSTAS ---
    st.title("📊 Todas as Apostas dos Participantes")

    apostas_df = get_apostas_df()
    usuarios_df = get_usuarios_df()
    provas_df = get_provas_df()

    if apostas_df.empty or usuarios_df.empty or provas_df.empty:
        st.info("Nenhuma aposta registrada ou tabelas vazias.")
        return

    # Junta informações do usuário e da prova para facilitar a visualização
    apostas_completas = apostas_df.merge(
        usuarios_df[['id', 'nome']], left_on='usuario_id', right_on='id', suffixes=('', '_usuario')
    ).merge(
        provas_df[['id', 'nome', 'data']], left_on='prova_id', right_on='id', suffixes=('', '_prova')
    )

    # Ajusta e renomeia as colunas para exibição
    apostas_completas = apostas_completas.rename(columns={
        'nome': 'Participante',
        'nome_prova': 'Prova',
        'data': 'Data'
    })

    # Seleciona apenas as colunas relevantes
    colunas = [
        'Participante', 'Prova', 'Data', 'pilotos', 'fichas', 'piloto_11', 'data_envio', 'automatica'
    ]
    apostas_completas = apostas_completas[colunas]

    # Ordena e exibe a tabela
    st.dataframe(
        apostas_completas.sort_values(['Data', 'Prova', 'Participante']),
        use_container_width=True
    )
