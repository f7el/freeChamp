__author__ = 'Paul'
#takes 2 arguments to call either the rotate or newChamp endpoints
#param One: rotate or param two: newChamp - (case-insensitive)
from sys import argv
from champNotif_v2 import app
import re
from requests import get
import info
def main():
    baseUrl = "http://" + app.config['HOST'] + ":" + str(app.config['PORT'])
    rotationUrl = baseUrl + "/freeChampPoll"
    newChampUrl = baseUrl + "/checkForNewChamps"
    dragonUrl = baseUrl + "/updateDragon"

    #get the command-line arg
    input = argv[1]

    rotatePattern = "^[rR][oO][tT][aA][tT][eE]$"
    newChampPattern = "^[nN][eE][wW][cC][hH][aA][mM][pP]$"
    dragonPattern = "^[dD][rR][aA][gG][oO][nN]$"
    rotateMatch = re.match(rotatePattern, input)
    newChampMatch = re.match(newChampPattern, input)
    dragonMatch = re.match(dragonPattern, input)

    if rotateMatch:
        get(rotationUrl)
    elif newChampMatch:
        get(newChampUrl)
    elif dragonMatch:
        get(dragonUrl)
    else:
        print "invalid parameter"

if __name__ == "__main__":
    main()
