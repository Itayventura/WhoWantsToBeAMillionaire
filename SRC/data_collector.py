# import SRC.db_populator
import requests
import hashlib
import json
import re
from bs4 import BeautifulSoup
from db_populator import DatabasePopulator
from datetime import datetime
from constants import *

dbp = DatabasePopulator()

added_albums = {''}


def str_to_uid(text):
    m = hashlib.md5()
    m.update(str(text).encode('utf-8'))
    return str(int(m.hexdigest(), 16))[0:12]


def http_request(method='GET', url=None, headers=None, params=None):
    status_code = 500
    while status_code == 500:
        response = requests.request(method, url, headers=headers, params=params)
        status_code = response.status_code
        if status_code <= 299:
            return json.loads(response.text)
    return None


def collect_genres():
    params = {'apikey': MUSIXMATCH_API_KEY}
    json_data = http_request(url=MUSIXMATCH_URL + "/music.genres.get", params=params)
    if json_data and json_data.get('message', {}).get('body', {}):
        for entry in json_data.get('message', {}).get('body', {}).get('music_genre_list', []):
            genre_id = entry.get('music_genre', {}).get('music_genre_id')
            genre_name = entry.get('music_genre', {}).get('music_genre_name')
            # print(str((GENRES, [genre_id, genre_name])))
            dbp.insert_row(GENRES, [genre_id, genre_name])


def parse_date(text):
    for fmt in ('%Y', '%Y-%m-%d', '%Y-%m'):
        try:
            return str(datetime.strptime(text, fmt))
        except ValueError:
            pass
    return None


def scrap_song_url(url):
    lyrics = ''
    status_code = 500
    while status_code == 500:
        response = requests.request('GET', url)
        status_code = response.status_code
        if status_code <= 299:
            html = BeautifulSoup(response.text, 'html.parser')
            lyrics = html.find("div", {"class": "lyrics"}).get_text()
    # remove redundant comments in lyrics
    lyrics = re.sub(r'\[.+?\]', '', lyrics)
    lyrics = re.sub(r'\(.+?\)', '', lyrics)
    return lyrics


def get_track_lyrics(track_name, artist_name):
    remote_song_info = None
    headers = {'Authorization': f'Bearer {GENIUS_API_KEY}'}
    params = {'q': f'{track_name} {artist_name}'}
    response = requests.request("GET", GENIUS_URL + "/search", headers=headers, params=params)
    if response.status_code <= 299:
        json_data = json.loads(response.text)
        if not json_data.get('response', {}).get('hits', []):
            return None
        for hit in json_data['response']['hits']:
            if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
                remote_song_info = hit
                break
    if remote_song_info:
        song_url = remote_song_info['result']['url']
        return scrap_song_url(song_url)
    return None


def get_track_movies(track_id, track_name, artist_name):
    response = requests.request("GET", TUNEFIND_URL + f'/artist/{artist_name}')
    if response.status_code <= 299:
        html = BeautifulSoup(response.text, 'html.parser')
        songs = html.find_all('div', {'class': re.compile("^AppearanceRow__songInfoTitle")})
        appearances_list = None
        for song in songs:
            if song.get_text() == track_name:
                appearances_list = song.find_parent("div", {"class": re.compile("^AppearanceRow__container")})
                break
        if appearances_list:
            movie_list = appearances_list.find_all("a", {"href": re.compile("^/movie")})

            movie_name_list = [movie.find("span", {"class": re.compile("^EventLink__eventTitle")}).get_text() for movie in movie_list]

            movie_uid_list = []
            for movie in movie_list:
                movie_unique_str = movie.get_attribute_list('href')[0].replace('/movie/', '')
                movie_uid = str_to_uid(movie_unique_str)
                movie_uid_list.append(movie_uid)

            # print(str(movie_name_list))
            for movie_uid, movie_name in zip(movie_uid_list, movie_name_list):
                # print(str((MOVIES, [movie_uid, movie_name])))
                dbp.insert_row(MOVIES, [movie_uid, movie_name])
                # print(str((MOVIE_TRACKS, [track_id, movie_uid])))
                dbp.insert_row(MOVIE_TRACKS, [track_id, movie_uid])


def get_track_genres(track_data):
    track_genre_list = track_data.get('primary_genres', {}).get('music_genre_list', [])
    for elem in track_genre_list:
        genre_id = elem['music_genre']['music_genre_id']
        values = [track_data['track_id'], genre_id]
        # print(str((TRACKS_GENRES, values)))
        dbp.insert_row(TRACKS_GENRES, values)


def add_track_entry(track_data, album_id, artist_id):
    track_id = track_data.get('track_id', '')
    track_name = track_data.get('track_name', '')
    track_rating = track_data.get('track_rating', -1)
    artist_name = track_data.get('artist_name', '')
    track_lyrics = get_track_lyrics(track_name, artist_name)
    values = [track_id, track_name, track_rating, artist_id, album_id, track_lyrics]
    # print(str((TRACKS, values)))
    dbp.insert_row(TRACKS, values)
    # print(str((ALBUM_TRACKS, [track_id, album_id])))
    dbp.insert_row(ALBUM_TRACKS, [track_id, album_id])
    # print(str((ARTIST_TRACKS, [track_id, artist_id])))
    dbp.insert_row(ARTIST_TRACKS, [track_id, artist_id])
    get_track_movies(track_id, track_name, artist_name)
    get_track_genres(track_data)


def add_album_tracks(album_id, artist_id):
    params = {
        'album_id': album_id,
        'page_size': 100,
        'apikey': MUSIXMATCH_API_KEY
    }
    tracks_response = http_request(url=MUSIXMATCH_URL + "/album.tracks.get", params=params)
    if tracks_response:
        response_body = tracks_response.get('message', {}).get('body', {})
        if response_body and response_body.get('track_list'):
            for track in response_body['track_list']:
                track = track['track']
                if track['track_name'] and track['track_name'].find('[') == -1:
                    add_track_entry(track, album_id, artist_id)


def add_album_entry(album_data, artist_id):
    album_id = album_data.get('album_id', '')
    album_name = album_data.get('album_name', '')
    release_date = parse_date(album_data.get('album_release_date', '0000'))
    added_albums.add(album_name)
    # enter the album entry to the ALBUMS table
    values = [album_id, album_name, release_date]
    # print(str((ALBUMS, values)))
    dbp.insert_row(ALBUMS, values)
    # print(str((ARTIST_ALBUMS, [album_id, artist_id])))
    dbp.insert_row(ARTIST_ALBUMS, [album_id, artist_id])
    add_album_tracks(album_id, artist_id)


def add_artist_entry(artist_data, artist_id):
    artist_name = artist_data.get('name', '')
    artist_type = artist_data.get('type', '')
    artist_rating = artist_data.get('score', -1)
    birth = parse_date(artist_data.get('life-span', {}).get('begin', '0000'))
    death = parse_date(artist_data.get('life-span', {}).get('end', '0000'))
    values = [artist_id, artist_name, artist_type, artist_rating, birth, death]
    # print(str((ARTISTS, values)))
    dbp.insert_row(ARTISTS, values)


def add_all_artist_albums(musixmatch_artist_id):
    params = {
        'artist_id': musixmatch_artist_id,
        'g_album_name': 1,
        'page_size': 100,
        'apikey': MUSIXMATCH_API_KEY
    }
    albums_response = http_request(url=MUSIXMATCH_URL + "/artist.albums.get", params=params)
    if albums_response:
        response_body = albums_response.get('message', {}).get('body', {})
        if response_body and response_body.get('album_list'):
            for album in albums_response['message']['body']['album_list']:
                album = album['album']
                if album.get('album_release_type', 'Album') == 'Album' and album.get('album_name', '') not in added_albums:
                    add_album_entry(album, musixmatch_artist_id)


def get_musixmatch_artist_id(artist):
    params = {
        'q_artist': artist.get('name', ''),
        'apikey': MUSIXMATCH_API_KEY
    }
    musixmatch_artist_response = http_request(url=MUSIXMATCH_URL + "/artist.search", params=params)
    if musixmatch_artist_response:
        response_body = musixmatch_artist_response.get('message', {}).get('body', {})
        if response_body and response_body.get('artist_list'):
            return response_body['artist_list'][0]['artist']['artist_id']
    return None


def get_artists(limit, offset):
    for artist_type in ['person', 'group']:
        for country in ['US', 'UK']:
            params = {
                'query': f'type:\"{artist_type}\" AND country:\"{country}\"',
                'limit': limit,
                'offset': offset,
                'fmt': 'json'
            }
            response = http_request(url=MUSICBRAINZ_URL + "/artist", params=params)
            if response and response['artists']:
                for artist in response['artists']:
                    artist_id = get_musixmatch_artist_id(artist)
                    if artist_id:
                        add_artist_entry(artist, artist_id)
                        add_all_artist_albums(artist_id)


# collect_genres()

for i in range(0, 5000):
    get_artists(limit=50, offset=i*50)
print("success")
