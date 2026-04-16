import requests
from config import SPOTIFY_API_TOKEN as TOKEN


def fetch_web_api(endpoint, method='GET', params=None):
    url = f'https://api.spotify.com/{endpoint}'
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }

    response = requests.request(method, url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(f"Ошибка: {response.status_code}, {response.text}")

    return response.json()

def search_tracks(query):
    endpoint = 'v1/search'
    params = {
        'q': query,
        'type': 'track',
        'limit': 5
    }
    data = fetch_web_api(endpoint, params=params)
    return data.get('tracks', {}).get('items', [])
