import json
import jwt
import requests
import networkx as nx

from datetime import datetime, timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from geopy.distance import geodesic


with open('staticfiles/json/cities.json', 'r') as f:
    cities = json.load(f)

url = requests.get(f'http://ip-api.com/json/185.204.71.251')

# Serializer choices
cities_ = [url.json()['city']]
cities_2 = [cities_.append(i['city']) for i in cities]


def generate_routes(cities):
    """Generate routes between cities."""
    routes = nx.Graph()
    for city in cities:
        routes.add_node(city['city'])

        # get city coordinates
        long = float(city['lng'])
        city_coord = (float(city['lat']), long)

        # get other cities coordinates and create way between cities with similar coordinates
        # similar coordinates - when difference between coordinates less than 2
        for other in cities:
            long_other = float(other['lng'])
            other_coord = (float(other['lat']), long_other)
            if int(long) > int(long_other):
                check = int(long) - int(long_other)
                if check < 2:
                    routes.add_edge(
                        city['city'],
                        other['city'],
                        weight=round(geodesic(city_coord, other_coord).km + 10, 2),
                    )
            else:
                check = int(long_other) - int(long)
                if check < 2:
                    routes.add_edge(
                        city['city'],
                        other['city'],
                        weight=round(geodesic(city_coord, other_coord).km + 10, 2),
                    )
    return routes


routes = generate_routes(cities)


def create_register_token(time=5, **kwargs):
    """Token for registration. Time limit by default 5 minutes."""
    token = {'exp': int((datetime.utcnow() + timedelta(minutes=time)).timestamp())}
    token.update(kwargs)
    token = jwt.encode(
        token,
        settings.SECRET_KEY,
    )
    return token


def get_register_token(token):
    token = jwt.decode(token, settings.SECRET_KEY, 'HS256')
    return token


def create_routes(my_city, other_city):
    """Create the shortest way between two cities."""
    dist = nx.shortest_path(routes, source=my_city, target=other_city, weight='weight')
    dist_km = round(
        nx.shortest_path_length(
            routes, source=my_city, target=other_city, weight='weight'
        ), 2)
    return dist, dist_km


def send_token_email(url, email):
    """Send one time link with token to email adress."""
    return send_mail(
        'Verification',
        url,
        'kvydyk@gmail.com',
        [email],
    )