__author__ = 'Paul'
from champNotif_v2 import app
import json
import requests

naEndpoint = "na.api.pvp.net"
api_key = app.config['API_KEY']
staticDataVer = "v1.2"
champApi = "api/lol/NA/" + staticDataVer + "/champion"

# def dictToList(champDict):
#     "turn a dict of champs to a list of champs"
#     champList = []
#     for champ in champDict:
#         if champ == "MonkeyKing":
#             champ = "Wukong"
#
#     champList.append(champ)
#     return champList

#gets a dict of champion lists
def getChampionsDict():
    champApiUrl = "https://" + naEndpoint + "/" + champApi + "?api_key=" + api_key
    r = requests.get(champApiUrl)
    jObj = r.json()
    return jObj['champions']

def getChampById(id):
    response = requests.get("https://global.api.pvp.net/api/lol/static-data/na/" + staticDataVer +"/champion/" + id + "?api_key=" + api_key)
    dict = response.json()
    return dict['name']

def main():
    return None



if __name__ == '__main__':
    main()