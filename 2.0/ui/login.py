import streamlit as st
from services.auth_service import (
    autenticar_usuario,
    cadastrar_usuario,
    generate_token,
    get_user_by_email,
    hash_password
)
from services.email_service import enviar_email_recuperacao_senha
from datetime import datetime, timedelta
import extra_streamlit_components as stx

def login_view():
    st.title("Login do BF1")

    # Estados de navegação das telas
    if "esqueceu_senha" not in st.session_state:
        st.session_state["esqueceu_senha"] = False
    if "criar_usuario" not in st.session_state:
        st.session_state["criar_usuario"] = False

    cookie_manager = stx.CookieManager()

    # Tela padrão de login
    if not st.session_state["esqueceu_senha"] and not st.session_state["criar_usuario"]:
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            if st.button("Entrar"):
                user = autenticar_usuario(email, senha)
                if user:
                    token = generate_token(user[0], user[4], user[5])
                    st.session_state["token"] = token
                    st.session_state["user_id"] = user[0]
                    st.session_state["user_role"] = user[4]
                    st.session_state["pagina"] = "Painel do Participante"

                    expire_time = datetime.now() + timedelta(minutes=120)
                    cookie_manager.set(
                        "session_token",
                        token,
                        expires_at=expire_time,
                        secure=True
                    )
                    st.success(f"Bem-vindo, {user[1]}!")
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos.")

        with col2:
            if st.button("Esqueceu a senha?"):
                st.session_state["esqueceu_senha"] = True

        with col3:
            if st.button("Criar usuário"):
                st.session_state["criar_usuario"] = True

        # Bloco do badge/link da DigitalOcean como na versão original
        st.markdown(
            """
            <div style="margin-top: 2em; text-align: center;">
                <a href="https://www.digitalocean.com/?refcode=7a57329868da&utm_campaign=Referral_Invite&utm_medium=Referral_Program&utm_source=badge" target="_blank">
                    <img src="https://web-platforms.sfo2.cdn.digitaloceanspaces.com/WWW/Badge%201.svg" alt="DigitalOcean Referral Badge" style="width:160px;" />
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Tela "Esqueceu a senha"
    elif st.session_state["esqueceu_senha"]:
        st.subheader("Recuperação de Senha")
        email_reset = st.text_input("Informe o email cadastrado")
        nova_senha = st.text_input("Nova senha", type="password")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Salvar nova senha"):
                usuario = get_user_by_email(email_reset)
                if usuario:
                    nova_hash = hash_password(nova_senha)
                    from db.db_utils import db_connect
                    conn = db_connect()
                    c = conn.cursor()
                    c.execute('UPDATE usuarios SET senha_hash=? WHERE email=?', (nova_hash, email_reset))
                    conn.commit()
                    conn.close()
                    st.success("Senha redefinida com sucesso. Você já pode fazer login.")
                    try:
                        enviar_email_recuperacao_senha(email_reset, nova_senha)
                    except Exception:
                        st.info("Não foi possível enviar o e-mail de confirmação.")
                    st.session_state["esqueceu_senha"] = False
                else:
                    st.error("Email não cadastrado.")
        with col2:
            if st.button("Voltar ao login"):
                st.session_state["esqueceu_senha"] = False

    # Tela "Criar usuário"
    elif st.session_state["criar_usuario"]:
        st.subheader("Cadastro de Novo Usuário")
        nome = st.text_input("Nome completo")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Cadastrar"):
                if not nome or not email or not senha:
                    st.error("Preencha todos os campos!")
                else:
                    sucesso = cadastrar_usuario(nome, email, senha, perfil="participante", status="Inativo")
                    if sucesso:
                        st.success("Usuário cadastrado com sucesso! Aguarde ativação pela administração.")
                        st.session_state["criar_usuario"] = False
                    else:
                        st.error("Email já cadastrado.")
        with col2:
            if st.button("Voltar ao login", key="voltar_login_criar"):
                st.session_state["criar_usuario"] = False
