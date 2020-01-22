import random

from flask import Flask, render_template, jsonify, request, session, redirect
from database import Database
from constants import *

from SRC.constants import QUESTION_SONG_CONTAINS_WORDS

app = Flask(__name__)
app.secret_key = 't3mp_k3y'
service_port = 40004
db = Database()


def generate_question():
    questions_list = [artist_with_album_released_in_specific_decade_with_love_song,
                      avg_tracks_for_artist_albums,
                      artist_with_more_albums_than_avg,
                      movie_with_most_played_tracks_in_genre,
                      artist_with_mainly_tracks_from_specific_genre,
                      highest_rated_artist_without_movie_tracks,
                      sentence_to_fill_with_missing_word,
                      the_most_rated_artist,
                      first_released_album_out_of_four,
                      track_in_movie,
                      movie_without_track,
                      track_of_specific_artist,
                      year_of_birth_of_specific_artist,
                      song_that_contains_a_word]
    random.shuffle(questions_list)
    return questions_list[0]()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        session['number'] = 0
        session['question_number'] = 1
        session['target'] = 70
        data, session['correct'] = generate_question()
        # print(session['correct'])
        return render_template('index.html', **data)
    else:
        req_data = request.get_data().decode('utf-8')
        # print(req_data)
        last_correct = session['correct']
        session['question_number'] += 1
        data, session['correct'] = generate_question()
        data['correct'] = 'false'
        data['win'] = 'false'
        # print(last_correct)
        # print(req_data)
        if last_correct == req_data:
            data['correct'] = 'true'
            session['number'] += 1
            if session['number'] == session['target']:
                data['win'] = 'true'
                # print(data)
            return jsonify(**data)
        # print(data)
        return jsonify(**data)


def shuffle_answers(wrong_answers, correct_answer):
    letters = ['a', 'b', 'c', 'd']
    random.shuffle(letters)
    wrong_answers.append(correct_answer)
    answers = [("answer_"+letter, str(ans)) for letter, ans in zip(letters, wrong_answers)]
    return dict(answers), "answer_" + letters[len(letters) - 1]


def artist_with_more_albums_than_avg():
    question = QUESTION_ARTIST_WITH_MORE_ALBUMS_THAN_AVG
    correct_answer, wrong_answers = db.get_artist_with_more_albums_than_avg()
    answers, correct_answer_number = shuffle_answers(wrong_answers, correct_answer)
    answers['win'] = 'false'
    answers['correct'] = 'true'
    answers['question'] = question
    # print("answer:")
    # print(answers)
    return answers, correct_answer_number


def avg_tracks_for_artist_albums():
    correct_answer, wrong_answers, artist_name = db.get_avg_tracks_for_artist_albums()
    question = QUESTION_AVG_TRACKS_IN_ALBUM_FOR_ARTIST.format(artist=artist_name)
    answers, correct_answer_number = shuffle_answers(wrong_answers, correct_answer)
    answers['win'] = 'false'
    answers['correct'] = 'true'
    answers['question'] = question
    # print("answer:")
    # print(answers)
    return answers, correct_answer_number


def movie_with_most_played_tracks_in_genre():
    correct_answer, wrong_answers, genre_name = db.get_movie_with_most_played_tracks_in_genre()
    question = QUESTION_MOVIE_WITH_MOST_PLAYED_TRACKS_FROM_GENRE.format(genre=genre_name)
    answers, correct_answer_number = shuffle_answers(wrong_answers, correct_answer)
    answers['win'] = 'false'
    answers['correct'] = 'true'
    answers['question'] = question
    # print("answer:")
    # print(answers)
    return answers, correct_answer_number


def artist_with_mainly_tracks_from_specific_genre():
    correct_answer, wrong_answers, genre_name = db.get_artist_with_mainly_tracks_from_specific_genre()
    question = QUESTION_ARTIST_WITH_MAINLY_TRACKS_FROM_SPECIFIC_GENRE.format(genre=genre_name)
    answers, correct_answer_number = shuffle_answers(wrong_answers, correct_answer)
    answers['win'] = 'false'
    answers['correct'] = 'true'
    answers['question'] = question
    # print("answer:")
    # print(answers)
    return answers, correct_answer_number


def artist_with_album_released_in_specific_decade_with_love_song():
    correct_answer, wrong_answers, decade = db.get_artist_with_album_released_in_specific_decade_with_love_song()
    question = QUESTION_ARTIST_WITH_ALBUM_RELEASED_IN_SPECIFIC_DECADE_WITH_LOVE_SONG.format(decade=str(decade))
    answers, correct_answer_number = shuffle_answers(wrong_answers, correct_answer)
    answers['win'] = 'false'
    answers['correct'] = 'true'
    answers['question'] = question
    # print("answer:")
    # print(answers)
    return answers, correct_answer_number


def highest_rated_artist_without_movie_tracks():
    question = QUESTION_HIGHEST_RATED_ARTIST_WITHOUT_MOVIE_TRACKS
    correct_answer, wrong_answers = db.get_highest_rated_artist_without_movie_tracks()
    answers, correct_answer_number = shuffle_answers(wrong_answers, correct_answer)
    answers['win'] = 'false'
    answers['correct'] = 'true'
    answers['question'] = question
    # print("answer:")
    # print(answers)
    return answers, correct_answer_number


def sentence_to_fill_with_missing_word():
    correct_answer, wrong_answers, sentence = db.get_sentence_to_fill_with_missing_word()
    question = QUESTION_FILL_THE_MISSING_WORD.format(sentence=sentence)
    answers, correct_answer_number = shuffle_answers(wrong_answers, correct_answer)
    answers['win'] = 'false'
    answers['correct'] = 'true'
    answers['question'] = question
    # print("answer:")
    # print(answers)
    return answers, correct_answer_number


def the_most_rated_artist():
    correct_answer, wrong_answers = db.get_the_most_rated_artist()
    question = QUESTION_MOST_RATED_ARTIST
    answers, correct_answer_number = shuffle_answers(wrong_answers, correct_answer)
    answers['win'] = 'false'
    answers['correct'] = 'true'
    answers['question'] = question
    # print("answer:")
    # print(answers)
    return answers, correct_answer_number


def first_released_album_out_of_four():
    correct_answer, wrong_answers = db.get_first_released_album_out_of_four()
    question = QUESTION_FIRST_RELEASED_ALBUM
    answers, correct_answer_number = shuffle_answers(wrong_answers, correct_answer)
    answers['win'] = 'false'
    answers['correct'] = 'true'
    answers['question'] = question
    # print("answer:")
    # print(answers)
    return answers, correct_answer_number


def track_in_movie():
    correct_answer, wrong_answers, movie_name = db.get_track_in_movie()
    question = QUESTION_TRACK_IN_SPECIFIC_MOVIE.format(movie=movie_name)
    answers, correct_answer_number = shuffle_answers(wrong_answers, correct_answer)
    answers['win'] = 'false'
    answers['correct'] = 'true'
    answers['question'] = question
    # print("answer:")
    # print(answers)
    return answers, correct_answer_number


def movie_without_track():
    correct_answer, wrong_answers, track_name = db.get_movie_without_track()
    question = QUESTION_MOVIE_WITHOUT_SPECIFIC_TRACK.format(track=track_name)
    answers, correct_answer_number = shuffle_answers(wrong_answers, correct_answer)
    answers['win'] = 'false'
    answers['correct'] = 'true'
    answers['question'] = question
    # print("answer:")
    # print(answers)
    return answers, correct_answer_number


def track_of_specific_artist():
    correct_answer, wrong_answers, artist_name = db.get_track_of_specific_artist()
    question = QUESTION_TRACK_PLAYED_BY_SPECIFIC_ARTIST.format(artist=artist_name)
    answers, correct_answer_number = shuffle_answers(wrong_answers, correct_answer)
    answers['win'] = 'false'
    answers['correct'] = 'true'
    answers['question'] = question
    # print("answer:")
    # print(answers)
    return answers, correct_answer_number


def year_of_birth_of_specific_artist():
    correct_answer, wrong_answers, artist_name = db.get_year_of_birth_of_specific_artist()
    question = QUESTION_SPECIFIC_ARTIST_DATE_OF_BIRTH.format(artist=artist_name)
    answers, correct_answer_number = shuffle_answers(wrong_answers, correct_answer)
    answers['win'] = 'false'
    answers['correct'] = 'true'
    answers['question'] = question
    # print("answer:")
    # print(answers)
    return answers, correct_answer_number

def song_that_contains_a_word():
    correct_answer, wrong_answers, word_in_song = db.get_song_that_contain_a_word_from_list_of_words()
    question = QUESTION_SONG_CONTAINS_WORDS.format(word=word_in_song)
    answers, correct_answer_number = shuffle_answers(wrong_answers, correct_answer)
    answers['win'] = 'false'
    answers['correct'] = 'true'
    answers['question'] = question
    print("answer:")
    print(answers)
    return answers, correct_answer_number


if __name__ == "__main__":
    app.run(port=service_port, host="0.0.0.0", debug=False)

