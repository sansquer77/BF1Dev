import streamlit as st


def main():
    st.title("ℹ️ Sobre o BF1")

    st.markdown("""
    ## 🏁 BF1 - Bolão de Fórmula 1

    **BF1** é um sistema digital de bolão esportivo dedicado à Fórmula 1, criado para proporcionar organização, transparência e diversão para grupos de amigos e entusiastas da categoria. O aplicativo centraliza apostas, classificação, estatísticas e comunicação em uma plataforma intuitiva, segura e acessível via web.

    ### ✒️ Funcionalidades principais

    - Cadastro e gestão de apostas para cada corrida
    - Aposta especial do campeonato (campeão, vice e equipe)
    - Classificação geral e por corrida
    - Relatórios, análise detalhada e logs de apostas
    - Painel de usuários e administração completa
    - Exportação/importação de dados e backup seguro
    - Regulamento oficial, gestão de provas e pilotos

    ### 👨‍💻 Desenvolvimento

    - **Desenvolvedor:** Cristiano Gaspar (administração e código), colaboração de usuários-masters.
    - **Tecnologias:** Python, Streamlit, SQLite, pandas, Plotly, bcrypt, JWT, extra-streamlit-components

    ### 💡 Missão e inspiração

    O BF1 nasceu da paixão pelas corridas e pela convivência entre amigos—buscando promover interação, rivalidade saudável, controle rigoroso das apostas e distribuição transparente dos prêmios.

    ### 📬 Contato e créditos

    - Para dúvidas, sugestões ou reportar bugs:
        - **E-mail:** cristiano_gaspar@outlook.com

    - Agradecimentos a todos os participantes e beta testers do bolão ao longo dos anos.

    ### ☁️ Infraestrutura

    O BF1 está hospedado em ambiente cloud, utilizando serviços como Digital Ocean para performance, redundância e automação de backups.

    ---
    <small>Versão atual: 2.0-2025. Todos os direitos reservados.</small>
    """)


if __name__ == "__main__":
    main()
