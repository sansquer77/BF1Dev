import streamlit as st
import pandas as pd
import os
from pathlib import Path

DB_PATH = Path("bolao_f1Dev.db")

def download_db():
    """Permite fazer o download do arquivo inteiro do banco de dados SQLite."""
    if DB_PATH.exists():
        with open(DB_PATH, "rb") as fp:
            st.download_button(
                label="⬇️ Baixar banco de dados completo (.db)",
                data=fp,
                file_name=DB_PATH.name,
                mime="application/octet-stream",
                use_container_width=True
            )
    else:
        st.warning("Arquivo do banco de dados não encontrado.")

def upload_db():
    """Permite upload de um novo arquivo .db, substituindo o banco atual."""
    uploaded_file = st.file_uploader(
        "Faça upload de um arquivo .db para substituir todo o banco atual",
        type=["db", "sqlite"],
        key="upload_whole_db"
    )
    if uploaded_file is not None:
        with open(DB_PATH, "wb") as out:
            out.write(uploaded_file.getbuffer())
        st.success("Banco de dados substituído com sucesso!")

def listar_tabelas():
    """Retorna o nome de todas as tabelas do banco de dados."""
    import sqlite3
    with sqlite3.connect(DB_PATH) as conn:
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        tabelas = pd.read_sql(query, conn)["name"].tolist()
    return tabelas

def exportar_tabela_excel(tabela):
    """Exporta uma tabela como arquivo Excel."""
    import sqlite3
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql(f"SELECT * FROM {tabela}", conn)
    if df.empty:
        st.info(f"Tabela '{tabela}' está vazia.")
        return None
    excel_bytes = df.to_excel(None, index=False, engine="openpyxl")
    return excel_bytes

def download_tabela():
    """Permite download selecionado de uma tabela em formato Excel."""
    tabelas = listar_tabelas()
    tabela = st.selectbox("Escolha uma tabela para exportar:", tabelas, key="select_export")
    if st.button("Exportar tabela", key="btn_exportar"):
        excel_data = exportar_tabela_excel(tabela)
        if excel_data is not None:
            st.download_button(
                label=f"⬇️ Baixar tabela {tabela} (.xlsx)",
                data=excel_data,
                file_name=f"{tabela}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

def upload_tabela():
    """Permite upload de uma tabela Excel que será inserida/substituída no banco."""
    tabelas = listar_tabelas()
    tabela = st.selectbox("Escolha a tabela para sobrescrever:", tabelas, key="select_import")
    uploaded_file = st.file_uploader(
        f"Upload do arquivo .xlsx para substituir dados da tabela '{tabela}'",
        type=["xlsx"], key="upload_one_table"
    )
    if uploaded_file is not None and tabela:
        df = pd.read_excel(uploaded_file)
        import sqlite3
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(f"DELETE FROM {tabela}")
            df.to_sql(tabela, conn, if_exists='append', index=False)
        st.success(f"Tabela '{tabela}' atualizada com sucesso!")

def main():
    st.title("💾 Backup e Restauração do Banco de Dados")
    st.markdown("""
    - **Download Completo:** Baixe uma cópia do banco inteiro (.db).
    - **Upload Completo:** Substitua todo o banco de dados por um novo arquivo.
    - **Exportar tabela:** Exporte uma tabela específica (.xlsx).
    - **Importar tabela:** Importe dados para uma tabela específica (sobrescreve).
    """)

    st.header("Backup/Restauração do arquivo completo (.db)")
    col1, col2 = st.columns(2)
    with col1:
        download_db()
    with col2:
        upload_db()

    st.divider()
    st.header("Backup/Restauração de tabelas específicas")
    tab1, tab2 = st.tabs(["Exportar Tabela", "Importar Tabela"])
    with tab1:
        download_tabela()
    with tab2:
        upload_tabela()
