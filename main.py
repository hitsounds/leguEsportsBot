import requests
import time
from datetime import datetime

ID_TOKEN = input("Token:")

def getLive():
    url = "https://esports-api.lolesports.com/persisted/gw/getLive"
    querystring = {"hl":"en-GB"}
    headers = {
    'authority': "esports-api.lolesports.com",
    'accept': "application/json",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36",
    'x-api-key': "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z",
    'origin': "https://lolesports.com",
    'sec-fetch-site': "same-site",
    'sec-fetch-mode': "cors",
    'sec-fetch-dest': "empty",
    'referer': "https://lolesports.com/schedule",
    'accept-language': "en-GB,en-UK;q=0.9,en;q=0.8,ja;q=0.7"
  }
    return requests.request("GET", url, headers=headers, params=querystring).json()

def getEvent(id):
    url = "https://esports-api.lolesports.com/persisted/gw/getEventDetails"
    querystring = {"hl":"en-GB","id":id}
    headers = {
    'authority': "esports-api.lolesports.com",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36",
    'x-api-key': "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z",
    'accept': "*/*",
    'origin': "https://lolesports.com",
    'sec-fetch-site': "same-site",
    'sec-fetch-mode': "cors",
    'sec-fetch-dest': "empty",
    'referer': "https://lolesports.com/live/lcs",
    'accept-language': "en-GB,en-UK;q=0.9,en;q=0.8,ja;q=0.7"
  }
    return requests.request("GET", url, headers=headers, params=querystring).json()

def watch(tourny_id, param, provider):
    global ID_TOKEN
    url = "https://rex.rewards.lolesports.com/v1/events/watch"
    payload = {
	"geolocation":{"code":"GB","area":"EU"},
        "stream_id":param,
        "source":provider,
        "stream_position_time": (datetime.now().replace(microsecond=0).isoformat() + "Z"),
        "tournament_id":tourny_id
    }
    headers = {
        'cookie': f"id_token={ID_TOKEN}",
    'authority': "rex.rewards.lolesports.com",
        "content-type": "application/json",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36",
    'accept': "*/*",
    'origin': "https://lolesports.com",
    'sec-fetch-site': "same-site",
    'sec-fetch-mode': "cors",
    'sec-fetch-dest': "empty",
    'referer': "https://lolesports.com/live/",
    'accept-language': "en-GB,en-UK;q=0.9,en;q=0.8,ja;q=0.7"
  }
    return requests.request("POST", url, json=payload, headers=headers)
    
def main():
    event_id = None
    stream = None
    tourny_id = None

    while True:
        #Get live events
        l_t = getLive()["data"]["schedule"]["events"]
        #Sometimes returns None if there are no events rathjer than an empty list
        if l_t is None:
            print(f"[{str(datetime.now())}]"+"None type error")
            event_id = None
            stream = None
            tourny_id = None
            time.sleep(12*60)
            continue
        #sort by priority and then by if a match is on
        l_t.sort(key=lambda x: x["league"]["priority"])
        l_t.sort(key= lambda x: 0 if x["type"] == "match" else 1)
        #get ids and make sure in progress
        live = [i["id"] for i in l_t if i["state"] == "inProgress"]
        #Catch no live events
        if len(live) == 0:
            print(f"[{str(datetime.now())}]"+"No in progress matches to watch")
            event_id = None
            stream = None
            tourny_id = None
            time.sleep(12*60)
            continue
        #More suitable event has started so run this code
        if event_id != live[0]:
            for j in live:
                event_id = None
                stream = None
                tourny_id = None
                event_id_tmp = j
                tmp = getEvent(event_id_tmp)["data"]["event"]
                strems = tmp["streams"]
                if len(strems) == 0:
                    event_id = None
                    stream = None
                    tourny_id = None
                    continue
                else:
                    strems.sort(key=lambda x: 0 if x["provider"] == "twitch" else 1)
                    strems.sort(key=lambda x: 0 if x["locale"][:2] == "en" else 1)
                event_id = event_id_tmp
                stream = strems[0]
                tourny_id = tmp["tournament"]["id"]
                break
            if event_id == None:
                print(f"[{str(datetime.now())}]"+ "No in progress streams to watch")
                time.sleep(12*60)
                continue
        #Log activity
        print(f"[{str(datetime.now())}]"+ f"Watching: {stream['parameter']}:{stream['provider']}")
        code = watch(tourny_id, stream["parameter"], stream["provider"]).status_code
        #Capture error
        if code != 201:
            print("ERROR " + code)
            break
        #<60s to allow code to run and maintain 60s interval
        time.sleep(59.4)

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(e)
            time.sleep(300)
            pass

