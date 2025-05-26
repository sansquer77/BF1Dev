import streamlit as st
import requests

st.title("Resultados F1 2025 - Top 11 de cada etapa")

url = "https://api.jolpi.ca/ergast/f1/2025/results/"
cal_url = "https://api.jolpi.ca/ergast/f1/2025.json"

try:
    data = requests.get(url, timeout=10).json()
    races_with_results = {race["raceName"]: race for race in data["MRData"]["RaceTable"]["Races"]}

    # Pega o calendário completo
    cal_data = requests.get(cal_url, timeout=10).json()
    all_races = cal_data["MRData"]["RaceTable"]["Races"]

    for race in all_races:
        race_name = race["raceName"]
        if race_name in races_with_results:
            results = races_with_results[race_name]["Results"]
            resultado_dict = {}
            for pos in range(1, 12):
                piloto = next((r for r in results if int(r["position"]) == pos), None)
                if piloto:
                    nome = f"{piloto['Driver']['givenName']} {piloto['Driver']['familyName']}"
                    resultado_dict[pos] = nome
            st.markdown(f"**{race_name}**")
            st.code(str(resultado_dict), language="python")
        else:
            st.markdown(f"**{race_name}**")
            st.info("Sem resultado disponível ainda.")
except Exception as e:
    st.error(f"Erro ao acessar a API ou processar os dados: {e}")
