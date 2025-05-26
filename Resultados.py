import streamlit as st
import requests

st.title("Resultados F1 2025 - Top 11 de cada etapa (todas as etapas disponíveis na API)")

url_base = "https://api.jolpi.ca/ergast/f1/2025/results/"
limit = 30
offset = 0
todas_as_races = []

try:
    # Primeiro request para descobrir o total
    url = f"{url_base}?offset={offset}"
    resposta = requests.get(url, timeout=10).json()
    total = int(resposta["MRData"]["total"])
    # Adiciona as primeiras races
    todas_as_races.extend(resposta["MRData"]["RaceTable"]["Races"])
    offset += limit

    # Continua buscando até trazer todas as races
    while offset < total:
        url = f"{url_base}?offset={offset}"
        resposta = requests.get(url, timeout=10).json()
        races = resposta["MRData"]["RaceTable"]["Races"]
        if not races:
            break
        todas_as_races.extend(races)
        offset += limit

    if not todas_as_races:
        st.warning("Nenhum resultado disponível na API para 2025.")
    else:
        for race in todas_as_races:
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
