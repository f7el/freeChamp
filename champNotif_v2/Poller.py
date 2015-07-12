__author__ = 'Paul'
import requests
import time
import logging
#a class for creating any kind of poller. calls a specified service every X seconds
class Poller:

    def __init__(self, url, seconds):
        self.url = url
        self.seconds = seconds

    def runPoller(self):
        while True:
            response = requests.get(self.url)
            print("response: " + response.text)
            #logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
            time.sleep(self.seconds)


