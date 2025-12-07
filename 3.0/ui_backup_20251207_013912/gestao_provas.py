"""
Gestão de Provas - BF1Dev 3.0
Corrigido com context manager para pool de conexões
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from db.db_utils import get_provas_df, db_connect

def main():
    st.title("🏁 Gestão de Provas")
    
    # Verificar permissão
    perfil = st.session_state.get("user_role", "participante")
    if perfil not in ("admin", "master"):
        st.warning("Acesso restrito a administradores.")
        return
    
    # Buscar provas com cache
    df = get_provas_df().sort_values(by="data", ascending=False)
    
    # Seção: Provas Cadastradas
    if df.empty:
        st.info("Nenhuma prova cadastrada.")
    else:
        st.markdown("### 📋 Provas Cadastradas")
        show_df = df[["id", "nome", "data", "status"]].copy()
        show_df.columns = ["ID", "Nome", "Data", "Status"]
        st.dataframe(show_df, use_container_width=True)
    
    # Seção: Editar Prova
    st.markdown("### ✏️ Editar Prova")
    if not df.empty:
        provas = df["nome"].tolist()
        selected = st.selectbox("Selecione uma prova para editar", provas, key="sel_prova_edit")
        prova_row = df[df["nome"] == selected].iloc[0]
        
        novo_nome = st.text_input("Nome da prova", prova_row["nome"], key="edit_nome_prova")
        nova_data = st.date_input("Data da prova", pd.to_datetime(prova_row["data"]).date(), key="edit_data_prova")
        novo_status = st.selectbox(
            "Status", 
            ["Aberta", "Fechada", "Finalizada"],
            index=["Aberta", "Fechada", "Finalizada"].index(prova_row["status"]),
            key="edit_status_prova"
        )
        
        col1, col2 = st.columns(2)
        
        # Botão: Atualizar
        with col1:
            if st.button("🔄 Atualizar prova", key="btn_update_prova"):
                with db_connect() as conn:
                    c = conn.cursor()
                    c.execute(
                        "UPDATE provas SET nome=?, data=?, status=? WHERE id=?",
                        (novo_nome, nova_data, novo_status, int(prova_row["id"]))
                    )
                    conn.commit()
                
                st.success("✅ Prova atualizada com sucesso!")
                st.cache_data.clear()
                st.rerun()
        
        # Botão: Excluir
        with col2:
            if st.button("🗑️ Excluir prova", key="btn_delete_prova"):
                with db_connect() as conn:
                    c = conn.cursor()
                    c.execute("DELETE FROM provas WHERE id=?", (int(prova_row["id"]),))
                    conn.commit()
                
                st.success("✅ Prova excluída com sucesso!")
                st.cache_data.clear()
                st.rerun()
    
    # Divisor
    st.markdown("---")
    
    # Seção: Adicionar Nova Prova
    st.markdown("### ➕ Adicionar Nova Prova")
    
    nome_novo = st.text_input("Nome da nova prova", key="novo_nome_prova")
    data_nova = st.date_input("Data da prova", key="nova_data_prova")
    status_novo = st.selectbox("Status", ["Aberta", "Fechada", "Finalizada"], key="novo_status_prova")
    
    if st.button("➕ Adicionar prova", key="btn_add_prova"):
        if not nome_novo:
            st.error("❌ Preencha o nome da prova.")
        else:
            with db_connect() as conn:
                c = conn.cursor()
                c.execute(
                    '''INSERT INTO provas (nome, data, status)
                       VALUES (?, ?, ?)''',
                    (nome_novo, data_nova, status_novo)
                )
                conn.commit()
            
            st.success("✅ Prova adicionada com sucesso!")
            st.cache_data.clear()
            st.rerun()

if __name__ == "__main__":
    main()
