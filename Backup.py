import streamlit as st
import sqlite3
import os
import pandas as pd

def listar_tabelas(banco):
    if not os.path.exists(banco):
        return []
    conn = sqlite3.connect(banco)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tabelas = [row[0] for row in c.fetchall()]
    conn.close()
    return tabelas

def backup_banco(origem_db, arquivo_backup, tabela=None):
    conn = sqlite3.connect(origem_db)
    with open(arquivo_backup, 'w', encoding='utf-8') as f:
        if tabela is None:
            for linha in conn.iterdump():
                f.write(f'{linha}\n')
        else:
            c = conn.cursor()
            c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (tabela,))
            create_table = c.fetchone()
            if create_table:
                f.write(f'{create_table[0]};\n')
                c.execute(f"SELECT * FROM {tabela}")
                rows = c.fetchall()
                for row in rows:
                    valores = ', '.join([f"'{str(v).replace('\'', '\'\'')}'" if v is not None else 'NULL' for v in row])
                    f.write(f"INSERT INTO {tabela} VALUES ({valores});\n")
            else:
                raise ValueError(f'Tabela {tabela} não encontrada no banco.')
    conn.close()

def restaurar_banco(destino_db, arquivo_backup):
    if not os.path.exists(arquivo_backup):
        st.error(f'Arquivo {arquivo_backup} não encontrado!')
        return
    if os.path.exists(destino_db):
        os.remove(destino_db)
    conn = sqlite3.connect(destino_db)
    with open(arquivo_backup, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    conn.executescript(sql_script)
    conn.close()

def visualizar_tabela(banco, tabela):
    conn = sqlite3.connect(banco)
    df = pd.read_sql(f"SELECT * FROM {tabela}", conn)
    conn.close()
    return df

def main():
    st.set_page_config(page_title="Backup, Restore e Visualização", layout="wide")
    st.title("Backup, Restore e Visualização do Banco de Dados")

    menu = st.sidebar.radio("Menu", ["Backup", "Restore", "Visualizar e Exportar"])

    if menu == "Backup":
        st.header("Backup do Banco de Dados")
        banco_origem = st.text_input('Caminho do banco de dados de origem', value='bolao_f1alpha.db')
        arquivo_backup = st.text_input('Nome do arquivo de backup (.sql)', value='backup_bolao.sql')
        tabelas = listar_tabelas(banco_origem) if os.path.exists(banco_origem) else []
        tabela_escolhida = st.selectbox("Tabela para backup (opcional)", ['-- Banco Completo --'] + tabelas)
        if st.button("Fazer Backup"):
            try:
                if tabela_escolhida == '-- Banco Completo --':
                    backup_banco(banco_origem, arquivo_backup)
                    st.success(f'Backup do banco completo realizado em: {arquivo_backup}')
                else:
                    backup_banco(banco_origem, arquivo_backup, tabela_escolhida)
                    st.success(f'Backup da tabela {tabela_escolhida} realizado em: {arquivo_backup}')
            except Exception as e:
                st.error(f'Erro ao fazer backup: {e}')

    elif menu == "Restore":
        st.header("Restauração do Banco de Dados")
        arquivo_backup = st.text_input('Nome do arquivo de backup para restauração (.sql)', value='backup_bolao.sql', key='rest')
        banco_destino = st.text_input('Caminho do banco de dados para restaurar', value='bolao_f1alpha_restaurado.db', key='rest2')
        if st.button("Restaurar Banco"):
            try:
                restaurar_banco(banco_destino, arquivo_backup)
                st.success(f'Banco restaurado com sucesso a partir de: {arquivo_backup}')
            except Exception as e:
                st.error(f'Erro ao restaurar banco: {e}')

    elif menu == "Visualizar e Exportar":
        st.header("Visualização e Exportação de Tabelas")
        banco = st.text_input("Caminho do banco de dados", value="bolao_f1alpha.db", key="visu")
        tabelas = listar_tabelas(banco) if os.path.exists(banco) else []
        if tabelas:
            tabela = st.selectbox("Escolha a tabela para visualizar", tabelas)
            if tabela:
                df = visualizar_tabela(banco, tabela)
                st.dataframe(df)
                # Exportação para Excel
                xlsx = df.to_excel(index=False, engine='openpyxl')
                st.download_button(
                    label="Exportar dados para Excel",
                    data=xlsx,
                    file_name=f"{tabela}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("Nenhuma tabela encontrada no banco de dados ou banco não existe.")

if __name__ == '__main__':
    main()
