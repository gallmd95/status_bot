#!/usr/bin/env python3
"""
Microsoft Teams Bot API
"""
import urllib
import os
import json
import requests
import threading
from bottle import Bottle, request, run


app = Bottle()

BOT_TOKEN = ""
BOT_NAME = 'status_bot'
BOT_ID = os.environ["BOT_ID"]
BOT_PASS = os.environ["BOT_PASS"]


coms = {}
coms

def bot_auth():
    try:
        threading.Timer(3000.0, bot_auth).start()
        data = "grant_type=client_credentials&client_id="+BOT_ID+"&client_secret="+BOT_PASS+"&scope=https%3A%2F%2Fapi.botframework.com%2F.default"
        headers = {"Host": "login.microsoftonline.com", "Content-Type": "application/x-www-form-urlencoded"}
        url = "https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token"
        response = requests.post(url,data=data, headers=headers)
        BOT_TOKEN = response.json()['access_token']
        print BOT_TOKEN
    except KeyboardInterrupt:
        print "done"
bot_auth()


def respond(replyToId="", text="hi", mentions=[], hook="redacted"):
    payload = {
        "type": "message",
        "from": {
            "id": "12345678",
            "name": "bot's name"
        },
        "conversation": {
            "id": "abcd1234",
            "name": "conversation's name"
        },
    "recipient": {
            "id": "1234abcd",
            "name": "user's name"
        },
        "text": text
    }
    if replyToId != "":
        payload["replyToId"] = replyToId
    
    data =  json.dumps(payload)
    headers = {'content-type': 'application/json'}
    response = requests.post(hook, data=data, headers = headers )
    print response

@app.post('/vqa')
def get_vqa():
    json_data = request.json
    text = json_data["text"]
    print text.split(" ")
    inputs = []
    for each in text.split(" "):
        if "bot_vqa" not in each:
            inputs.append(str(each))
    lane = -1
    url = ""
    params = {}
    print inputs
    if len(inputs) > 0:
        lane = inputs[0]
        params["token"] = "39ydz43wys"
        params["host"] = "dtord03qax"+lane+"d.dc.dotomi.net"
        url = "http://dtord03dvo11d.dc.dotomi.net:8080/job/Build%20Lane%20And%20Run%20Regression/buildWithParameters?"
    if len(inputs) > 1:
        params["jira_ticket"] = "ESGE-"+inputs[1]
    if len(inputs[2:]) > 1 and len(inputs[2:]) % 2 == 0:
        temp = ""
        for i in range(0, len(inputs[2:]), 2):
            if temp != "":
                temp = temp + "," + " "
            temp = temp + '{}: "{}"'.format(inputs[2:][i], inputs[2:][i+1])
        print temp
        params["Overrides"] = temp
    if url != "":
        requests.get(url + urllib.urlencode(params))
        print url + urllib.urlencode(params)

@app.post('/api/messages')
def get_status():
    json_data = request.json
    print json_data
    url = json_data["serviceUrl"] if "serviceUrl" in json_data else None
    conv_id = json_data["conversation"]["id"] if "conversation" in json_data and "id" in json_data["conversation"] else None
    conv_name = json_data["conversation"]["name"] if "conversation" in json_data and "name" in json_data["conversation"] else None
    recipient_id = json_data["from"]["id"] if "from" in json_data and "id" in json_data["from"] else None
    recipient_name = json_data["from"]["name"] if "from" in json_data and "name" in json_data["from"] else None
    reply_id = json_data["id"] if "id" in json_data else None
    payload = {
        "type": "message",
        "from": {
            "id": "12345678",
            "name": "status_bot"
        },
        "conversation": {
            "id": conv_id,
            #"name": conv_name
        },
    "recipient": {
            "id": recipient_id,
            "name": recipient_name
        },
        "text": "I have several times available on Saturday!",
        "replyToId": reply_id
    }
    print json_data
    headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + BOT_TOKEN}
    print url+"v3/conversations/"+conv_id+"/activities/"+reply_id, json.dumps(payload), headers
    response = requests.post(url+"v3/conversations/"+conv_id+"/activities/"+reply_id, data=json.dumps(payload), headers=headers)  
    print response
    #respond(replyToId=reply_id, text="Your regression is ready")

@app.get('/api/auth')
def get_auth():
    data = "grant_type=client_credentials&client_id="+BOT_ID+"&client_secret="+BOT_PASS+"&scope=https%3A%2F%2Fapi.botframework.com%2F.default"
    headers = {"Host": "login.microsoftonline.com", "Content-Type": "application/x-www-form-urlencoded"}
    url = "https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token"
    response = requests.post(url,data=data, headers=headers)
    BOT_TOKEN = response.json()['access_token']
    print BOT_TOKEN

def main():
    #url = "redacted"
    #response = requests.post(url)
    run(app,host='localhost', port=8081)

if __name__ == "__main__":
    main()