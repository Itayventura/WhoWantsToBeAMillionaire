import random
from flask import Flask, render_template, jsonify, request, session, redirect
from database import Database
from constants import *

app = Flask(__name__)
app.secret_key = 't3mp_k3y'
service_port = 40004
db = Database()

topic_sets = {'artist':{1,2,4,5,7, 11, 12}, 'albums':{1,2,8}, 'genres':{4}, 'movies':{3,5,9,10}, 'songs':{1,4,6,9,11,13}}

def generate_question(options_set):
    """ This function chooses a random question and calls the method that generates the question's data.
    :return: The question's data.
    """
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
    #random.shuffle(questions_list)
    question = questions_list[random.sample(options_set, 1)[0]]
    data, session['correct'] = question()
    #return questions_list[0]()
    return data

###############
# route funcs #
###############

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        session['number'] = 1
        session['question_number'] = 1
        session['target'] = 2
        session['topics'] = list(range(14))
        data = generate_question(session['topics'])
        print(session['correct'])
        return render_template('template.html', **data)
    else:
        req_data = request.get_data().decode('utf-8')
        last_correct = session['correct']
        session['question_number'] += 1
        data = generate_question(session['topics'])
        print(session['correct'])
        data['correct'] = 'false'
        data['win'] = 'false'
        data['answer'] = last_correct
        if last_correct == req_data:
            data['correct'] = 'true'
            session['number'] += 1
            if session['number'] >= session['target']:
                data['win'] = 'true'
            data['number'] = session['number']
            return jsonify(**data)
        return jsonify(**data)

@app.route('/new_game', methods=['POST'])
def new_game():
    session['number'] = 1
    data = generate_question(session['topics'])
    data['number'] = session['number']
    print(session['correct'])
    return jsonify(**data)

@app.route('/level', methods=['POST'])
def level():
    l = request.get_data().decode('utf-8')
    session['level'] = l
    if l == 'easy':
        session['target'] = 2
    if l == 'medium':
        session['target'] = 4
    if l == 'hard':
        session['target'] = 6
    return jsonify()

@app.route('/topics', methods=['POST'])
def topics():
    req_data = request.get_data().decode('utf-8')
    for topic, options in topic_sets.items():
        if req_data.find(topic) > -1:
            for item in options:
                if req_data.find('add') > -1 and item not in session['topics']:
                    session['topics'].append(item)
                elif req_data.find('remove') > -1 and item in session['topics']:
                    session['topics'].remove(item)
            return jsonify()
    return jsonify()

@app.route('/theme', methods=['POST'])
def theme():
    return jsonify()

#############
# route end #
#############
def shuffle_answers(wrong_answers, correct_answer):
    """ This function shuffles a question's four answers.
    :param wrong_answers: (list) A list of three wrong answers.
    :param correct_answer: (str) The correct answer.
    :return: 1. (dict) A dictionary of the shuffled answers.
             2. (str) The key of the correct answer.
    """
    letters = ['a', 'b', 'c', 'd']
    random.shuffle(letters)
    all_answers = wrong_answers + [correct_answer]
    answers = [("answer_"+letter, str(ans)) for letter, ans in zip(letters, all_answers)]
    return dict(answers), "answer_" + letters[len(letters) - 1]


def artist_with_more_albums_than_avg():
    """ This function creates the data for the question:
        'Which artist has more albums than the average?'
    :return: 1. (dict) The question data.
             2. (str) The key of the correct answer in data dict.
    """
    question = QUESTION_ARTIST_WITH_MORE_ALBUMS_THAN_AVG
    correct_answer, wrong_answers = db.get_artist_with_more_albums_than_avg()
    data, correct_answer_key = shuffle_answers(wrong_answers, correct_answer)
    data['question'] = question
    return data, correct_answer_key


def avg_tracks_for_artist_albums():
    """ This function creates the data for the question:
        'What is the average tracks number in <RANDOM_ARTIST>'s albums?'
    :return: 1. (dict) The question data.
             2. (str) The key of the correct answer in data dict.
    """
    correct_answer, wrong_answers, artist_name = db.get_avg_tracks_for_artist_albums()
    question = QUESTION_AVG_TRACKS_IN_ALBUM_FOR_ARTIST.format(artist=artist_name)
    data, correct_answer_key = shuffle_answers(wrong_answers, correct_answer)
    data['question'] = question
    return data, correct_answer_key


def movie_with_most_played_tracks_in_genre():
    """ This function creates the data for the question:
        'What is the movie with the most played tracks from genre <RANDOM_GENRE>?'
    :return: 1. (dict) The question data.
             2. (str) The key of the correct answer in data dict.
    """
    correct_answer, wrong_answers, genre_name = db.get_movie_with_most_played_tracks_in_genre()
    question = QUESTION_MOVIE_WITH_MOST_PLAYED_TRACKS_FROM_GENRE.format(genre=genre_name)
    data, correct_answer_key = shuffle_answers(wrong_answers, correct_answer)
    data['question'] = question
    return data, correct_answer_key


def artist_with_mainly_tracks_from_specific_genre():
    """ This function creates the data for the question:
        'To which of the following artists most of their tracks are from genre <RANDOM_GENRE>?'
    :return: 1. (dict) The question data.
             2. (str) The key of the correct answer in data dict.
    """
    correct_answer, wrong_answers, genre_name = db.get_artist_with_mainly_tracks_from_specific_genre()
    question = QUESTION_ARTIST_WITH_MAINLY_TRACKS_FROM_SPECIFIC_GENRE.format(genre=genre_name)
    data, correct_answer_key = shuffle_answers(wrong_answers, correct_answer)
    data['question'] = question
    return data, correct_answer_key


def artist_with_album_released_in_specific_decade_with_love_song():
    """ This function creates the data for the question:
        'Which of the following artists has an album released in the <RANDOM_DECADE>'s
         that has a track which contains the word 'love'?'
    :return: 1. (dict) The question data.
             2. (str) The key of the correct answer in data dict.
    """
    correct_answer, wrong_answers, decade = db.get_artist_with_album_released_in_specific_decade_with_love_song()
    question = QUESTION_ARTIST_WITH_ALBUM_WITH_LOVE_SONG.format(decade=str(decade))
    data, correct_answer_key = shuffle_answers(wrong_answers, correct_answer)
    data['question'] = question
    return data, correct_answer_key


def highest_rated_artist_without_movie_tracks():
    """ This function creates the data for the question:
        'Which of the following is the highest rated artist that his tracks have not been played in any movie?'
    :return: 1. (dict) The question data.
             2. (str) The key of the correct answer in data dict.
    """
    question = QUESTION_HIGHEST_RATED_ARTIST_WITHOUT_MOVIE_TRACKS
    correct_answer, wrong_answers = db.get_highest_rated_artist_without_movie_tracks()
    data, correct_answer_key = shuffle_answers(wrong_answers, correct_answer)
    data['question'] = question
    return data, correct_answer_key


def sentence_to_fill_with_missing_word():
    """ This function creates the data for the question:
        'Complete the following line from <RANDOM TRACK> by <ARTIST>: <RANDOM_SENTENCE_WITH_MISSING_WORD>'
    :return: 1. (dict) The question data.
             2. (str) The key of the correct answer in data dict.
    """
    correct_answer, wrong_answers, sentence, track_name, artist_name = db.get_sentence_to_fill_with_missing_word()
    question = QUESTION_FILL_THE_MISSING_WORD.format(track=track_name, artist=artist_name, sentence=sentence)
    data, correct_answer_key = shuffle_answers(wrong_answers, correct_answer)
    data['question'] = question
    return data, correct_answer_key


def the_most_rated_artist():
    """ This function creates the data for the question:
        'Which of the following is the most highly rated artist?'
    :return: 1. (dict) The question data.
             2. (str) The key of the correct answer in data dict.
    """
    correct_answer, wrong_answers = db.get_the_most_rated_artist()
    question = QUESTION_MOST_RATED_ARTIST
    data, correct_answer_key = shuffle_answers(wrong_answers, correct_answer)
    data['question'] = question
    return data, correct_answer_key


def first_released_album_out_of_four():
    """ This function creates the data for the question:
        'Which of the following albums was the first to be released?'
    :return: 1. (dict) The question data.
             2. (str) The key of the correct answer in data dict.
    """
    correct_answer, wrong_answers = db.get_first_released_album_out_of_four()
    question = QUESTION_FIRST_RELEASED_ALBUM
    data, correct_answer_key = shuffle_answers(wrong_answers, correct_answer)
    data['question'] = question
    return data, correct_answer_key


def track_in_movie():
    """ This function creates the data for the question:
        'What track is played in the movie <RANDOM_MOVIE>?'
    :return: 1. (dict) The question data.
             2. (str) The key of the correct answer in data dict.
    """
    correct_answer, wrong_answers, movie_name = db.get_track_in_movie()
    question = QUESTION_TRACK_IN_SPECIFIC_MOVIE.format(movie=movie_name)
    data, correct_answer_key = shuffle_answers(wrong_answers, correct_answer)
    data['question'] = question
    return data, correct_answer_key


def movie_without_track():
    """ This function creates the data for the question:
        'In which movie the track <TRACK_NAME> is not played?'
    :return: 1. (dict) The question data.
             2. (str) The key of the correct answer in data dict.
    """
    correct_answer, wrong_answers, track_name = db.get_movie_without_track()
    question = QUESTION_MOVIE_WITHOUT_SPECIFIC_TRACK.format(track=track_name)
    data, correct_answer_key = shuffle_answers(wrong_answers, correct_answer)
    data['question'] = question
    return data, correct_answer_key


def track_of_specific_artist():
    """ This function creates the data for the question:
        'Which of the following tracks is played by the artist <RANDOM_ARTIST>?'
    :return: 1. (dict) The question data.
             2. (str) The key of the correct answer in data dict.
    """
    correct_answer, wrong_answers, artist_name = db.get_track_of_specific_artist()
    question = QUESTION_TRACK_PLAYED_BY_SPECIFIC_ARTIST.format(artist=artist_name)
    data, correct_answer_key = shuffle_answers(wrong_answers, correct_answer)
    data['question'] = question
    return data, correct_answer_key


def year_of_birth_of_specific_artist():
    """ This function creates the data for the question:
        'What is the birth date of <RANDOM_ARTIST>?'
    :return: 1. (dict) The question data.
             2. (str) The key of the correct answer in data dict.
    """
    correct_answer, wrong_answers, artist_name = db.get_year_of_birth_of_specific_artist()
    question = QUESTION_SPECIFIC_ARTIST_DATE_OF_BIRTH.format(artist=artist_name)
    data, correct_answer_key = shuffle_answers(wrong_answers, correct_answer)
    data['question'] = question
    return data, correct_answer_key


def song_that_contains_a_word():
    """ This function creates the data for the question:
        'Which of the following songs contains the word <RANDOM_WORD>?'
    :return: 1. (dict) The question data.
             2. (str) The key of the correct answer in data dict.
    """
    correct_answer, wrong_answers, word_in_song = db.get_song_that_contain_a_word_from_list_of_words()
    question = QUESTION_SONG_CONTAINS_WORDS.format(word=word_in_song)
    data, correct_answer_key = shuffle_answers(wrong_answers, correct_answer)
    data['question'] = question
    return data, correct_answer_key


if __name__ == "__main__":
    app.run(port=service_port, host="0.0.0.0", debug=True)

