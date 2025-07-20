import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

EMAIL_REMETENTE = st.secrets["EMAIL_REMETENTE"]
SENHA_REMETENTE = st.secrets["SENHA_EMAIL"]
EMAIL_ADMIN = st.secrets.get("EMAIL_ADMIN", "")

def enviar_email(destinatario: str, assunto: str, corpo_html: str) -> bool:
    """Envia um e-mail HTML para o destinatário informado."""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = destinatario
    msg['Subject'] = assunto
    msg.attach(MIMEText(corpo_html, 'html'))
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_REMETENTE, SENHA_REMETENTE)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Erro no envio para {destinatario}: {str(e)}")
        return False

def enviar_email_confirmacao_aposta(email_usuario: str, nome_prova: str, pilotos: list, fichas: list, piloto_11: str, data_envio: str):
    """Envia e-mail de confirmação de aposta para o usuário e para o admin."""
    corpo_html = f"""
    <h3>Confirmação de Aposta - BF1</h3>
    <b>Prova:</b> {nome_prova}<br>
    <b>Pilotos:</b> {', '.join(pilotos)}<br>
    <b>Fichas:</b> {', '.join(map(str, fichas))}<br>
    <b>11º Colocado:</b> {piloto_11}<br>
    <b>Data/Hora:</b> {data_envio}
    """
    enviar_email(email_usuario, f"Confirmação de Aposta - {nome_prova}", corpo_html)
    if EMAIL_ADMIN:
        enviar_email(EMAIL_ADMIN, f"Nova aposta de {email_usuario}", corpo_html)

def enviar_email_recuperacao_senha(destinatario: str, nova_senha: str):
    """Envia um e-mail de recuperação de senha com a nova senha definida."""
    corpo_html = f"""
    <h3>Redefinição de Senha - BF1</h3>
    <b>Sua nova senha:</b> <code>{nova_senha}</code>
    <br>Recomendamos alterar a senha após o login.
    """
    enviar_email(destinatario, "Redefinição de Senha - BF1", corpo_html)
