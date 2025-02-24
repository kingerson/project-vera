"""
Creado el 15/6/2022 a las 10:34 a. m.

@author: jacevedo
"""

import twitter_tools_v1 as tt
from searchtweets import ResultStream
from searchtweets import gen_rule_payload as payload_rule
import requests as rs

#%%

args = tt.twitter_premium_args()

#%%
username = 'stodomingonews'
url_base = (
    "https://api.twitter.com/1.1/followers/list.json?"
    "cursor=-1"
    f"&screen_name={username}"
    "&skip_status=false"
    "&include_user_entities=false"
)

auth = (
    f' -H "Authorization: Bearer {args["bearer_token"]}"'
)


result = rs.get(url_base+auth, verify=False)
result.status_code
result.text

#%%

import searchtweets