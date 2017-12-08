import requests
import os
import json
from bottle import Bottle, request, run

app = Bottle()

BOT_NAME = 'status_bot'
BOT_TOKEN = os.environ["BOT_TOKEN"]

@app.post('/status')
def get_status():
    json_data = request.json
    print json_data["text"]
    url = json_data["serviceUrl"]
    payload = {'some': 'data'}
    headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + BOT_TOKEN}
    response = requests.post(url, data=json.dumps(payload), headers=headers)  
    """
    POST https://smba.trafficmanager.net/apis/v3/conversations/abcd1234/activities/bf3cc9a2f5de... 
    {
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
    "text": "I have several times available on Saturday!",
    "replyToId": "bf3cc9a2f5de..."
    }
    """    
def main():
    run(app,host='localhost', port=8081)

if __name__ == "__main__":
    main()