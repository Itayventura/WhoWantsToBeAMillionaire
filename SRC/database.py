import mysql.connector
import sql_queries
import random
import json

from constants import *


class Database:
    def __init__(self):
        self.cnx = mysql.connector.connect(user=DB_USERNAME,
                                           password=DB_PASSWORD,
                                           host=DB_HOST,
                                           database=DB_NAME,
                                           port=DB_PORT)
        self.cursor = self.cnx.cursor()

    def organized_results(self):
        field_names = [i[0] for i in self.cursor.description]
        data = self.cursor.fetchall()
        if len(data) == 1:
            return dict(zip(field_names, data[0]))
        ret = []
        for row in data:
            ret.append(dict(zip(field_names, row)))
        return ret

    def get_random_row(self, table_name):
        self.cursor.execute(sql_queries.get_random_row % table_name)
        return self.organized_results()

    def get_artist_name(self, artist_id):
        self.cursor.execute(sql_queries.get_artist_name % artist_id)
        return self.organized_results()

    def get_artist_last_album(self, artist_id):
        self.cursor.execute(sql_queries.get_artist_last_album % artist_id)
        data = self.organized_results()
        if data:
            return data.get('album_name')
        return None

    def get_random_wrong_answers(self, attribute_name, table_name, unwanted_value):
        self.cursor.execute(sql_queries.get_random_wrong_answers % (attribute_name, table_name,
                                                                    attribute_name, unwanted_value))
        data = self.organized_results()
        return [row[attribute_name] for row in data]

    def get_artist_with_more_albums_than_avg(self):
        self.cursor.execute(sql_queries.get_artist_with_more_albums_than_avg)
        data = self.cursor.fetchall()
        # return: correct_answer, [wrong_answers]
        return data[0][0], [data[i][0] for i in range(1, len(data))]

    def get_avg_tracks_for_artist_albums(self):
        avg_track_in_album = 0
        while not avg_track_in_album:
            self.cursor.execute(sql_queries.get_avg_tracks_for_artist_albums)
            data = self.cursor.fetchall()
            avg_track_in_album = data[0][0]
        avg_track_in_album = round(avg_track_in_album, 2)
        # return: avg(tracks_count_in_album), 3 wrong answers, artist_name
        return avg_track_in_album, self.generate_3_random_numbers(avg_track_in_album), data[0][1]

    def generate_3_random_numbers(self, avg_num):
        random_nums = set([])
        while len(random_nums) < 3:
            random1 = round(random.uniform(4.0, 20.0), 2)
            if random1 != avg_num and random1 not in random_nums:
                random_nums.add(random1)
        return list(random_nums)

    def get_movie_with_most_played_tracks_in_genre(self):
        data = []
        while len(data) == 0:
            self.cursor.execute(sql_queries.get_movie_with_most_played_tracks_in_genre)
            data = self.cursor.fetchall()
        return data[0][0], [data[i][1] for i in range(len(data))], data[0][len(data) - 1]

