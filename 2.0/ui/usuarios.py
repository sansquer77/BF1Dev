import streamlit as st
from db.db_utils import get_usuarios_df, db_connect
from services.auth_service import hash_password


def main():
    st.title("👥 Gestão de Usuários")

    # Definir permissões necessárias: apenas master pode editar tudo, admin
    # pode ver; participante não acessa
    perfil = st.session_state.get("user_role", "participante")
    if perfil not in ("admin", "master"):
        st.warning("Acesso restrito a administradores.")
        return

    df = get_usuarios_df()
    if df.empty:
        st.info("Nenhum usuário cadastrado.")
        return

    st.markdown("### Usuários Cadastrados")
    with st.expander("Lista Completa de Usuários", expanded=True):
        show_df = df[["id", "nome", "email",
                      "perfil", "status", "faltas"]].copy()
        show_df.columns = ["ID", "Nome", "Email", "Perfil", "Status", "Faltas"]
        st.dataframe(show_df, use_container_width=True)

    st.markdown("### Editar Usuário")

    usuarios = df["nome"].tolist()
    selected = st.selectbox("Selecione um usuário para editar", usuarios)
    user_row = df[df["nome"] == selected].iloc[0]

    # Campos de edição
    novo_nome = st.text_input("Nome", user_row["nome"])
    novo_email = st.text_input("Email", user_row["email"])
    novo_perfil = st.selectbox(
        "Perfil", [
            "participante", "admin", "master"], index=[
            "participante", "admin", "master"].index(
                user_row["perfil"]))
    novo_status = st.selectbox(
        "Status", [
            "Ativo", "Inativo"], index=0 if user_row["status"] == "Ativo" else 1)
    novas_faltas = st.number_input(
        "Faltas", value=int(
            user_row.get(
                "faltas", 0)), min_value=0)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Atualizar usuário"):
            conn = db_connect()
            c = conn.cursor()
            c.execute(
                "UPDATE usuarios SET nome=?, email=?, perfil=?, status=?, faltas=? WHERE id=?",
                (novo_nome, novo_email, novo_perfil, novo_status, novas_faltas, int(user_row["id"]))
            )
            conn.commit()
            conn.close()
            st.success("Usuário atualizado!")
            st.cache_data.clear()
            st.rerun()

    with col2:
        if "alterar_senha" not in st.session_state:
            st.session_state["alterar_senha"] = False

        if st.button("Alterar senha do usuário"):
            st.session_state["alterar_senha"] = True

        if st.session_state["alterar_senha"]:
            nova_senha = st.text_input(
                "Nova senha", type="password", key="senha_reset")
            if st.button("Salvar nova senha"):
                if not nova_senha:
                    st.error("Digite a nova senha.")
                else:
                    nova_hash = hash_password(nova_senha)
                    conn = db_connect()
                    c = conn.cursor()
                    c.execute(
                        "UPDATE usuarios SET senha_hash=? WHERE id=?", (nova_hash, int(
                            user_row["id"])))
                    conn.commit()
                    conn.close()
                    st.success("Senha atualizada com sucesso!")
                    st.session_state["alterar_senha"] = False
                    st.cache_data.clear()
                    st.rerun()
            if st.button("Cancelar alteração de senha"):
                st.session_state["alterar_senha"] = False

    st.markdown("### Excluir usuário")
    if perfil == "master":
        if st.button("Excluir usuário selecionado"):
            if user_row["perfil"] == "master":
                st.error("Não é possível excluir um usuário master.")
            else:
                conn = db_connect()
                c = conn.cursor()
                c.execute("DELETE FROM usuarios WHERE id=?",
                          (int(user_row["id"]),))
                conn.commit()
                conn.close()
                st.success("Usuário excluído com sucesso!")
                st.cache_data.clear()
                st.rerun()

    st.markdown("---")
    st.markdown("### Adicionar Novo Usuário")
    nome_novo = st.text_input("Nome completo", key="novo_nome")
    email_novo = st.text_input("Email", key="novo_email")
    senha_novo = st.text_input("Senha", type="password", key="nova_senha")
    perfil_novo = st.selectbox(
        "Perfil", [
            "participante", "admin", "master"], key="novo_perfil")
    status_novo = st.selectbox(
        "Status", ["Ativo", "Inativo"], key="novo_status")
    faltas_novo = st.number_input(
        "Faltas",
        value=0,
        min_value=0,
        key="novo_faltas")

    if st.button("Adicionar usuário"):
        if not nome_novo or not email_novo or not senha_novo:
            st.error("Preencha todos os campos obrigatórios.")
        else:
            from services.auth_service import cadastrar_usuario
            sucesso = cadastrar_usuario(
                nome_novo,
                email_novo,
                senha_novo,
                perfil=perfil_novo,
                status=status_novo)
            if sucesso:
                # Atualiza as faltas manualmente, se não zero
                if faltas_novo > 0:
                    conn = db_connect()
                    c = conn.cursor()
                    c.execute(
                        "UPDATE usuarios SET faltas=? WHERE email=?", (faltas_novo, email_novo))
                    conn.commit()
                    conn.close()
                st.success("Usuário adicionado com sucesso!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Email já cadastrado.")


if __name__ == "__main__":
    main()
