import dbinfo
import requests
import json
import requests
from requests.auth import HTTPBasicAuth


r = requests.get(dbinfo.STATIONS_URI, params={"apiKey": dbinfo.JCKEY,"contract": dbinfo.NAME})
data = json.loads(r.text)
print(json.dumps(data, indent=4))