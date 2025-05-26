import streamlit as st
import os
import sqlite3

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

def listar_tabelas(banco):
    if not os.path.exists(banco):
        return []
    conn = sqlite3.connect(banco)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tabelas = [row[0] for row in c.fetchall()]
    conn.close()
    return tabelas

def app_backup_restore():
    st.title('Backup e Restauração do Banco de Dados')
    banco_origem = st.text_input('Caminho do banco de dados de origem', value='bolao_f1alpha.db')
    banco_destino = st.text_input('Caminho do banco de dados de destino', value='bolao_f1alpha_backup.db')
    arquivo_backup = st.text_input('Nome do arquivo de backup (.sql)', value='backup_bolao.sql')

    tabelas = listar_tabelas(banco_origem) if os.path.exists(banco_origem) else []

    st.subheader('Escolha a tabela para backup (opcional)')
    tabela_selecionada = st.selectbox('Tabela', ['-- Banco Completo --'] + tabelas)

    if st.button('Fazer Backup'):
        try:
            if tabela_selecionada == '-- Banco Completo --':
                backup_banco(banco_origem, arquivo_backup)
            else:
                backup_banco(banco_origem, arquivo_backup, tabela_selecionada)
            st.success(f'Backup realizado com sucesso em: {arquivo_backup}')
        except Exception as e:
            st.error(f'Erro ao fazer backup: {e}')

    st.markdown('---')

    st.subheader('Restauração do Banco de Dados')
    arquivo_backup_rest = st.text_input('Nome do arquivo de backup para restauração (.sql)', value=arquivo_backup, key='rest')
    banco_destino_rest = st.text_input('Caminho do banco de dados para restaurar', value=banco_destino, key='rest2')

    if st.button('Restaurar Banco'):
        try:
            restaurar_banco(banco_destino_rest, arquivo_backup_rest)
            st.success(f'Banco restaurado com sucesso a partir de: {arquivo_backup_rest}')
        except Exception as e:
            st.error(f'Erro ao restaurar banco: {e}')

if __name__ == '__main__':
    app_backup_restore()
