__author__ = 'Paul'
import requests
import time

requests.get("http://127.0.0.1:5001/freeChampPollTest")
while True:

    time.sleep(14400)
    requests.get("http://127.0.0.1:5000/freeChampPoll")