import jwt
import datetime

VIDEOSDK_API_KEY = "50ef8d50-d9c0-45d6-abc1-1923b6c96352"
VIDEOSDK_SECRET_KEY = "2787f875870c181def57fe0cf72056e8d90c0399e727c8338a6fcde65e53560b"

expiration_in_seconds = 7200
expiration = datetime.datetime.now() + datetime.timedelta(seconds=expiration_in_seconds)

token = jwt.encode(payload={
	'exp': expiration,
	'apikey': VIDEOSDK_API_KEY,
	'permissions': ['allow_join'], # 'ask_join' || 'allow_mod' 
}, key=VIDEOSDK_SECRET_KEY, algorithm= 'HS256')
print(token)

import requests
url = "https://api.videosdk.live/v2/rooms"
headers = {'Authorization': f'{token}', 'Content-Type': 'application/json'}
response = requests.request("POST", url, headers = headers)
print(response.text)
