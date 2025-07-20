import streamlit as st
import pandas as pd
from db.db_utils import db_connect, get_usuarios_df, get_provas_df, get_apostas_df, get_resultados_df
from services.championship_service import calcular_pontuacao_campeonato

def carregar_classificacao_geral():
    """
    Gera a classificação geral com soma dos pontos de todas as provas e bônus do campeonato.
    """
    usuarios_df = get_usuarios_df()
    provas_df = get_provas_df()
    apostas_df = get_apostas_df()
    resultados_df = get_resultados_df()
    participantes = usuarios_df[usuarios_df['status'] == "Ativo"]
    provas_realizadas = resultados_df['prova_id'].unique().tolist()

    tabela = []
    for _, user in participantes.iterrows():
        total_pontos = 0
        acertos_11 = 0
        apostas_antes = 0
        for prova_id in provas_realizadas:
            aposta = apostas_df[(apostas_df['usuario_id'] == user['id']) & (apostas_df['prova_id'] == prova_id)]
            resultado = resultados_df[resultados_df['prova_id'] == prova_id]
            if not aposta.empty and not resultado.empty:
                # Cálculo do ponto da aposta
                res = eval(resultado.iloc[0]['posicoes'])
                pilotos_ap = aposta.iloc[0]['pilotos'].split(',')
                fichas = list(map(int, aposta.iloc[0]['fichas'].split(',')))
                piloto_11_ap = aposta.iloc[0]['piloto_11']
                automatica = int(aposta.iloc[0].get('automatica', 0))
                tipo = provas_df[provas_df['id'] == prova_id]['tipo'].iloc[0] if 'tipo' in provas_df.columns else 'Normal'
                pontos_f1 = [25,18,15,12,10,8,6,4,2,1]
                pontos_sprint = [8,7,6,5,4,3,2,1]
                n_pos = 10 if tipo == 'Normal' else 8
                pontos_lista = pontos_f1 if tipo == 'Normal' else pontos_sprint
                piloto_para_pos = {v: int(k) for k, v in res.items()}
                pt = 0
                for i, pilot in enumerate(pilotos_ap):
                    f = fichas[i] if i < len(fichas) else 0
                    pos_real = piloto_para_pos.get(pilot, None)
                    if pos_real and 1 <= pos_real <= n_pos:
                        pt += f * pontos_lista[pos_real-1]
                piloto_11_real = res.get(11, "")
                if piloto_11_ap == piloto_11_real:
                    pt += 25
                    acertos_11 += 1
                if automatica >= 2:
                    pt = round(pt * 0.75, 2)
                total_pontos += pt
                data_envio = aposta.iloc[0]['data_envio']
                # Conta apostas feitas antes do prazo final da corrida
                horario_corrida = provas_df[provas_df['id']==prova_id]['horario_prova'].values[0]
                data_corrida = provas_df[provas_df['id']==prova_id]['data'].values[0]
                data_horario_corrida = f"{data_corrida} {horario_corrida}"
                try:
                    if pd.to_datetime(data_envio) <= pd.to_datetime(data_horario_corrida):
                        apostas_antes += 1
                except Exception:
                    pass
        # Pontos do campeonato (bônus)
        pontos_bonus = calcular_pontuacao_campeonato(user['id'])
        total = total_pontos + pontos_bonus
        tabela.append({
            "Participante": user['nome'],
            "Total": total,
            "Pontos Corridas": total_pontos,
            "Bônus Campeonato": pontos_bonus,
            "Apostas Antecipadas": apostas_antes,
            "Acertos 11º": acertos_11,
        })

    df = pd.DataFrame(tabela)
    if df.empty:
        return df
    # Critérios de desempate: Total (desc), Apostas Antecipadas (desc), Acertos 11º (desc), Bônus Campeonato (desc)
    df = df.sort_values(by=["Total", "Apostas Antecipadas", "Acertos 11º", "Bônus Campeonato"], ascending=[False]*4)
    df = df.reset_index(drop=True)
    df.index = df.index + 1
    df.index.name = "Posição"
    return df

def main():
    st.title("🏆 Classificação Geral dos Participantes")
    df = carregar_classificacao_geral()
    if df.empty:
        st.info("Ainda não há dados suficientes cadastrados para gerar a classificação geral.")
        return
    st.dataframe(df, use_container_width=True)
    st.markdown("""
    <small>
    Critérios de desempate:
    1. Total de pontos<br>
    2. Apostas feitas dentro do prazo<br>
    3. Acertos do 11º colocado<br>
    4. Bônus do campeonato (campeão, equipe, vice)
    </small>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
