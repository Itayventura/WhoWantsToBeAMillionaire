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


def parse_date(text):
    for fmt in ('%Y', '%Y-%m-%d', '%Y-%m'):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    return None


def scrap_song_url(url):
    page = requests.get(url)
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics = html.find('div', class='lyrics').get_text()

    return lyrics


def get_track_lyrics(track_name, artist_name):
    headers = {'Authorization': f'Bearer {GENIUS_API_KEY}'}
    params = {'q': f'{track_name} {artist_name}'}
    response = requests.request("GET", GENIUS_URL + "/search", headers=headers, params=params)
    json_data = json.loads(response.text)
    for hit in json_data['response']['hits']:
        if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
            remote_song_info = hit
            break
    if remote_song_info:
        song_url = remote_song_info['result']['url']
        return scrap_song_url(song_url)
    return None


def add_album_entry(track_id, album_id):
    if album_id not in album_ids:
        album_ids.add(album_id)
        params = {'album_id': album_id, 'apikey': MUSIXMATCH_API_KEY}
        response = requests.request("GET", MUSIXMATCH_URL + "/album.get", params=params)
        json_data = json.loads(response.text)
        album_data = json_data['body']['album']
        album_name = album_data['album_name']
        tracks_count = album_data['album_track_count']
        release_date = parse_date(album_data['album_release_date'])
        release_type = album_data['album_release_type']
        # enter the album entry to the ALBUMS table
        dbp.insert_row(ALBUMS, [album_id, album_name, tracks_count, release_date, release_type])
    # create relation between album and track
    dbp.insert_row(ALBUM_TRACKS, [track_id, album_id])


def add_artist_entry(track_id, artist_id):
    artist_mbid = None
    if not artist_ids.get(artist_id):
        # get artist's mbid
        params = {'artist_id': artist_id, 'apikey': MUSIXMATCH_API_KEY}
        response = requests.request("GET", MUSIXMATCH_URL + "/artist.get", params=params)
        artist_mbid = response['body']['artist']['artist_mbid']
        # enter the artist entry to the ARTISTS table
        if artist_mbid:
            artist_ids[artist_id] = artist_mbid
            params = {'query': f'arid:{artist_mbid}'}
            response = requests.request("GET", MUSICBRAINZ_URL + "/artist", params=params)
            if response['count'] == 1:
                artist_data = response['artists'][0]
                artist_name = artist_data['name']
                artist_type = artist_data['type']
                artist_rating = artist_data['score']
                artist_country = artist_data['area']['name']
                birth = parse_date(artist_data['life-span']['begin'])
                death = parse_date(artist_data['life-span']['end'])
                dbp.insert_row(ARTISTS,
                               [artist_id, artist_name, artist_type, artist_rating, artist_country, birth, death])
        else:
            artist_ids[artist_id] = -1
    if artist_ids[artist_id] != -1:
        dbp.insert_row(ARTIST_TRACKS, [track_id, artist_id])
    return artist_mbid


def get_top_tracks(**kwargs):
    kwargs["apikey"] = MUSIXMATCH_API_KEY
    response = requests.request("GET", MUSIXMATCH_URL + "/chart.tracks.get", params=kwargs)
    json_data = json.loads(response.text)
    track_list = json_data['message']['body']['track_list']

    for track_id, track in enumerate(track_list, 1):
        track = track['track']

        artist_id = track['artist_id']
        artist_mbid = add_artist_entry(track_id, artist_id)
        if not artist_mbid:
            continue

        album_id = track['album_id']
        add_album_entry(track_id, album_id)

        track_name = track['track_name']
        track_rating = track['track_rating']
        # album_name = str(track['album_name'])
        track_genre_list = track['primary_genres']['music_genre_list']
        for elem in track_genre_list:
            genre_id = elem['music_genre']['music_genre_id']
            dbp.insert_row(TRACKS_GENRES, [track_id, genre_id])

        artist_name = track['artist_name']
        track_lyrics = get_track_lyrics(track_name, artist_name)

        values = [track_id, track_name, track_rating, artist_id, album_id, track_lyrics]
        dbp.insert_row(TRACKS, values)


for i in range(1, 5):
    get_top_tracks(page=str(i), page_size=3, f_has_lyrics="1", chart_name="hot")
print("success")
