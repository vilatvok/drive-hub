import json
import jwt
import networkx as nx

from datetime import datetime, timedelta

from django.conf import settings
from django.core.mail import send_mail

from geopy.distance import geodesic


with open('staticfiles/json/cities.json', 'r') as f:
    cities = json.load(f)


def get_cities():
    return [i['city'] for i in cities]


def generate_routes(cities):
    """Generate routes between cities with similar coordinates."""
    routes = nx.Graph()
    for city in cities:
        routes.add_node(city['city'])

        # get city coordinates
        from_city_lon = float(city['lng'])
        from_city_coords = (float(city['lat']), from_city_lon)

        for other in cities:
            to_city_lon = float(other['lng'])
            to_city_coords = (float(other['lat']), to_city_lon)
            if int(from_city_lon) > int(to_city_lon):
                similar = int(from_city_lon) - int(to_city_lon)
                if similar < 2:
                    distance = geodesic(from_city_coords, to_city_coords).km + 10
                    routes.add_edge(
                        city['city'],
                        other['city'],
                        weight=round(distance, 2),
                    )
            else:
                similar = int(to_city_lon) - int(from_city_lon)
                if similar < 2:
                    distance = geodesic(from_city_coords, to_city_coords).km + 10
                    routes.add_edge(
                        city['city'],
                        other['city'],
                        weight=round(distance, 2),
                    )
    return routes


def create_register_token(time=5, **kwargs):
    """Token for registration. Time limit by default 5 minutes."""
    exp_time = int((datetime.utcnow() + timedelta(minutes=time)).timestamp())
    token = {'exp': exp_time}
    token.update(kwargs)
    token = jwt.encode(
        payload=token,
        key=settings.SECRET_KEY,
    )
    return token


def get_register_token(token):
    token = jwt.decode(
        jwt=token,
        key=settings.SECRET_KEY,
        algorithms='HS256',
    )
    return token


def create_routes(from_city, to_city):
    """Create the shortest way between two cities."""
    routes = generate_routes(cities)
    way_to_city = nx.shortest_path(
        G=routes,
        source=from_city,
        target=to_city,
        weight='weight',
    )
    distance_in_km = nx.shortest_path_length(
        G=routes,
        source=from_city,
        target=to_city,
        weight='weight',
    )
    return way_to_city, round(distance_in_km, 2)


def send_token_email(url, email):
    """Send one time link with token to email adress."""
    return send_mail(
        subject='Verification',
        message=url,
        from_email='kvydyk@gmail.com',
        recipient_list=[email],
    )
