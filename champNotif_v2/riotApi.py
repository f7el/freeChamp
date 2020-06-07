__author__ = 'Paul'
from champNotif_v2 import app
import json, requests, time
from .database import query_db, get_db
from flask import g
from .champRotation import ChampRotation

naEndpoint = "https://na1.api.riotgames.com"
ddragonCdn = "http://ddragon.leagueoflegends.com/cdn"
api_key = app.config['API_KEY']
dDragonVer = "10.8.1"
champVer = "v3"
champDataUrl = ddragonCdn + "/" + dDragonVer + "/data/en_US/champion.json"
champRotationApi = "/lol/platform/v3/champion-rotations"
champRotationUrl = naEndpoint + champRotationApi
#champion = "/api/lol/na/" + champVer + "/champion?api_key=" + api_key

#has key
def getDataDict():
    url = champDataUrl
    r = requests.get(url)
    jObj = r.json()
    return jObj['data']

#gets a list of free champs; 
#param: rotation enum: new player or standard rotation
""" def getFreeChampRotation(rotationType): 
    r = requests.get(champRotationUrl)
    jObj = r.json()
    if (rotationType == ChampRotation.NewPlayers):
        return jObj['freeChampionIdsForNewPlayers']
    return jObj['freeChampionIds'] """

def getFreeChampRotations(): 
    headers = {'X-Riot-Token': api_key}
    r = requests.get(champRotationUrl, headers=headers)
    return r.json()

#returns a dictionary with champ id as the key and champion name as the value
def createChampLookupTable():
    champLookup = {}
    champDicts = getDataDict()
    for name, champDict in champDicts.items():
        id = champDict["key"]
        champLookup[id] = name
    return champLookup

#get the latest image repo version in order to render the latest champ images
def getDragonVer():
    url = "https://ddragon.leagueoflegends.com/api/versions.json"
    response = requests.get(url)
    jObj = response.json()
    return jObj[0]

def main():
    data = getDragonVer()
    print(data)
if __name__ == "__main__":

    main()