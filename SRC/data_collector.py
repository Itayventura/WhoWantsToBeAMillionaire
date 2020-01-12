# import SRC.db_populator
import requests
import json
import re
from bs4 import BeautifulSoup
from db_populator import DatabasePopulator
from datetime import datetime

'''entities tables'''
TRACKS = 'Tracks'
ALBUMS = 'Albums'
ARTISTS = 'Artists'
MOVIES = 'Movies'
GENRES = 'Genres'

'''ER tables'''
ALBUM_TRACKS = 'AlbumTracks'
ARTIST_ALBUMS = 'ArtistAlbums'
ARTIST_TRACKS = 'ArtistTracks'
MOVIE_TRACKS = 'MovieTracks'
TRACKS_GENRES = 'TracksGenres'

MUSIXMATCH_URL = 'https://api.musixmatch.com/ws/1.1'
MUSIXMATCH_API_KEY = 'f1ed26e2ca739a996575ce0465ecc571'

MUSICBRAINZ_URL = 'http://musicbrainz.org/ws/2'

GENIUS_URL = 'https://api.genius.com'
GENIUS_API_KEY = 'JcdMNbQcAaiRz00B_YjtDUSCfm-NGAtwfae_WI-KfWvUpf6ZozUhYFlVFpGkE6LP'

TUNEFIND_URL = 'https://www.tunefind.com'

dbp = DatabasePopulator()

album_ids = set([])
artist_ids = set([])


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
    if json_data:
        for entry in json_data['message']['body']['music_genre_list']:
            genre_id = entry['music_genre']['music_genre_id']
            genre_name = entry['music_genre']['music_genre_name']
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


def get_track_movies(track_name, artist_name):
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
            movie_uid_list = [movie.get_attribute_list('href')[0].replace('/movie/', '') for movie in movie_list]
            print(str(movie_name_list))
            for movie_uid, movie_name in zip(movie_uid_list, movie_name_list):
                dbp.insert_row(MOVIES, [movie_uid, movie_name])
            return movie_uid_list
    return None


def add_album_entry(album_id):
    if album_id not in album_ids:
        album_ids.add(album_id)
        params = {'album_id': album_id, 'apikey': MUSIXMATCH_API_KEY}
        json_data = http_request(url=MUSIXMATCH_URL + "/album.get", params=params)
        if json_data and json_data.get('message', {}).get('body', {}).get('album'):
            album_data = json_data['message']['body']['album']
            album_name = album_data.get('album_name', '')
            release_date = parse_date(album_data.get('album_release_date', '0000'))
            release_type = album_data.get('album_release_type', 'Album')
            # enter the album entry to the ALBUMS table
            values = [album_id, album_name, release_date, release_type]
            print(str(values))
            dbp.insert_row(ALBUMS, values)


def add_artist_entry(artist_id):
    if artist_id not in artist_ids:
        artist_ids.add(artist_id)
        params = {'query': f'arid:{artist_id}',
                  'fmt': 'json'}
        musicbrainz_data = http_request(url=MUSICBRAINZ_URL + "/artist", params=params)
        if musicbrainz_data and musicbrainz_data['count'] == 1:
            # print("artist_data_exists_in_musixbrainz")
            artist_data = musicbrainz_data['artists'][0]
            artist_name = artist_data.get('name', '')
            artist_type = artist_data.get('type', '')
            artist_rating = artist_data.get('score', -1)
            artist_country = artist_data.get('area', {}).get('name', '')
            birth = parse_date(artist_data.get('life-span', {}).get('begin', '0000'))
            death = parse_date(artist_data.get('life-span', {}).get('end', '0000'))
            values = [artist_id, artist_name, artist_type, artist_rating,
                      artist_country, birth, death]
            print(str(values))
            dbp.insert_row(ARTISTS, values)


def get_top_tracks(page, page_size, chart_name):
    params = {
        'apikey': MUSIXMATCH_API_KEY,
        'page': page, 'page_size': page_size, 'chart_name': chart_name
    }
    json_data = http_request(url=MUSIXMATCH_URL + "/chart.tracks.get", params=params)
    if json_data:
        track_list = json_data['message']['body']['track_list']
        for track in track_list:
            musix_match_track = track['track']
            track_id = musix_match_track['track_id']
            track_name = musix_match_track['track_name']
            artist_name = musix_match_track['artist_name']

            params = {
                'query': f'\"{track_name}\" AND artist:\"{artist_name}\"',
                'fmt': 'json'
            }
            response = http_request(url=MUSICBRAINZ_URL + "/recording", params=params)
            if response and response['recordings']:
                music_brainz_track = response['recordings'][0]
                artist_id = music_brainz_track.get('artist-credit', [{}])[0].get('artist', {}).get('id')
                add_artist_entry(artist_id)

                album_id = musix_match_track.get('album_id')
                add_album_entry(album_id)

                track_rating = music_brainz_track.get('score', -1)
                track_lyrics = get_track_lyrics(track_name, artist_name)
                track_movies = get_track_movies(track_name, artist_name)

                values = [track_id, track_name, track_rating, artist_id, album_id, track_lyrics]
                print(str(values))
                dbp.insert_row(TRACKS, values)

                print(str([track_id, artist_id]))
                dbp.insert_row(ARTIST_TRACKS, [track_id, artist_id])

                print(str([track_id, album_id]))
                dbp.insert_row(ALBUM_TRACKS, [track_id, album_id])

                if track_movies:
                    for movie_uid in track_movies:
                        dbp.insert_row(MOVIE_TRACKS, [track_id, movie_uid])

                track_genre_list = musix_match_track.get('primary_genres', {}).get('music_genre_list', [])
                for elem in track_genre_list:
                    genre_id = elem['music_genre']['music_genre_id']
                    values = [track_id, genre_id]
                    print(str(values))
                    dbp.insert_row(TRACKS_GENRES, values)


# collect_genres()

for i in range(1, 5):
    get_top_tracks(page=i, page_size=10, chart_name="hot")
print("success")
