import random

from flask import Flask, render_template, jsonify, request, session, redirect
from database import Database
from constants import *

app = Flask(__name__)
app.secret_key = 't3mp_k3y'
service_port = 40004
db = Database()


def generate_question(question_number):
    if question_number == 1:
        return artist_with_more_albums_than_avg()
    elif question_number == 2:
        return artist_last_album()
    else:
        return artist_with_more_albums_than_avg()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        session['number'] = 0
        session['question_number'] = 1
        session['target'] = 70
        data, session['correct'] = generate_question(session['question_number'])
        # print(session['correct'])
        return render_template('index.html', **data)
    else:
        req_data = request.get_data().decode('utf-8')
        # print(req_data)
        last_correct = session['correct']
        session['question_number'] += 1
        data, session['correct'] = generate_question(session['question_number'])
        data['correct'] = 'false'
        data['win'] = 'false'
        # print(last_correct)
        # print(req_data)
        if last_correct == req_data:
            data['correct'] = 'true'
            session['number'] += 1
            if session['number'] == session['target']:
                data['win'] = 'true'
            return jsonify(**data)
        # print(data)
        return jsonify(**data)


def shuffle_answers(wrong_answers, correct_answer):
    letters = ['a', 'b', 'c', 'd']
    random.shuffle(letters)
    wrong_answers.append(correct_answer)
    answers = [("answer_"+letter, ans) for letter, ans in zip(letters, wrong_answers)]
    return dict(answers), "answer_" + letters[len(letters) - 1]


def artist_last_album():
    question = None
    correct_answer = None
    wrong_answers = []
    # get random artist
    # todo: migrate the randomization to the question query itself
    while len(wrong_answers) < 3:
        random_artist = db.get_random_row(ARTISTS)
        artist_id = random_artist.get('artist_id')
        artist_name = random_artist.get('artist_name')

        correct_answer = db.get_artist_last_album(artist_id)

        question = QUESTION_LAST_ALBUM.format(artist=artist_name)
        wrong_answers = db.get_random_wrong_answers('album_name', ALBUMS, correct_answer)
    answers, correct_answer_number = shuffle_answers(wrong_answers, correct_answer)
    answers['win'] = 'false'
    answers['correct'] = 'true'
    answers['question'] = question
    # print("answer:")
    # print(answers)
    return answers, correct_answer_number


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


if __name__ == "__main__":
    app.run(port=service_port, host="0.0.0.0", debug=False)
