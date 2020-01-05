# import SRC.db_populator
import requests
import json
from db_populator import DatabasePopulator

BASE_URL = 'https://api.musixmatch.com/ws/1.1/'
API_KEY = 'f1ed26e2ca739a996575ce0465ecc571'

dbp = DatabasePopulator()


def get_track_lyrics(track_id):
    params = {'track_id': track_id, 'apikey': API_KEY}
    response = requests.request("GET", BASE_URL + "track.lyrics.get", params=params)
    json_data = json.loads(response.text)
    return json_data['message']['body']['lyrics']['lyrics_body']


def get_top_tracks(**kwargs):
    kwargs["apikey"] = API_KEY
    response = requests.request("GET", BASE_URL + "chart.tracks.get", params=kwargs)
    json_data = json.loads(response.text)
    track_list = json_data['message']['body']['track_list']
    album_ids = set([])
    artist_ids = set([])
    for track in track_list:
        album_ids.add(track['track']['album_id'])
        artist_ids.add(track['track']['artist_id'])
        track_id = track['track']['track_id']
        track_name = str(track['track']['track_name']).replace('\'', '\\\'')
        album_name = str(track['track']['album_name']).replace('\'', '\\\'')
        artist_name = str(track['track']['artist_name']).replace('\'', '\\\'')
        track_genre_list = track['track']['primary_genres']['music_genre_list']
        track_genre_list_str = (', '.join([entry['music_genre']['music_genre_name'] for entry in track_genre_list]))\
            .replace('\'', '\\\'')

        track_lyrics = str(get_track_lyrics(track_id)).replace('\'', '\\\'')

        dbp.insert_row('test_table',
                       track_name=track_name,
                       album_name=album_name,
                       artist_name=artist_name,
                       track_genre_list=track_genre_list_str,
                       track_lyrics=track_lyrics)
    return album_ids, artist_ids


for i in range(1, 5):
    get_top_tracks(page=str(i), page_size=3, f_has_lyrics="1", chart_name="hot")
print("success")
