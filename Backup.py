import streamlit as st
import os

def main():
    # Configurações da página
    st.set_page_config(
        page_title="Backup dos Bancos de Dados",
        page_icon=":floppy_disk:",
        layout="wide"
    )

    # Título da página
    st.title("Backup dos Bancos de Dados SQLite")

    # Instruções para o usuário
    st.markdown("""
    Esta página permite que você baixe os bancos de dados SQLite utilizados pelo sistema.
    Certifique-se de fazer backup regularmente para evitar perda de dados.
    """)
    # Lista dos bancos definidos
    db_files = [
        ("bolao_f1Dev.db", "Banco Principal (corridas)"),
        ("championship.db", "Banco do Campeonato")
    ]

    st.title("Download dos Bancos de Dados SQLite")

    for db_filename, db_label in db_files:
        if os.path.exists(db_filename):
            with open(db_filename, "rb") as fp:
                st.download_button(
                    label=f"Baixar {db_label}",
                    data=fp,
                    file_name=db_filename,
                    mime="application/octet-stream"
                )
        else:
            st.warning(f"Arquivo {db_filename} não encontrado.")
