from riotwatcher import LolWatcher, ApiError
import requests
from datetime import date
import pandas as pd

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# https://www.projectpro.io/recipes/upload-files-to-google-drive-using-python

api_key = 'RGAPI-f90e1c10-d5a1-4eeb-8959-93936a754e3f'
list_jugadores = ["alexgarcy", "ElTitoEscri", "WDNW ŠtîCkS", "RunnanPlays", "Megaibacu", "Marcostiz", "Chιzuru"]
my_region = 'EUW1'
today = date.today().strftime("%d/%m/%Y")
win = -1
lista_datos = []


# Devuelve las últimas 20 partidas, recibe el nombre del invocador
def getHistory(usuario):
    watcher = LolWatcher(api_key)
    user = watcher.summoner.by_name(my_region, usuario)
    puuid = user['puuid']
    history = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid"
                           "/" + puuid + "/ids"
                                         "?start=0&count=20&api_key=" + api_key)
    return history.json()


def getMatchInfo(match_id):
    match = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/" + match_id + "?api_key=" + api_key)
    return match.json()


def getPlayerData(info):
    duration = round(info["info"]["gameDuration"] / 60, 2)
    for i in list_jugadores:
        for j in info["info"]["participants"]:
            if i == j["summonerName"]:
                win = 1 if j["win"] else 0

                # Añadir información para añadir en csv
                data = {"id": info["metadata"]["matchId"],
                        "fecha": today, "lane": j["lane"],
                        "summonerName": j["summonerName"],
                        "championName": j["championName"],
                        "kills": j["kills"],
                        "deaths": j["deaths"],
                        "assists": j["assists"],
                        "KDA": round((j["kills"] + j["assists"]) / j["deaths"], 2),
                        "totalMinionsKilled": j["totalMinionsKilled"],
                        "Minions/Min": round(j["totalMinionsKilled"] / duration, 2),
                        "wardsPlaced": j["wardsPlaced"],
                        "visionWardsBoughtInGame": j["visionWardsBoughtInGame"],
                        "win": win}
                lista_datos.append(data)

    writeInCsv(lista_datos)


def writeInCsv(datos):
    df = pd.DataFrame(datos)
    df.to_csv('prueba.csv', header=False, mode='a', index=False)


historial = getHistory("alexgarcy")
info = getMatchInfo(historial[0])
getPlayerData(info)
