import random

from flask import Flask, render_template, jsonify, request, session
from database import Database
from constants import *

app = Flask(__name__)
service_port = 40004
db = Database()
united_states = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    if (request.method == 'GET'):
        data = artist_last_album()
        return render_template('index.html', **data)
    else:
        data = artist_last_album()
        print(data)
        return jsonify(**data)


def shuffle_answers(wrong_answers):
    answers = [("answer_"+str(i), ans) for i, ans in enumerate(wrong_answers, 1)]
    print(answers)
    random.shuffle(answers)
    return dict(answers)


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
    wrong_answers.append(correct_answer)
    answers = shuffle_answers(wrong_answers)
    answers['win'] = 'false'
    answers['correct'] = 'true'
    answers['question'] = question
    return answers


if __name__ == "__main__":
    app.run(port=service_port, host="0.0.0.0")
