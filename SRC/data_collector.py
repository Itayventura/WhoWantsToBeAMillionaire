import requests
import hashlib
import json
import re
from bs4 import BeautifulSoup
from database import Database
from datetime import datetime
from constants import *

database = Database()

""" HELPER FUNCTIONS """

def http_request(method='GET', url=None, headers=None, params=None):
    """ This function creates an API request to one of the servers our app uses:
        1. MusixMatch
        2. Musicbrainz
    :param method: (str) The API request method (default: "GET").
    :param url: (str) The API request's URL.
    :param headers: (dict) Optional request headers.
    :param params: (dict) Optional request parameters.
    :return: (dict) The response payload.
    """
    # Sometimes musixmatch API returns status code 500, so we try again until the response is OK.
    status_code = 500
    while status_code == 500:
        response = requests.request(method, url, headers=headers, params=params)
        status_code = response.status_code
        if status_code <= 299:
            return json.loads(response.text)
    return None


def str_to_uid(move_name):
    """ This function generates a unique id for a movie, using hashlib library.
    :param move_name: (str) A movie name string.
    :return: (str) The generated movie ID string.
    """
    m = hashlib.md5()
    m.update(str(move_name).encode('utf-8'))
    return str(int(m.hexdigest(), 16))[0:12]


def parse_date(text):
    """ This function parses a date out of MusixMatch optional date formats.
    :param text: (str) A date of the format '%Y', '%Y-%m-%d' or '%Y-%m'.
    :return: (str) A date of the format '%Y-%m-%d'. If the date is not in one of the above formats, None is returned.
    """
    for fmt in ('%Y', '%Y-%m-%d', '%Y-%m'):
        try:
            return str(datetime.strptime(text, fmt))
        except ValueError:
            pass
    return None


def scrap_song_url(url):
    """ This function fetches a track's lyrics from its Genius HTML web page, using bs4 library.
    :param url: (str) The track's Genius web page.
    :return: (str) The song lyrics.
    """
    lyrics = ''
    status_code = 500
    while status_code == 500:
        response = requests.request('GET', url)
        status_code = response.status_code
        if status_code <= 299:
            html = BeautifulSoup(response.text, 'html.parser')
            lyrics = html.find("div", {"class": "lyrics"}).get_text()
    # remove redundant comments in lyrics (text in parenthesis)
    lyrics = re.sub(r'\[.+?\]|\(.+?\)', '', lyrics)
    return lyrics


def get_track_lyrics(track_name, artist_name):
    """ This function searches for a track's lyrics, using Genius API.
    :param track_name: (str) The track name.
    :param artist_name: (str) The artist name.
    :return: (str) The track lyrics, if exists in Genius (None otherwise).
    """
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


def track_not_in_db(filtered_track_name, track_id, added_tracks):
    """ This function checks if a track has already been inserted into our database.
    :param filtered_track_name: (str) The track name string, filtered to contain letters or digit characters only.
    :param track_id: The track MusixMatch ID.
    :param added_tracks: (dict) All the added tracks of the current artist.
    :return: True iff the track exists in our database.
    """
    if filtered_track_name not in added_tracks.keys():
        added_tracks[filtered_track_name] = track_id
        return True
    return False


def album_not_in_db(album, added_albums):
    """ This function checks if an album has already been inserted into our database.
    :param album: (str) The album name string.
    :param added_albums: (dict) All the added albums of the current artist.
    :return: True iff the album exists in our database.
    """
    album_name = album.get('album_name', '')
    album_name = re.sub(r'\[.+?\]|\(.+?\)|[^a-zA-Z0-9]', '', album_name).lower()
    if album_name not in added_albums:
        added_albums.add(album_name)
        return True
    return False


""" MAIN DATABASE POPULATION FUNCTIONS """

def collect_genres():
    """ This function inserts all the genres from MusixMatch API into our database.
    """
    params = {'apikey': MUSIXMATCH_API_KEY}
    json_data = http_request(url=MUSIXMATCH_URL + "/music.genres.get", params=params)
    if json_data and json_data.get('message', {}).get('body', {}):
        for entry in json_data.get('message', {}).get('body', {}).get('music_genre_list', []):
            genre_id = entry.get('music_genre', {}).get('music_genre_id')
            genre_name = entry.get('music_genre', {}).get('music_genre_name')
            database.insert_row(GENRES, [genre_id, genre_name])


def get_track_movies(track_id, track_name, artist_name):
    """ This function inserts into our database all the movies that `track_name` is played in,
        according to TuneFind website, using bs4 library.
    :param track_id: (int) The track ID.
    :param track_name: (str) The track name.
    :param artist_name: (str) The track artist.
    """
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

            movie_name_list = [movie.find("span", {"class": re.compile("^EventLink__eventTitle")}).get_text()
                               for movie in movie_list]

            movie_uid_list = []
            for movie in movie_list:
                movie_unique_str = movie.get_attribute_list('href')[0].replace('/movie/', '')
                movie_uid = str_to_uid(movie_unique_str)
                movie_uid_list.append(movie_uid)

            for movie_uid, movie_name in zip(movie_uid_list, movie_name_list):
                database.insert_row(MOVIES, [movie_uid, movie_name])
                database.insert_row(MOVIE_TRACKS, [track_id, movie_uid])


def get_track_genres(track_data):
    """ This function inserts into our database a specific track's genres records.
    :param track_data: The track data from MusixMatch API.
    """
    track_genre_list = track_data.get('primary_genres', {}).get('music_genre_list', [])
    for elem in track_genre_list:
        genre_id = elem['music_genre']['music_genre_id']
        values = [track_data['track_id'], genre_id]
        database.insert_row(TRACKS_GENRES, values)


def add_track_entry(track_data, album_id, artist_id, added_tracks):
    """ This function inserts a track record into our database.
    :param track_data: (dict) The track data.
    :param album_id: (int) The track's album ID.
    :param artist_id: (int) The track's artist ID.
    :param added_tracks: (dict) All the added tracks of the current artist.
    """
    track_name = track_data.get('track_name', '')
    track_id = track_data.get('track_id', '')
    filtered_track_name = re.sub(r'\[.+?\]|\(.+?\)|[^a-zA-Z0-9]', '', track_name).lower()
    if track_not_in_db(filtered_track_name, track_id, added_tracks):
        track_rating = track_data.get('track_rating', -1)
        artist_name = track_data.get('artist_name', '')
        track_lyrics = get_track_lyrics(track_name, artist_name)
        values = [track_id, track_name, track_rating, track_lyrics, artist_id]
        database.insert_row(TRACKS, values)
        get_track_movies(track_id, track_name, artist_name)
        get_track_genres(track_data)
    else:
        track_id = added_tracks[filtered_track_name]
    database.insert_row(ALBUM_TRACKS, [track_id, album_id])


def add_album_tracks(album_id, artist_id, added_tracks):
    """ This function inserts the album's tracks into our database.
    :param album_id: (int) The track's album ID.
    :param artist_id: (int) The track's artist ID.
    :param added_tracks: (dict) All the added tracks of the current artist.
    """
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
                if track['track_name']:
                    add_track_entry(track, album_id, artist_id, added_tracks)


def add_album_entry(album_data, artist_id, added_tracks):
    """ This function inserts an album record into our database.
    :param album_data: (dict) The album data.
    :param artist_id: (int) The album's artist ID.
    :param added_tracks: (dict) All the added tracks of the current artist.
    """
    album_id = album_data.get('album_id', '')
    album_name = album_data.get('album_name', '')
    release_date = parse_date(album_data.get('album_release_date', '0000'))
    # enter the album entry to the ALBUMS table
    values = [album_id, album_name, release_date, artist_id]
    database.insert_row(ALBUMS, values)
    add_album_tracks(album_id, artist_id, added_tracks)


def add_artist_entry(artist_data, artist_id):
    """ This function inserts an artist record into our database.
    :param artist_data: (dict) The artist data.
    :param artist_id: (int) The artist ID.
    """
    artist_name = artist_data.get('name', '')
    artist_type = artist_data.get('type', '')
    artist_rating = artist_data.get('score', -1)
    birth = parse_date(artist_data.get('life-span', {}).get('begin', '0000'))
    death = parse_date(artist_data.get('life-span', {}).get('end', '0000'))
    values = [artist_id, artist_name, artist_type, artist_rating, birth, death]
    database.insert_row(ARTISTS, values)


def add_all_artist_albums(musixmatch_artist_id):
    """ This function inserts the artist's albums into our database.
    :param musixmatch_artist_id: (int) The album's MusixMatch artist ID.
    """
    added_tracks = {'': ''}
    added_albums = {''}
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
                if album.get('album_release_type', 'Album') == 'Album' and album_not_in_db(album, added_albums):
                    add_album_entry(album, musixmatch_artist_id, added_tracks)


def get_musixmatch_artist_id(artist):
    """ This function retrieves artists' MusixMatch ID by their names.
    :param artist: (str) Artist's name.
    :return: (int) The artist's MusixMatch ID.
    """
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
    """ This function inserts the artists data into our database (including tracks, genres, albums and movies),
        using a list from Musicbrainz API and the data from MusixMatch API.
    :param limit: (int) Maximum number of artists to retrieve from Musicbrainz.
    :param offset: (int) Offset to start retrieving data from Musicbrainz.
    """
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

for i in range(400, 800):
    get_artists(limit=50, offset=i*50)
print("success")
