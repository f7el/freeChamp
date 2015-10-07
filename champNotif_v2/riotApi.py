__author__ = 'Paul'
from champNotif_v2 import app
import json, requests, time
from database import query_db, get_db
from flask import g

naEndpoint = "na.api.pvp.net"
globalEndpoint = "global.api.pvp.net"
api_key = app.config['API_KEY']
staticDataVer = "v1.2"
champVer = "v1.2"
lolStaticData = "/api/lol/static-data/na/" + staticDataVer + "/champion?api_key=" + api_key
champion = "/api/lol/na/" + champVer + "/champion?api_key=" + api_key

#has key
def getDataDict():
    url = "https://" + globalEndpoint + lolStaticData
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
        champList.append(getChampById(str(dict['id'])))
    return champList

#get the latest image repo version in order to render the latest champ images
def getDragonVer():
    url = "https://" + globalEndpoint + "/api/lol/static-data/na/v1.2/versions?api_key=" + api_key
    response = requests.get(url)
    jObj = response.json()
    return jObj[0]




def main():
    data = getDragonVer()
    print data
if __name__ == "__main__":

    main()