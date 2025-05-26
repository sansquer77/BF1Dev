import requests

url = "https://api.jolpi.ca/ergast/f1/2025/results/"
data = requests.get(url).json()

for race in data["MRData"]["RaceTable"]["Races"]:
    race_name = race["raceName"]
    results = race["Results"]
    resultado_dict = {}
    for pos in range(1, 12):
        piloto = next((r for r in results if int(r["position"]) == pos), None)
        if piloto:
            nome = f"{piloto['Driver']['givenName']} {piloto['Driver']['familyName']}"
            resultado_dict[pos] = nome
    print(f"# {race_name}\n{resultado_dict}\n")
