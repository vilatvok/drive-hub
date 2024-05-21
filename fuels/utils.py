import json


paths = {
    'wog': 'staticfiles/json/wog_stations.json',
    'okko': 'staticfiles/json/okko_stations.json',
    'ukrnafta': 'staticfiles/json/ukrnafta_stations.json',
    'anp': 'staticfiles/json/anp_stations.json',
    'prices': 'staticfiles/json/prices.json',
}


with open(paths['wog'], 'r', encoding='utf-8') as f:
    wog = json.load(f)


with open(paths['okko'], 'r', encoding='utf-8') as f:
    data = json.load(f)
    okko = [s['attributes'] for s in data]


with open(paths['ukrnafta'], 'r', encoding='utf-8') as f:
    ukr = json.load(f)


with open(paths['anp'], 'r', encoding='utf-8') as f:
    anp = json.load(f)


with open(paths['prices'], 'r', encoding='utf-8') as f:
    prices = json.load(f)
