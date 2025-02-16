import dbinfo
import requests
import json
from requests.auth import HTTPBasicAuth


r = requests.get(dbinfo.STATIONS_URI, params={"apiKey": dbinfo.JCKEY,"contract": dbinfo.NAME})
data = json.loads(r.text)
with open("jcdecaux_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)

print("Data saved to jcdecaux_data.json")

# print(json.dumps(data, indent=4))