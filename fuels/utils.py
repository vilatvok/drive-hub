import json


with open('staticfiles/json/wog_stations.json', 'r', encoding='utf-8') as f:
    wog = json.load(f)


with open('staticfiles/json/okko_stations.json', 'r', encoding='utf-8') as f:
    okk = json.load(f)
    okko = [s['attributes'] for s in okk]


with open('staticfiles/json/ukrnafta_stations.json', 'r', encoding='utf-8') as f:
    ukr = json.load(f)


with open('staticfiles/json/anp_stations.json', 'r', encoding='utf-8') as f:
    anp = json.load(f)


with open('staticfiles/json/prices.json', 'r', encoding='utf-8') as f:
    prices = json.load(f)
