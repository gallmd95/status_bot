#!/usr/bin/env python3
"""
Microsoft Teams Bot API
"""
import urllib
import os
import json
import threading
import datetime
import string
import re
from tinydb import TinyDB, Query
from bs4 import BeautifulSoup
import requests
from bottle import Bottle, request, run, static_file

class Member(object):
    def __init__(self, name, nickname, member_id, email, conversation_id=None):
        self.name = name
        self.nickname = nickname
        self.member_id = member_id
        self.email = email
        self.conversation_id = conversation_id
        self.groups = {}
        self.status = {}    
    def start_convo(self):
        global bot_state
        headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + bot_state.bot_token}
        payload = {
            "bot": {
                "id": bot_state.bot_id,
                "name": bot_state.bot_name
            },
            "members": [
                {
                    "id": self.member_id
                }
            ],
            "channelData": {
                "tenant": {
                    "id": bot_state.tenant_id
                }
            }
        }
        url = bot_state.service_url + "v3/conversations/"
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        json_data = response.json()
        self.conversation_id = json_data["id"]
        print self.conversation_id

    def send_message(self, text="hi"):
        global bot_state
        headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + bot_state.bot_token}
        payload = {
            "type" : "message",
            "text" : text
        }
        url = bot_state.service_url + "v3/conversations/"+self.conversation_id+"/activities"
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        print response

class BotState(object):
    def __init__(self):
        self.bot_token = ""
        self.bot_name = "status_bot"
        self.bot_id = os.environ["BOT_ID"]
        self.bot_pass = os.environ["BOT_PASS"]
        self.jira_token = os.environ["JIRA_TOKEN"]
        self.service_url = os.environ["SERVICE_URL"]
        self.tenant_id = os.environ["TENANT_ID"]
        self.team_id = os.environ["TEAM_ID"]
        self.email_ids = []
        self.test_email_ids = [os.environ["MY_EMAIL"]]
        self.coms = {
            "_pop": self.api_pop,
            "_joke" : self.api_joke,
            "_rm" : self.api_rm,
            "_ai" : self.api_ai,
            "_time" : self.api_time,
            "_show" : self.api_show,
            "_reset" : self.api_reset
        }
        self.rm = {} 
        self.pop = {} 
        self.statuses = {} 
        self.yeststatuses = {} 
        self.issues = {} 
        self.members = {}
    def api_pop(self, i, s):
        self.pop["pops"].append(s)
        print self.pop
    def api_joke(self, i, s):
        self.pop["jokes"].append(s)
        print self.pop
    def api_rm(self, i, s):
        when = s.split(" . ")[0]
        what = s.split(" . ")[1]
        if when in self.rm.keys():
            self.rm[when].append(what)
        else:
            self.rm[when] = [what]
        print self.rm
    def api_ai(self, i, s):
        who = s.split(" . ")[0]
        what = s.split(" . ")[1]
        if who in self.issues.keys():
            self.issues[who].append(what)
        else:
            self.issues[who] = [what]
        print self.issues
    def api_time(self, i, s):
        print s
        s_split = s.split(" ")
        print s_split
        nick = s_split[0]
        print nick
        member_id = -1
        for key in bot_state.members.keys():
            temp = bot_state.members[key].nickname.split(" ")[0]
            print temp, nick
            if temp == nick:
                member_id = bot_state.members[key].member_id
        time = s_split[1]
        self.statuses[str(member_id)]["time"] = time 
        print self.statuses
    def api_show(self, i, s):
        x = bot_state.members[i]
        x.send_message(",".join(self.statuses[i]["status"]))
    def api_reset(self, i, s):
        self.statuses[i]["status"] = []
    def api_status(self, i, s):
        spl = s.split(" . ")
        if len(spl) > 1:
            for each in spl:
                if i in self.statuses.keys():
                    self.statuses[i]["status"].append(each)
                else:
                    self.statuses[i] = {}
                    self.statuses[i]["status"] = [each]
                    self.statuses[i]["time"] = "-1"
        elif i in self.statuses.keys():
            self.statuses[i]["status"].append(s)
        else:
            self.statuses[i] = {}
            self.statuses[i]["status"] = [s]
            self.statuses[i]["time"] = "-1"
    def get_members(self):
        url = os.environ["CONVO_LINK"]+self.team_id+"/members"
        headers = {'Authorization': 'Bearer ' + self.bot_token}
        response = requests.get(url, headers=headers)
        json_data = response.json() if response.status_code == 200 else []
        for each in json_data:
            temp = Member(each["name"], each["givenName"], each["id"], each["email"])
            if temp.member_id == os.environ["MY_ID"]:
                temp.start_convo()
            self.members[temp.member_id] = temp
    def do_auth(self):
        try:
            threading.Timer(3000.0, self.bot_auth).start()
        except KeyboardInterrupt:
            print "Exiting application"
    def bot_auth(self):
        data = "grant_type=client_credentials&client_id="+self.bot_id+"&client_secret="+self.bot_pass+"&scope=https%3A%2F%2Fapi.botframework.com%2F.default"
        headers = {"Host": "login.microsoftonline.com",
                   "Content-Type": "application/x-www-form-urlencoded"}
        url = os.environ["BOT_AUTH_LINK"]
        response = requests.post(url, data=data, headers=headers)
        self.bot_token = response.json()['access_token']
        print self.bot_token
    def send_email(self):
        url, body =  self.setup_email(self.test_email_ids)
        headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + bot_state.bot_token}
        payload = {
            "bot": {
                "id": bot_state.bot_id
            },
            "type": "message",
            "locale": "en-Us",
            "channelID":"email",
            "from": { "id":os.environ["MY_WORK_EMAIL"], "name":bot_state.bot_name},
            "channelData":{
                "htmlBody" : body,
                "subject":"ASAPI Scrum Update "+str(datetime.date.today()),
            }
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        print response
    def setup_email(self,emails):
        headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + bot_state.bot_token}
        payload = {
            "bot": {
                "id": bot_state.bot_id,
                "name": bot_state.bot_name
            },
            "members": [],
            "channelData": {
                "tenant": {
                "id": bot_state.tenant_id
                }
            }
        }  
        for each in emails:
            payload["members"].append({"id" : each})
        url = os.environ["CONVO_EMAIL_LINK"]
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        json_data = response.json()
        body = get_page()
        return os.environ["CONVO_EMAIL_LINK"]+json_data["id"]+"/activities", body

def get_links_status(s):
    for each in s.split(" "):
        temp = each.replace(":", "")
        if "ESGE-" in temp:
            s = s.replace(temp, "<a href='https://jira.cnvrmedia.net/browse/"+temp+"'>"+temp+"</a>")
        if "PI-" in temp:
            s = s.replace(temp, "<a href='https://jira.cnvrmedia.net/browse/"+temp+"'>"+temp+"</a>")
    return s

def get_links_ai(s):
    for each in s.split(" "):
        temp = each.replace(":", "")
        if "ESGE-" in temp:
            s = s.replace(temp, "<a href='https://jira.cnvrmedia.net/browse/"+temp+"'>"+temp+"</a>")
        if "PI-" in temp:
            link = "https://jira.cnvrmedia.net/browse/"+temp
            headers = {"Authorization" : "Basic "+bot_state.jira_token}
            response = requests.get(link, headers=headers)
            contents = response.content.split("\n")
            priority = -1
            status = -1
            for i,each in enumerate(contents):
                if "priority-val" in each:
                    priorityInd = i + 1
                if "status-val" in each:
                    statusInd = i + 1
            priorStr = contents[priorityInd]
            statStr = contents[statusInd]
            k = priorStr.rfind("> ")
            priorStr = priorStr[k+2:]
            k = statStr.rfind("</span>")
            statStr = statStr[:k]
            soup = BeautifulSoup(statStr, "html.parser")
            statStr = soup.span.contents[0]
            s = s.replace(temp, "<a href='"+link+"'>"+temp+"</a> ("+priorStr+") "+statStr)
    return s      

def get_page():
    with open("index.html", "r") as f:
        contents = f.read()
        rep = []
        popHtmlFn = lambda x : "<div id='this_is_the_pop' style='text-align:left;font-family:Helvetica,Arial,sans-serif;font-size:15px;margin-bottom:0;color:#5F5F5F;line-height:135%;'>"+x+"</div>"
        popStr = ""
        for each in bot_state.pop["pops"]:
            popStr = popStr + popHtmlFn("- POP: "+each)
        for each in bot_state.pop["jokes"]:
            popStr = popStr + popHtmlFn("- "+each)
        rep.append(popStr)

        rmHtmlTitleFn = lambda x : "<h3 id='this_is_the_rm'style='color:#000;line-height:125%;font-family:Helvetica,Arial,sans-serif;font-size:20px;font-weight:normal;margin-top:0;margin-bottom:3px;text-align:left;'>"+x+"</h3>"
        rmHtmlBodyFn = lambda x : "<div id='this_is_the_rm' style='text-align:left;font-family:Helvetica,Arial,sans-serif;font-size:15px;margin-bottom:0;color:#5F5F5F;line-height:135%;'>"+x+"</div>"
        rmStr = ""
        for key in bot_state.rm.keys():
            rmStr = rmStr + rmHtmlTitleFn(key)
            for each in bot_state.rm[key]:
                rmStr = rmStr + rmHtmlBodyFn("- "+each)
        rep.append(rmStr)

        staHtmlLeftTitleFn = lambda x : "<h3 style='color:#5F5F5F;line-height:125%;font-family:Helvetica,Arial,sans-serif;font-size:20px;font-weight:normal;margin-top:0;margin-bottom:3px;text-align:left;'>"+x+"</h3>"
        staHtmlLeftBodyFn = lambda x : "<div style='text-align:left;font-family:Helvetica,Arial,sans-serif;font-size:15px;margin-bottom:0;color:#5F5F5F;line-height:135%;'>"+x+"</div>"
        staStrLeft = "<h3 style='color:#000;line-height:125%;font-family:Helvetica,Arial,sans-serif;font-size:20px;font-weight:normal;margin-top:0;margin-bottom:3px;text-align:left;'>Yesterday</h3>"
        
        staHtmlRightTitleFn = lambda x : "<h3 style='color:#5F5F5F;line-height:125%;font-family:Helvetica,Arial,sans-serif;font-size:20px;font-weight:normal;margin-top:0;margin-bottom:3px;text-align:left;'>"+x+"</h3>"
        staHtmlRightBodyFn = lambda x : "<div style='text-align:left;font-family:Helvetica,Arial,sans-serif;font-size:15px;margin-bottom:0;color:#5F5F5F;line-height:135%;'>"+x+"</div>"
        staStrRight = "<h3 style='color:#000;line-height:125%;font-family:Helvetica,Arial,sans-serif;font-size:20px;font-weight:normal;margin-top:0;margin-bottom:3px;text-align:left;'>Today</h3>"
        staStr = ""
        staHtmlRow = "</td> </tr> </table> </td> <td align='right' valign='middle' class='flexibleContainerBox'> <table class='flexibleContainerBoxNext' border='0' cellpadding='0' cellspacing='0' width='210' style='max-width: 100%;'> <tr> <td align='left' class='textContent'>"
        staHtmlCol = "</td> </tr> </table> </td> </tr> </table> <!-- // CONTENT TABLE --></td> </tr> </table> <!-- // FLEXIBLE CONTAINER --> </td> </tr> </table> <!-- // CENTERING TABLE --> </td> </tr> <!-- // MODULE ROW --> <!-- MODULE ROW // --> <tr> <td align='center' valign='top'> <!-- CENTERING TABLE // --> <table border='0' cellpadding='0' cellspacing='0' width='100%'> <tr> <td align='center' valign='top'> <!-- FLEXIBLE CONTAINER // --> <table border='0' cellpadding='30' cellspacing='0' width='500' class='flexibleContainer'> <tr> <td valign='top' width='500' class='flexibleContainerCell'><!-- CONTENT TABLE // --> <table align='left' border='0' cellpadding='0' cellspacing='0' width='100%'> <tr> <td align='left' valign='top' class='flexibleContainerBox'> <table border='0' cellpadding='0' cellspacing='0' width='210' style='max-width: 100%;'> <tr> <td align='left' class='textContent'> <div id='this_is_the_status_left_col' style='text-align:left;font-family:Helvetica,Arial,sans-serif;font-size:15px;margin-bottom:0;color:#5F5F5F;line-height:135%;'>"
        staHtmlEnd = "</td> </tr> </table> </td> </tr> </table> <!-- // CONTENT TABLE --> </td> </tr> </table> <!-- // FLEXIBLE CONTAINER --> </td> </tr> </table> <!-- // CENTERING TABLE --> </td> </tr> <!-- // MODULE ROW --> <!-- MODULE ROW // --> <tr> <td align='center' valign='top'> <!-- CENTERING TABLE // --> <table border='0' cellpadding='0' cellspacing='0' width='100%'> <tr> <td align='center' valign='top'> <!-- FLEXIBLE CONTAINER // --> <table border='0' cellpadding='30' cellspacing='0' width='500' class='flexibleContainer'> <tr> <td valign='top' width='500' class='flexibleContainerCell'> <!-- CONTENT TABLE // --> <table align='left' border='0' cellpadding='0' cellspacing='0' width='100%'> <tr> <td align='left' valign='top' class='flexibleContainerBox'> <table border='0' cellpadding='0' cellspacing='0' width='210' style='max-width: 100%;'> <tr> <td align='left' class='textContent'> <div id='this_is_the_status_left_col' style='text-align:left;font-family:Helvetica,Arial,sans-serif;font-size:15px;margin-bottom:0;color:#5F5F5F;line-height:135%;'></div> </td> </tr> </table> </td> <td align='right' valign='middle' class='flexibleContainerBox'> <table class='flexibleContainerBoxNext' border='0' cellpadding='0' cellspacing='0' width='210' style='max-width: 100%;'> <tr> <td align='left' class='textContent'>"
        for i, key in enumerate(bot_state.statuses.keys()):
            staStrRight = staStrRight + staHtmlRightTitleFn(bot_state.statuses[key]["time"]+" min")
            staStrLeft = staStrLeft + staHtmlLeftTitleFn(bot_state.members[key].nickname)
            for each in bot_state.statuses[key]["status"]:
                staStrRight = staStrRight + staHtmlRightBodyFn("- "+get_links_status(each))
            for each in bot_state.yeststatuses[key]["status"]:
                staStrLeft = staStrLeft + staHtmlLeftBodyFn("- "+get_links_status(each))
            if i+1<len(bot_state.statuses.keys()):
                staStr = staStr + staStrLeft + staHtmlRow +staStrRight +staHtmlCol
                staStrRight = ""
                staStrLeft = ""
        rep.append(staStr+staStrLeft+staHtmlRow+staStrRight+staHtmlEnd)  
        
                
        aiHtmlTitleFn = lambda x : "<h3 style='color:#5F5F5F;line-height:125%;font-family:Helvetica,Arial,sans-serif;font-size:20px;font-weight:normal;margin-top:0;margin-bottom:3px;text-align:left;'>"+x+"</h3>"
        aiHtmlBodyFn = lambda x : "<div style='text-align:left;font-family:Helvetica,Arial,sans-serif;font-size:15px;margin-bottom:0;color:#5F5F5F;line-height:135%;'>"+x+"</div>"
        aiStr = ""

        for key in bot_state.issues.keys():
            aiStr = aiStr + aiHtmlTitleFn(key)
            for each in bot_state.issues[key]:
                aiStr = aiStr + aiHtmlBodyFn(get_links_ai(each))
        rep.append(aiStr)
        
        for each in contents.split("\n"):
            if "this_is_" in each:
                if len(rep) > 0:
                    contents = contents.replace(each,rep[0])
                    rep = rep[1:] if len(rep) > 1 else []
        #with open("temp.html", "wb") as outfile:
        #    outfile.write(contents.strip("\xa0"))
        return contents
def save_botstate():
    date = str(datetime.date.today())
    temp = {"date": date, "pop":bot_state.pop,
            "rm":bot_state.rm, "statuses":bot_state.statuses,
            "issues":bot_state.issues}
    Date = Query()
    db.upsert(temp, Date.date == str(datetime.date.today()))

def prep_botstate():
    save_botstate()
    Date = Query()
    bot_state.yeststatuses = db.get(Date.date == str(datetime.date.today() - datetime.timedelta(1)))
    if bot_state.yeststatuses is None:
        bot_state.yeststatuses = {}
    bot_state.statuses = {}
    for key in bot_state.members.keys():
        if key not in bot_state.yeststatuses.keys():
            bot_state.yeststatuses[key] = {"status":[], "time": "0"}
        bot_state.statuses[key] = {"status":[], "time": "0"}
    bot_state.pop = {"pops":[],"jokes":[]}
    bot_state.rm = {}
    bot_state.issues = {}

app = Bottle()
bot_state = BotState()
bot_state.bot_auth()
bot_state.get_members()
db = TinyDB('db.json')

prep_botstate()

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
    channelId = json_data["channelId"]
    s = json_data["text"]
    com = s.split(" ")[0]
    s_com = s[s.find(com)+len(com)+1:]
    member_id = json_data["from"]["id"]
    print json_data
    if channelId == 'msteams':
        if com in bot_state.coms.keys():
            bot_state.coms[com](member_id, s_com)
        else:
            bot_state.api_status(member_id, s)
    if channelId == 'email':
        print channelId
    if channelId == 'webchat':
        print channelId
    #print json_data
    #if "@" not in json_data["from"]["id"]:
    #    bot_state.members[json_data["from"]["id"]].send_message("Regression has started")
    #bot_state.send_email("hello hello is this thing on?")

@app.get('/api/roster')
def get_roster():
    bot_state.get_members()

@app.get('/api/auth')
def get_auth():
    bot_state.bot_auth()

@app.get('/api/email')
def get_email():
    bot_state.send_email()

@app.get('/api/static')
def get_static():
    return static_file("newindex.html", root=".")

@app.get('/api/prep')
def get_prep():
    prep_botstate()

def main():
    run(app, host='localhost', port=8081)

if __name__ == "__main__":
    main()
