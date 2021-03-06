import telepot
import json
import requests
import time
import urllib
import json
import csv
import pandas as pd
import numpy
import scipy
from ggplot import *
from numpy._distributor_init import NUMPY_MKL
import io
import matplotlib.pyplot as plt
import matplotlib


#BARRICK GOLD CORP, APPLE INC

token = '392920506:AAHPmmPeCuqFSBdqf5cswmN2Ew9oj-ZLUtg'
URL = "https://api.telegram.org/bot{}/".format(token)
TelegramBot = telepot.Bot(token)
chat = 171391200

dict = {}

with open('security-universe_20171014.csv', newline='', encoding='utf-8') as csvfile:
    securityList = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in securityList:
        dict[row[1]] = row[0]


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update=num_updates
    if last_update>0:
        last_update = num_updates - 1
        text = updates["result"][last_update]["message"]["text"]
        chat_id = updates["result"][last_update]["message"]["chat"]["id"]
        update_id = updates["result"][last_update]["update_id"]
    else:
        last_update=0
        text="None"
        chat_id=0
        update_id=0
    return (text, chat_id,update_id)


def send_message(text, chat):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat)
    get_url(url)

# Sends comments with the addition of the six month performance data.

def send_digitPhase1(digit, chat):
    text = " For the stock indicated, the year to date performance is {}. ".format(
        str(digit))
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat)
    get_url(url)


def main():
    stock,chat,update_id = get_last_chat_id_and_text(get_updates())
    update_id=update_id+1
    get_url("https://api.telegram.org/bot{}/getUpdates?offset={}".format(token,update_id))
    initialText = "Please enter the full name of the stock."
    errorText1 = "No performance data available."
    errorText2 = "Please enter a valid stock name."
    holder = "initial"
    while True:
        if (holder,chat,update_id) !=get_last_chat_id_and_text(get_updates()):
            stock, chat,update_id = get_last_chat_id_and_text(get_updates())
            if stock in dict or stock in dict.values():
                if stock in dict:
                    ticker = dict[stock]
                else:
                    ticker = stock
                urlAddress = "https://www.blackrock.com/tools/hackathon/performance?&identifiers=ticker%3{}&graph=resultMap.RETURNS.latestPerf".format(
                    ticker)
                perf_file = urllib.request.urlopen(urlAddress)
                data = json.loads(perf_file.read())
                perf_file.close()
                if data["resultMap"] != {}:
                    digit = data["resultMap"]["RETURNS"][0]["latestPerf"]["yearToDate"]
                    send_digitPhase1(digit, chat)
                    #Graph plotting and saving, and sending.
                    
                    x=[3,6,9]
                    LABELS = ["3 months", "6 months", "9 months"]
                    y=[data["resultMap"]["RETURNS"][0]["latestPerf"]["threeMonth"],data["resultMap"]["RETURNS"][0]["latestPerf"]["sixMonth"],data["resultMap"]["RETURNS"][0]["latestPerf"]["nineMonth"]]
                    fig = plt.figure()
                    ax = fig.add_subplot(111)
                    ax.set_title("Stock Performance")
                    ax.set_xlabel("Period")
                    ax.set_ylabel("Performance")
                    ggGraph=plt.hist(x,3, weights=y,rwidth=0.8)
                    plt.xticks(x, LABELS)
                    ggGraph=plt.savefig('ggGraph.png')
                    bio=open('ggGraph.png','rb')
                    TelegramBot.sendPhoto(chat,bio)
                else:
                    send_message(errorText1, chat)
            else:
                send_message(errorText2, chat)
            time.sleep(0.2)
            holder = stock
            get_url("https://api.telegram.org/bot{}/getUpdates?offset={}".format(token,chat+1))

        else:
            send_message(initialText, chat)
            while True:
                if (holder, chat,update_id) != get_last_chat_id_and_text(get_updates()):
                    break


if __name__ == '__main__':
    main()
