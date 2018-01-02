import requests
import os
import json
import urllib
from bottle import Bottle, request, run

app = Bottle()

BOT_NAME = 'status_bot'
BOT_ID = os.environ["BOT_ID"]
BOT_PASS = os.environ["BOT_PASS"]
BOT_TOKEN = "Nw/fLtHwVqX/VbValxSDmGDyVoucq92/w1kOBpinWsE="

coms = {}
coms
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

@app.post('/status')
def get_status():
    json_data = request.json
    url = json_data["serviceUrl"]
    conv_id = json_data["conversation"]["id"]
    conv_name = json_data["conversation"]["name"]
    recipient_id = json_data["from"]["id"]
    recipient_name = json_data["from"]["name"]
    reply_id = json_data["id"]
    payload = {
        "type": "message",
        "from": {
            "id": "12345678",
            "name": "status_bot"
        },
        "conversation": {
            "id": conv_id,
            "name": conv_name
        },
    "recipient": {
            "id": recipient_id,
            "name": recipient_name
        },
        "text": "I have several times available on Saturday!",
        "replyToId": reply_id
    }
    print json_data
    #headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + BOT_TOKEN}
    #response = requests.post(url+"/v3/conversations/"+conv_id+"/activities/"+reply_id, data=json.dumps(payload), headers=headers)  
    #print response
    payload = {"text" : "Hi <at>"+recipient_name+"</at>"}
    data =  json.dumps(payload)
    headers = {'content-type': 'application/json'}
    response = requests.post("https://outlook.office.com/webhook/863de451-0599-4542-a351-a51725ca7cb0@28fd52dd-6ab8-402c-b889-57b419ee909a/IncomingWebhook/ba4da87a94454da7b687773f8aad1a24/4e1f4578-ccf8-429a-8d88-3d1aa2a64a50",data=data, headers = headers )
    print response

def main():
    #data = "grant_type=client_credentials&client_id="+BOT_ID+"&client_secret="+BOT_PASS+"&scope=https%3A%2F%2Fapi.botframework.com%2F.default"
    #headers = {"Host": "login.microsoftonline.com", "Content-Type": "application/x-www-form-urlencoded"}
    #url = "https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token"
    #response = requests.post(url,data=data, headers=headers)
    #BOT_TOKEN = response.json()['access_token']
    print BOT_TOKEN
    run(app,host='localhost', port=8081)

if __name__ == "__main__":
    main()