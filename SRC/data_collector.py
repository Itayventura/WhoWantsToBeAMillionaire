# import SRC.db_populator
import requests
import json
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

dbp = DatabasePopulator()

album_ids = set([])
artist_ids = {}


def collect_genres():
    status_code = 500
    params = {'apikey': MUSIXMATCH_API_KEY}
    while status_code == 500:
        response = requests.request("GET", MUSIXMATCH_URL + "/music.genres.get", params=params)
        status_code = response.status_code
        if status_code <= 299:
            json_data = json.loads(response.text)
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
    return ""


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


def add_album_entry(album_id):
    status_code = 500
    if album_id not in album_ids:
        album_ids.add(album_id)
        while status_code == 500:
            params = {'album_id': album_id, 'apikey': MUSIXMATCH_API_KEY}
            response = requests.request("GET", MUSIXMATCH_URL + "/album.get", params=params)
            status_code = response.status_code
            if status_code <= 299:
                json_data = json.loads(response.text)
                if json_data.get('message', {}).get('body', {}).get('album'):
                    album_data = json_data['message']['body']['album']
                    # print(str(album_data))
                    album_name = album_data.get('album_name', '')
                    tracks_count = album_data.get('album_track_count', -1)
                    release_date = parse_date(album_data.get('album_release_date', '0000'))
                    release_type = album_data.get('album_release_type', 'Album')
                    # enter the album entry to the ALBUMS table
                    values = [album_id, album_name, tracks_count, release_date, release_type]
                    print(str(values))
                    dbp.insert_row(ALBUMS, values)

def add_artist_entry(artist_id, artist_name):
    status_code = 500
    artist_data_exists_in_musixbrainz = False
    if not artist_ids.get(artist_id):
        # get artist's mbid
        while status_code == 500:
            params = {'artist_id': artist_id, 'apikey': MUSIXMATCH_API_KEY}
            response = requests.request("GET", MUSIXMATCH_URL + "/artist.get", params=params)
            status_code = response.status_code
            if status_code <= 299:
                json_data = json.loads(response.text)
                if json_data.get('message', {}).get('body', {}).get('artist', {}):
                    artist_data = json_data['message']['body']['artist']
                    if artist_data.get('artist_mbid'):
                        artist_mbid = artist_data['artist_mbid']
                        # enter the artist entry to the ARTISTS table
                        status_code = 500
                        while status_code == 500:
                            params = {'query': f'arid:{artist_mbid}'}
                            response = requests.request("GET", MUSICBRAINZ_URL + "/artist", params=params)
                            status_code = response.status_code
                            if status_code <= 299:
                                musicbrainz_data = json.loads(response.text)
                                if musicbrainz_data['count'] == 1:
                                    # print("artist_data_exists_in_musixbrainz")
                                    artist_data_exists_in_musixbrainz = True
                                    artist_ids[artist_id] = artist_mbid

                                    artist_data = musicbrainz_data['artists'][0]
                                    artist_name = artist_data.get('name', '')
                                    artist_type = artist_data.get('type', '')
                                    artist_rating = artist_data.get('score', -1)
                                    artist_country = artist_data.get('area', {}).get('name', '')
                                    birth = parse_date(artist_data.get('life-span', {}).get('begin'))
                                    death = parse_date(artist_data.get('life-span', {}).get('end'))
                                    values = [artist_id, artist_name, artist_type, artist_rating,
                                              artist_country, birth, death]
                                    print(str(values))
                                    dbp.insert_row(ARTISTS, values)
    if not artist_data_exists_in_musixbrainz:
        artist_ids[artist_id] = -1
        values = [artist_id, artist_name, 'Other', -1, '', '0000-01-01', '0000-01-01']
        print(str(values))
        dbp.insert_row(ARTISTS, values)


def get_top_tracks(page, page_size, chart_name):
    status_code = 500
    params = {
        'apikey': MUSIXMATCH_API_KEY,
        'page': page, 'page_size': page_size, 'chart_name': chart_name
    }
    while status_code == 500:
        response = requests.request("GET", MUSIXMATCH_URL + "/chart.tracks.get", params=params)
        status_code = response.status_code
        if status_code <= 299:
            json_data = json.loads(response.text)
            track_list = json_data['message']['body']['track_list']

            for track_id, track in enumerate(track_list, 1 + (page - 1) * page_size):
                track = track['track']

                artist_id = track['artist_id']
                artist_name = track['artist_name']
                add_artist_entry(artist_id, artist_name)

                album_id = track['album_id']
                add_album_entry(album_id)

                track_name = track['track_name']
                track_rating = track['track_rating']
                # album_name = str(track['album_name'])
                artist_name = track['artist_name']
                track_lyrics = get_track_lyrics(track_name, artist_name)

                values = [track_id, track_name, track_rating, artist_id, album_id, track_lyrics]
                print(str(values))
                dbp.insert_row(TRACKS, values)

                print(str([track_id, artist_id]))
                dbp.insert_row(ARTIST_TRACKS, [track_id, artist_id])

                print(str([track_id, album_id]))
                dbp.insert_row(ALBUM_TRACKS, [track_id, album_id])

                track_genre_list = track['primary_genres']['music_genre_list']
                for elem in track_genre_list:
                    genre_id = elem['music_genre']['music_genre_id']
                    values = [track_id, genre_id]
                    print(str(values))
                    dbp.insert_row(TRACKS_GENRES, values)

# collect_genres()

for i in range(1, 5):
    get_top_tracks(page=i, page_size=3, chart_name="hot")
print("success")
