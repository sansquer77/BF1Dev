import streamlit as st
import requests

st.title("Resultados F1 2025 - Top 11 de cada etapa")

url = "https://api.jolpi.ca/ergast/f1/2025/results/"
try:
    data = requests.get(url, timeout=10).json()
    races = data["MRData"]["RaceTable"]["Races"]
    if not races:
        st.warning("Nenhum resultado disponível na API para 2025.")
    else:
        for race in races:
            race_name = race["raceName"]
            results = race["Results"]
            resultado_dict = {}
            for pos in range(1, 12):
                piloto = next((r for r in results if int(r["position"]) == pos), None)
                if piloto:
                    nome = f"{piloto['Driver']['givenName']} {piloto['Driver']['familyName']}"
                    resultado_dict[pos] = nome
            st.markdown(f"**{race_name}**")
            st.code(str(resultado_dict), language="python")
except Exception as e:
    st.error(f"Erro ao acessar a API ou processar os dados: {e}")
