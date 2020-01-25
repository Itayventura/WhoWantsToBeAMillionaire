import mysql.connector
import sql_queries
import random
import re
import json
from datetime import datetime
from constants import *


class Database:
    """
    A class used to connect and interact with a MySQL database.
    Attributes:
        cnx: The MySQL connection object.
        cursor: The MySQL cursor object which interacts with the MySQL server.
    """
    def __init__(self):
        self.cnx = mysql.connector.connect(user=DB_USERNAME,
                                           password=DB_PASSWORD,
                                           host=DB_HOST,
                                           database=DB_NAME,
                                           port=DB_PORT)
        self.cursor = self.cnx.cursor()

    def insert_row(self, table_name, values):
        """ This function inserts a record into a table in our database.
        :param table_name: (str) The table name.
        :param values: (list) The record data.
        """
        input_values = ', '.join(map(lambda x: "%s", values))
        sql_query = f'INSERT INTO `%s` VALUES (%s)' % (table_name, input_values)
        try:
            self.cursor.execute(sql_query, tuple(values))
            self.cnx.commit()
        except Exception as ex:
            print(ex)
            self.cnx.rollback()

    def get_artist_with_more_albums_than_avg(self):
        self.cursor.execute(sql_queries.get_artist_with_more_albums_than_avg)
        data = self.cursor.fetchall()
        # return correct_answer, [wrong_answers]
        return data[0][0], [data[i][0] for i in range(1, len(data))]

    def get_avg_tracks_for_artist_albums(self):
        self.cursor.execute(sql_queries.get_avg_tracks_for_artist_albums)
        data = self.cursor.fetchall()
        avg_track_in_album = data[0][0]
        avg_track_in_album = round(float(avg_track_in_album), 1)
        # return avg(tracks_count_in_album), 3 wrong answers, artist_name
        return avg_track_in_album, self.generate_3_random_numbers(avg_track_in_album), data[0][1]

    def generate_3_random_numbers(self, avg_num):
        """
        :param avg_num: Correct answer for get_avg_tracks_for_artist_albums()
        :return: Three random different answers
        """
        random_nums = set([])
        while len(random_nums) < 3:
            random1 = round(random.uniform(4.0, 20.0), 1)
            if random1 != avg_num and random1 not in random_nums:
                random_nums.add(random1)
        return list(random_nums)

    def get_movie_with_most_played_tracks_in_genre(self):
        data = []
        while len(data) == 0:
            self.cursor.execute(sql_queries.get_movie_with_most_played_tracks_in_genre)
            data = self.cursor.fetchall()
        # return correct answer, [wrong answers], genre_name
        return data[0][0], [data[i][1] for i in range(len(data))], data[0][len(data) - 1]

    def get_artist_with_mainly_tracks_from_specific_genre(self):
        data = []
        genre_name = None
        while len(data) < 4:
            genre_id, genre_name = self.generate_random_genre()
            self.cursor.execute(sql_queries.get_artist_with_mainly_tracks_from_specific_genre % (genre_id, genre_id))
            data = self.cursor.fetchall()
        # return correct_answer, [wrong_answers], genre_name
        return data[0][0], [data[i][0] for i in range(1, len(data))], genre_name

    def generate_random_genre(self):
        self.cursor.execute(sql_queries.get_random_genre)
        data = self.cursor.fetchall()
        # return genre_id, genre_name
        return data[0][0], data[0][1]

    def get_artist_with_album_released_in_specific_decade_with_love_song(self):
        decades = [year for year in range(1950, 2010, 10)]
        data = []
        while len(data) < 4:
            random.shuffle(decades)
            decade_start = datetime(decades[0], 1, 1)
            decade_end = datetime(decades[0] + 10, 1, 1)
            self.cursor.execute(sql_queries.get_artist_with_album_released_in_specific_decade_with_love_song,
                                (decade_start, decade_end, decade_start, decade_end))
            data = self.cursor.fetchall()
        # return correct_answer, [wrong_answers], decade
        return data[0][0], [data[i][0] for i in range(1, len(data))], decades[0]

    def get_highest_rated_artist_without_movie_tracks(self):
        self.cursor.execute(sql_queries.get_highest_rated_artist_without_movie_tracks)
        data = self.cursor.fetchall()
        # return correct_answer, [wrong_answers]
        return data[0][1], [data[i][1] for i in range(1, len(data))]

    def get_sentence_to_fill_with_missing_word(self):
        data = []
        sentence = None
        track_name = None
        artist_name = None
        while not sentence:
            self.cursor.execute(sql_queries.get_random_track_lyrics)
            data = self.cursor.fetchall()
            track_name = data[0][0]
            artist_name = data[0][1]
            sentence = self.get_sentence_from_lyrics(data[0][2])
        # remove special characters from lyrics to apply correct logic
        lyrics_without_special_chars = re.sub(r'\?|\.|,|;|\"|:', '', data[0][2])
        sentence, missing_word = self.get_word_and_sentence_without_the_word(sentence)
        wrong_answers = self.get_3_wrong_missing_words(lyrics_without_special_chars, missing_word)
        # return correct_answer, [wrong_answers], sentence_to_fill
        return missing_word, wrong_answers, sentence, track_name, artist_name

    def get_3_wrong_missing_words(self, lyrics, missing_word):
        split_lyrics = lyrics.split()
        wrong_answers = []
        while len(wrong_answers) < 3:
            random_word = random.choice(split_lyrics)
            if random_word and random_word != missing_word and random_word.lower() not in wrong_answers:
                wrong_answers.append(random_word.lower())
        return wrong_answers

    def get_word_and_sentence_without_the_word(self, sentence):
        split_sentence = sentence.split()
        rand = random.randint(0, len(split_sentence) - 1)
        while len(split_sentence[rand]) < 3:
            rand = random.randint(0, len(split_sentence) - 1)
        missing_word = split_sentence[rand]
        return sentence.replace(missing_word, "____", 1).lower(), missing_word.lower()

    def get_sentence_from_lyrics(self, lyrics):
        sentences = lyrics.splitlines()
        for sentence in sentences:
            if not sentence:
                continue
            split_sentence = sentence.split()
            if len(split_sentence) >= 3:
                return sentence
        return None

    def get_the_most_rated_artist(self):
        data = []
        while len(data) == 0:
            self.cursor.execute(sql_queries.get_the_most_rated_artist)
            data = self.cursor.fetchall()
        # return correct_answer, [wrong_answers]
        return data[0][0], [data[i][1] for i in range(0, len(data))]

    def get_first_released_album_out_of_four(self):
        data = []
        while len(data) == 0:
            self.cursor.execute(sql_queries.get_first_released_album_out_of_four)
            data = self.cursor.fetchall()
        # return correct_answer, [wrong_answers]
        return data[0][0], [data[i][1] for i in range(0, len(data))]

    def get_track_in_movie(self):
        data = []
        while len(data) == 0:
            self.cursor.execute(sql_queries.get_track_in_movie)
            data = self.cursor.fetchall()
        # return correct_answer, [wrong_answers], movie_name
        return data[0][1], [data[i][2] for i in range(0, len(data))], data[0][0]

    def get_movie_without_track(self):
        data = []
        while len(data) == 0:
            self.cursor.execute(sql_queries.get_movie_without_track)
            data = self.cursor.fetchall()
        # return correct_answer, [wrong_answers], track_name
        return data[0][1], [data[i][2] for i in range(0, len(data))], data[0][0]

    def get_track_of_specific_artist(self):
        data = []
        while len(data) == 0:
            self.cursor.execute(sql_queries.get_track_of_specific_artist)
            data = self.cursor.fetchall()
        # return correct_answer, [wrong_answers], artist_name
        return data[0][0], [data[i][2] for i in range(0, len(data))], data[0][1]

    def get_year_of_birth_of_specific_artist(self):
        data = []
        is_data_ok = False
        while not is_data_ok:
            self.cursor.execute(sql_queries.get_year_of_birth_of_specific_artist)
            data = self.cursor.fetchall()
            is_data_ok = data[0][1] is not None
        wrong_answers = self.generate_3_date_of_birth(data[0][1])
        # return correct_answer, [wrong_answers], artist_name
        return data[0][1], wrong_answers, data[0][0]

    def generate_3_date_of_birth(self, origin_date):
        dates = []
        given_year = origin_date.year
        while len(dates) < 3:
            random_day = random.randint(1, 28)
            random_month = random.randint(1, 12)
            if given_year >= 2000:
                end_range = given_year
            else:
                end_range = given_year + 10
            random_year = random.randint(given_year - 30, end_range)
            random_date_string = str(datetime(random_year, random_month, random_day))
            if random_date_string not in dates and random_date_string != str(origin_date):
                dates.append(random_date_string[:11])
        return dates

    def get_song_that_contain_a_word_from_list_of_words(self):
        words = ["sky", "sea", "vacation", "beach", "europe"]
        word = random.choice(words)
        data = []
        while len(data) < 4:
            self.cursor.execute(sql_queries.get_song_that_contain_a_word_from_list_of_words % (word, word))
            data = self.cursor.fetchall()
        # return: correct_answer, [wrong_answers], word
        return data[0][0], [data[i][0] for i in range(1, len(data))], word
