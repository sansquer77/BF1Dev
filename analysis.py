import streamlit as st
import pandas as pd
import plotly.express as px
from db_utils import db_connect

def get_apostas_por_piloto():
    conn = db_connect()
    query = '''
    SELECT u.nome AS participante, a.piloto, COUNT(*) AS total_apostas 
    FROM apostas a
    JOIN usuarios u ON a.usuario_id = u.id
    GROUP BY u.nome, a.piloto
    '''
    return pd.read_sql(query, conn)

def get_apostas_11_colocado():
    conn = db_connect()
    query = '''
    SELECT u.nome AS participante, COUNT(*) AS total_apostas 
    FROM apostas a
    JOIN usuarios u ON a.usuario_id = u.id
    WHERE a.posicao = 11
    GROUP BY u.nome
    '''
    return pd.read_sql(query, conn)

def main():
    st.title("Análise Detalhada das Apostas")
    
    # Dados
    apostas_pilotos = get_apostas_por_piloto()
    apostas_11 = get_apostas_11_colocado()
    
    # Tabs para organização
    tab1, tab2, tab3, tab4 = st.tabs([
        "Distribuição por Piloto (Individual)",
        "Apostas no 11º (Individual)",
        "Consolidado Pilotos",
        "Consolidado 11º"
    ])
    
    with tab1:
        st.subheader("Distribuição por Piloto - Individual")
        participantes = apostas_pilotos['participante'].unique()
        for participante in participantes:
            df_filtrado = apostas_pilotos[apostas_pilotos['participante'] == participante]
            fig = px.pie(df_filtrado, names='piloto', values='total_apostas', 
                        title=f"Apostas de {participante}")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Apostas no 11º Colocado - Individual")
        if not apostas_11.empty:
            fig = px.pie(apostas_11, names='participante', values='total_apostas',
                        title="Distribuição de Apostas no 11º Colocado")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhuma aposta no 11º colocado registrada.")
    
    with tab3:
        st.subheader("Consolidado de Apostas por Piloto")
        consolidado_pilotos = apostas_pilotos.groupby('piloto')['total_apostas'].sum().reset_index()
        fig = px.pie(consolidado_pilotos, names='piloto', values='total_apostas',
                    title="Distribuição Geral de Apostas por Piloto")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(consolidado_pilotos, use_container_width=True)
    
    with tab4:
        st.subheader("Consolidado de Apostas no 11º Colocado")
        total_11 = apostas_11['total_apostas'].sum()
        if total_11 > 0:
            fig = px.pie(apostas_11, names='participante', values='total_apostas',
                        title="Total de Apostas no 11º Colocado por Participante")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhuma aposta no 11º colocado registrada.")
