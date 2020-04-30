__author__ = 'Paul'
from champNotif_v2 import app
import json, requests, time
from .database import query_db, get_db
from flask import g

naEndpoint = "na1.api.riotgames.com"
ddragonCdn = "http://ddragon.leagueoflegends.com/cdn"
api_key = app.config['API_KEY']
dDragonVer = "10.8.1"
champVer = "v3"
champDataUrl = ddragonCdn + "/" + dDragonVer + "/data/en_US/champion.json"
champion = "/api/lol/na/" + champVer + "/champion?api_key=" + api_key

#has key
def getDataDict():
    url = champDataUrl
    r = requests.get(url)
    jObj = r.json()
    return jObj['data']

#has free attribute
def getListOfChampDicts():
    champApiUrl = "https://" + naEndpoint + champion
    r = requests.get(champApiUrl)
    jObj = r.json()
    return jObj['champions']

def getChampInfoById(id):
    champApiUrl = "https://" + naEndpoint + "/api/lol/na/" + champVer + "/champion/" + str(id) + "?api_key=" + api_key
    r = requests.get(champApiUrl)
    return r.json()


#could get 500 response
def getChampById(id):
    response = requests.get("https://" + naEndpoint + "/api/lol/na/" + champVer + "/champion/" + str(id) + "?api_key=" + api_key)
    dict = response.json()
    return dict['name']


def getListOfChamps():
    champList = []
    objOfLists = getListOfChampDicts()
    for dict in objOfLists:
        champList.append(getChampById(str(dict['key'])))
    return champList

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