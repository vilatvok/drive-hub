import json


with open("static/json_files/wog_stations.json", "r", encoding="utf-8") as f:
    wog = json.load(f)


with open("static/json_files/okko_stations.json", "r", encoding="utf-8") as f:
    okk = json.load(f)
    okko = [s["attributes"] for s in okk]


with open("static/json_files/ukrnafta_stations.json", "r", encoding="utf-8") as f:
    ukr = json.load(f)


with open("static/json_files/anp.json", "r", encoding="utf-8") as f:
    anp = json.load(f)


with open("static/json_files/price.json", "r", encoding="utf-8") as f:
    prices = json.load(f)
