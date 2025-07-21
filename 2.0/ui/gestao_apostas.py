import streamlit as st
import pandas as pd

from db.db_utils import get_usuarios_df, get_provas_df, get_apostas_df, get_pilotos_df, db_connect
from services.bets_service import gerar_aposta_automatica, salvar_aposta

def main():
    st.title("🗂️ Gestão de Apostas dos Participantes")

    perfil = st.session_state.get("user_role", "participante")
    if perfil not in ("admin", "master"):
        st.warning("Acesso restrito a administradores.")
        return

    usuarios_df = get_usuarios_df()
    provas_df = get_provas_df()
    pilotos_df = get_pilotos_df()
    participantes = usuarios_df[usuarios_df['status'] == "Ativo"].copy()
    provas_df = provas_df.sort_values("data")
    apostas_df = get_apostas_df()

    st.markdown("### Apostas dos Participantes")
    aba_participante, aba_prova, aba_lote = st.tabs(["Por Participante", "Por Prova", "Apostas Automáticas em Lote"])

    with aba_participante:
        st.subheader("Gerenciar Apostas de um Participante")
        part_nome = st.selectbox("Selecione o participante", participantes["nome"].tolist(), key="part_nome")
        part_row = participantes[participantes["nome"] == part_nome].iloc[0]
        part_id = part_row["id"]
        apostas_part = apostas_df[apostas_df["usuario_id"] == part_id]

        for idx, prova in enumerate(provas_df.itertuples()):
            st.markdown(f"#### {prova.nome} ({prova.data} {prova.horario_prova})")
            aposta = apostas_part[apostas_part["prova_id"] == prova.id]
            if not aposta.empty:
                aposta = aposta.iloc[0]
                st.success(
                    f"**Pilotos:** {aposta['pilotos']} \n"
                    f"**Fichas:** {aposta['fichas']} \n"
                    f"**11º:** {aposta['piloto_11']} \n"
                    f"**Data envio:** {aposta['data_envio']} \n"
                    f"**Automática:** {'Sim' if aposta['automatica'] else 'Não'}"
                )
            else:
                st.warning("Sem aposta registrada.")

            # Chave única robusta:
            if st.button(f"Gerar aposta automática ({prova.nome})", key=f"auto_part_{part_id}_prova_{prova.id}_linha_{idx}"):
                ok, msg = gerar_aposta_automatica(part_id, prova.id, prova.nome, apostas_df, provas_df)
                # Marcar falta na aposta automática:
                conn = db_connect()
                c = conn.cursor()
                c.execute('SELECT faltas FROM usuarios WHERE id=?', (part_id,))
                faltas_atual = c.fetchone()
                faltas_novo = (faltas_atual[0] if faltas_atual and faltas_atual[0] else 0) + 1
                c.execute('UPDATE usuarios SET faltas=? WHERE id=?', (faltas_novo, part_id))
                conn.commit()
                conn.close()
                st.success(msg)
                st.cache_data.clear()
                st.rerun()

    with aba_prova:
        st.subheader("Visualizar/Atribuir Apostas por Prova")
        prova_sel = st.selectbox("Selecione a prova", provas_df["nome"].tolist(), key="prova_sel")
        prova_row = provas_df[provas_df["nome"] == prova_sel].iloc[0]
        prova_id = prova_row["id"]
        apostas_df = get_apostas_df()  # Atualiza apostas após um possível rerun
        apostas_prova = apostas_df[apostas_df["prova_id"] == prova_id]

        for idx, part in enumerate(participantes.itertuples()):
            aposta = apostas_prova[apostas_prova["usuario_id"] == part.id]
            st.markdown(f"##### {part.nome}")
            if not aposta.empty:
                aposta = aposta.iloc[0]
                st.info(
                    f"**Pilotos:** {aposta['pilotos']} \n"
                    f"**Fichas:** {aposta['fichas']} \n"
                    f"**11º:** {aposta['piloto_11']} \n"
                    f"**Data envio:** {aposta['data_envio']} \n"
                    f"**Automática:** {'Sim' if aposta['automatica'] else 'Não'}"
                )
            else:
                st.warning("Sem aposta registrada.")

            # Chave única robusta:
            if st.button(f"Aposta automática ({part.nome})", key=f"auto_prova_{prova_id}_part_{part.id}_linha_{idx}"):
                ok, msg = gerar_aposta_automatica(part.id, prova_id, prova_row["nome"], apostas_df, provas_df)
                # Marcar falta na aposta automática:
                conn = db_connect()
                c = conn.cursor()
                c.execute('SELECT faltas FROM usuarios WHERE id=?', (part.id,))
                faltas_atual = c.fetchone()
                faltas_novo = (faltas_atual[0] if faltas_atual and faltas_atual[0] else 0) + 1
                c.execute('UPDATE usuarios SET faltas=? WHERE id=?', (faltas_novo, part.id))
                conn.commit()
                conn.close()
                st.success(msg)
                st.cache_data.clear()
                st.rerun()

    with aba_lote:
        st.subheader("Gerar apostas automáticas para todos sem aposta em uma prova")
        prova_para_auto = st.selectbox("Escolha uma prova para ação em lote", provas_df["nome"].tolist(), key="prova_lote")
        prova_row_lote = provas_df[provas_df["nome"] == prova_para_auto].iloc[0]
        prova_id_lote = prova_row_lote["id"]
        apostas_df = get_apostas_df()  # Garante atualização dos dados após os reruns
        apostas_prova_lote = apostas_df[apostas_df["prova_id"] == prova_id_lote]
        participantes_sem_aposta = participantes[
            ~participantes["id"].isin(apostas_prova_lote["usuario_id"].tolist())
        ]

        if participantes_sem_aposta.empty:
            st.success("Todos os participantes já têm apostas para esta prova.")
        else:
            if st.button("Gerar apostas automáticas para todos sem aposta", key="auto_lote_btn"):
                for _, part in participantes_sem_aposta.iterrows():
                    ok, msg = gerar_aposta_automatica(part["id"], prova_id_lote, prova_row_lote["nome"], apostas_df, provas_df)
                    # Marcar falta:
                    conn = db_connect()
                    c = conn.cursor()
                    c.execute('SELECT faltas FROM usuarios WHERE id=?', (part["id"],))
                    faltas_atual = c.fetchone()
                    faltas_novo = (faltas_atual[0] if faltas_atual and faltas_atual[0] else 0) + 1
                    c.execute('UPDATE usuarios SET faltas=? WHERE id=?', (faltas_novo, part["id"]))
                    conn.commit()
                    conn.close()
                st.success("Apostas automáticas geradas para todos os participantes sem aposta.")
                st.cache_data.clear()
                st.rerun()

if __name__ == "__main__":
    main()
