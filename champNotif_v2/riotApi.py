__author__ = 'Paul'
from champNotif_v2 import app
import requests
api_key = app.config['API_KEY']
champApiVer = "1.2"
champApi = "/api/lol/NA/" + champApiVer + "/champion/"
naEndpoint = "na.api.pvp.net/"
champApiUrl = "https://" + naEndpoint + champApi + "?api_key=" + api_key

def dictToList(self, champDict):
    "turn a dict of champs to a list of champs"
    champList = []
    for champ in champDict:
        if champ == "MonkeyKing":
            champ = "Wukong"

    champList.append(champ)
#global.api.pvp.net
#na.api.pvp.net

def main():
    r = requests.get(champApiUrl)
    print (r)

if __name__ == '__main__':
    main()