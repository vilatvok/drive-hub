import networkx as nx
import json
import jwt

from datetime import datetime, timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from geopy.distance import geodesic


with open("static/json_files/ua.json", "r") as f:
    cities = json.load(f)


cities_ = [(i["city"], i["city"]) for i in cities]

graph = nx.Graph()

# create graph with cities
for city in cities:
    graph.add_node(city["city"])

    # get city coordinates
    long = float(city["lng"])
    city_coord = (float(city["lat"]), long)

    # get other cities coordinates and create way between cities with similar coordinates
    # similar coordinates - when difference between coordinates less than 2
    for other in cities:
        long_other = float(other["lng"])
        other_coord = (float(other["lat"]), long_other)
        if int(long) > int(long_other):
            check = int(long) - int(long_other)
            if check < 2:
                graph.add_edge(
                    city["city"],
                    other["city"],
                    weight=round(geodesic(city_coord, other_coord).km + 10, 2),
                )
        else:
            check = int(long_other) - int(long)
            if check < 2:
                graph.add_edge(
                    city["city"],
                    other["city"],
                    weight=round(geodesic(city_coord, other_coord).km + 10, 2),
                )


def create_register_token(**kwargs):
    token = {"exp": int((datetime.utcnow() + timedelta(minutes=5)).timestamp())}
    token.update(kwargs)
    token = jwt.encode(
        token,
        settings.SECRET_KEY,
    )
    return token


def get_register_token(token):
    t = jwt.decode(token, settings.SECRET_KEY, "HS256")
    return t


# find the shortest way between two cities
def create_roads(my_city, other_city):
    dist = nx.shortest_path(graph, source=my_city, target=other_city, weight="weight")
    dist_km = round(
        nx.shortest_path_length(
            graph, source=my_city, target=other_city, weight="weight"
        ),
        2,
    )
    return dist, dist_km


def send_token_email(url, token, user=None, email=None):
    if user:
        uid = urlsafe_base64_encode(force_bytes(user))
        return send_mail(
            "Verification",
            url + f"{uid}/{token}/",
            "kvydyk@gmail.com",
            [user.email],
        )
    elif email:
        return send_mail(
            "Verification",
            url + f"{token}/",
            "kvydyk@gmail.com",
            [email],
        )


def get_client_ip_address(request):
    req_headers = request.META
    x_forwarded_for_value = req_headers.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for_value:
        ip_addr = x_forwarded_for_value.split(",")[-1].strip()
    else:
        ip_addr = req_headers.get("REMOTE_ADDR")
    return ip_addr
