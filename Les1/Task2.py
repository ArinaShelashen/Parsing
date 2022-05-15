import requests
import json
from pprint import pprint
api_key = "NRUSsUCr1EpVe6Ajb9kV05xJlOub2HzHsTzRLqvLY90LDZxt"
url = "https://api.mpds.io/v0/download/facet"
search = {
    "elements": "Ti",
    "classes": "binary, carbide",
    "props": "enthalpy of formation"}
headers = {'Key': api_key}
params = {'q': json.dumps(search),
          'dtype': 2}

response = requests.get(url, params=params, headers=headers)
pprint(response.json())
