import random

from flask import Flask, render_template
from database import Database
from constants import *

app = Flask(__name__)
service_port = 40001
db = Database()


@app.route('/')
def index():
    return app.send_static_file('index.html')


def shuffle_answers(correct_answer, wrong_answers):
    answers = [(ans, i) for i, ans in enumerate(wrong_answers, 1)] + [(correct_answer, 0)]
    print(answers)
    random.shuffle(answers)
    return dict(answers)


@app.route('/artist_last_album')
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
    answers = shuffle_answers(correct_answer, wrong_answers)
    return render_template('index.html',
                           question=question,
                           answers=answers)


if __name__ == "__main__":
    app.run(port=service_port)
