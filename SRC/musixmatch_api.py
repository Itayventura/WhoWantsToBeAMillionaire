# import SRC.db_populator
import requests
import json
from db_populator import DatabasePopulator

BASE_URL = 'https://api.musixmatch.com/ws/1.1/'
API_KEY = 'f1ed26e2ca739a996575ce0465ecc571'

dbp = DatabasePopulator()

def get_track_lyrics(track_id):
    response = requests.request("GET", BASE_URL + "chart.tracks.get", params=kwargs)

def get_top_tracks(**kwargs):
    kwargs["apikey"] = API_KEY
    response = requests.request("GET", BASE_URL + "chart.tracks.get", params=kwargs)
    track_list = response['message']['body']['track_list']
    album_ids = set([])
    artist_ids = set([])
    for track in track_list:
        album_ids.add(track['track']['album_id'])
        artist_ids.add(track['track']['artist_id'])
        track_id = track['track']['track_id']
        track_name = track['track']['track_name']
        album_name = track['track']['album_name']
        artist_name = track['track']['artist_name']
        track_genre_list = track['track']['music_genre_list']
        track_genre_list_str = ','.join([entry['music_genre']['music_genre_name'] for entry in track_genre_list])

        track_lyrics = get_track_lyrics(track_id)

        dbp.insert_row('test_table',
                       track_name=track_name,
                       album_name=album_name,
                       artist_name=artist_name,
                       track_genre_list=track_genre_list_str,
                       track_lyrics=track_lyrics)

    return album_ids, artist_ids

for i in range(4):
    get_top_tracks(page=str(i), page_size=100, f_has_lyrics="1", chart_name="hot")


'''mockValues = ["val1", "val2", "val3"]
dbp = DatabasePopulator()
dbp.sample_population(mockValues)'''

