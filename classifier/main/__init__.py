import os
import json

import pandas as pd

from flask import (redirect, url_for, render_template, request, flash,
                   send_from_directory, Blueprint, current_app)
from werkzeug.utils import secure_filename
from classifier import db as classifier_db
from datetime import datetime, timedelta

ALLOWED_EXTENSIONS = set(['json', 'csv'])


main_blueprint = Blueprint(
    'main',
    __name__,
    template_folder='./templates'
)


def parse_json_to_db(filename):
    db = classifier_db.get_db()
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    with open(path, 'r') as jsonfile:
        j = json.load(jsonfile)
        for line in j:
            db.execute("INSERT INTO data(label, content) VALUES(?, ?)",
                       (None, line['text'].strip()))
        db.commit()


def parse_csv_to_db(filename):
    db = classifier_db.get_db()
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    csvfile = pd.read_csv(path)
    for line in csvfile.get('text_content'):
        db.execute("INSERT INTO data(label, content) VALUES(?, ?)",
                   (None, line))
    db.commit()


def allowed_file(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    return ext if '.' in filename and ext else None


@main_blueprint.route('/')
def index():
    db = classifier_db.get_db()
    row = db.execute(
        'SELECT id FROM data LIMIT 1'
    ).fetchone()
    print(row)
    if row is not None:
        return render_template('index.html',
                               is_populated=True)
    else:
        return render_template('index.html')


@main_blueprint.route('/start_label')
def start_label():
    db = classifier_db.get_db()
    first_row = db.execute(
        'SELECT id, content FROM data '
        'WHERE label IS NULL ORDER BY id LIMIT 1'
    ).fetchone()
    if first_row:
        return redirect(
            'label/' + str(first_row[0])
        )
    else:
        return redirect(url_for('index'))


@main_blueprint.route('/label/<int:id>')
def label(id):
    db = classifier_db.get_db()
    data = db.execute('SELECT id, content FROM data WHERE id = ?',
                      (id,)).fetchone()

    stats_minute = db.execute(
        'SELECT COUNT(id) FROM data WHERE '
        'label IS NOT NULL '
        'AND datetime_update < ? '
        'AND datetime_update >= ?',
        (datetime.now(), datetime.now() - timedelta(minutes=1),)
    ).fetchone()
    others = db.execute(
        "SELECT count(id) FROM data WHERE label='other';"
    ).fetchone()
    refs = db.execute(
        "SELECT count(id) FROM data WHERE label='ref';"
    ).fetchone()

    stats = {
       'minutes': stats_minute[0],
       'others': others[0],
       'refs': refs[0],
    }
    print(stats_minute[0])
    return render_template(
        'label.html',
        text=data[1],
        id=data[0],
        stats=stats,
    )


@main_blueprint.route('/classify/<string:label>/<int:id>')
def classify(label, id):
    db = classifier_db.get_db()
    db.execute("UPDATE data SET label=?, datetime_update=? WHERE id=?",
               (label, datetime.now(), id,))
    db.commit()

    next = db.execute('SELECT id FROM data '
                      'WHERE id > ?  AND label IS NULL',
                      (id,)).fetchone()
    if next:
        return redirect(
            'label/' + str(next[0])
        )
    else:
        return redirect(url_for('index'))


@main_blueprint.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        flash('You didn\'t include a file.')
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        flash('You didn\'t include a file.')
        return redirect(url_for('index'))
    file_ext = allowed_file(file.filename)
    if file and file_ext:
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        if file_ext == 'json':
            parse_json_to_db(file.filename)
        if file_ext == 'csv':
            parse_csv_to_db(file.filename)

    return redirect(url_for('index'))


@main_blueprint.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'],
                               filename)
