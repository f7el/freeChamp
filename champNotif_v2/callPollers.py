__author__ = 'Paul'
def main():
    #insantiate all the pollers we need and call those services
    from Poller import Poller
    from champNotif_v2 import app
    import info
    testUrl = "http://" + app.config['HOST'] + ":" + str(app.config['PORT'])
    rotationTestUrl = testUrl + "/freeChampPoll"
    newChampTestUrl = testUrl + "/checkForNewChamps"
    #roationPoller = Poller("https://")
    newChampPoller = Poller(newChampTestUrl, 3600)
    newChampPoller.runPoller()

if __name__ == "__main__":
    main()
