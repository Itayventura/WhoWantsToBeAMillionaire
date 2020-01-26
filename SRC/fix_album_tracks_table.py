import requests
import json
import re
from database import Database
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


""" MAIN DATABASE POPULATION FUNCTIONS """


def add_track_entry(track_data, album_id, added_tracks):
    """ This function inserts a track record into our database.
    :param track_data: (dict) The track data.
    :param album_id: (int) The track's album ID.
    :param added_tracks: (dict) All the added tracks of the current artist.
    """
    track_name = track_data.get('track_name', '')
    track_id = track_data.get('track_id', '')
    filtered_track_name = re.sub(r'\[.+?\]|\(.+?\)|[^a-zA-Z0-9]', '', track_name).lower()
    if not track_not_in_db(filtered_track_name, track_id, added_tracks):
        track_id = added_tracks[filtered_track_name]
    database.insert_row(ALBUM_TRACKS, [track_id, album_id])


def add_album_tracks(album_id, added_tracks):
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
                    add_track_entry(track, album_id, added_tracks)


artists = database.get_artists()

for i in range(228, 281):  # Artists table length is 281
    # dan - replace to (0, 100)
    # adi - replace to (100, 200)
    # itay - replace to (200, 281)
    _added_tracks = {'': ''}
    albums = database.get_artist_albums(artists[i])
    for al_id in albums:
        add_album_tracks(al_id, _added_tracks)
