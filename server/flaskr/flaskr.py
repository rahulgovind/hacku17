import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask import request, session
from middleware.StreamConsumingMiddleware import StreamConsumingMiddleware
from models.models import db, Profile
from werkzeug.utils import secure_filename
from numpy.random import randint

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
UPLOAD_FOLDER = '/tmp'


def create_app(migrate=False):
    app = Flask(__name__)  # create the application instance :)
    app.wsgi_app = StreamConsumingMiddleware(app.wsgi_app)
    db.init_app(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    if migrate:
        with app.app_context():
            # Extensions like Flask-SQLAlchemy now know what the "current" app
            # is while within this block. Therefore, you can now run........
            print "Migrating"
            db.create_all()
    # app.config.from_object(__name__) # load config from this file , flaskr.py
    # app.config.from_envvar('FLASKR_SETTINGS', silent=True)

    app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'
    return app


app = create_app()


def get_session_files_key(key):
    return 'files-' + key


@app.route('/', methods=['GET', 'POST'])
def show_hello_world():
    if request.method == 'GET':
        return render_template("home.html", file_session=randint(1, 1e9))
    else:
        files = request.files.getlist('files[]')
        file_paths = []
        file_session_key = request.form['file_session']
        print 'File session key: ', file_session_key

        for file in files:
            print 'Filename: ', file.filename
            if len(file.filename) > 0:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                print file_path

                file.save(file_path)
                file_paths.append(file_path)
            else:
                # First file being sent is some empty file
                print 'Ignoring (possibly) empty file'

        if get_session_files_key(file_session_key) not in session:
            session[get_session_files_key(file_session_key)] = file_paths
        else:
            for file_path in file_paths:
                if file_path not in session[get_session_files_key(file_session_key)]:
                    l = session[get_session_files_key(file_session_key)]
                    l.append(file_path)
                    session[get_session_files_key(file_session_key)] = l

        return str(session[get_session_files_key(file_session_key)])


@app.route('/analyze')
def analyze():
    file_session_key = request.args.get('file_session')
    if get_session_files_key(file_session_key) in session:
        files = session[get_session_files_key(file_session_key)]
        return render_template("show-analysis.html", files=files)


@app.route('/create-profile', methods=['GET', 'POST'])
def create_profile():
    if request.method == 'GET':
        return render_template('create-profile.html')
    else:
        name = request.form['name']
        keywords = request.form['keywords']

        profile = Profile(name=name, keywords=keywords)
        db.session.add(profile)
        db.session.commit()

        return "%s<br/>%s<h2>Successful</h2>" % (name, keywords)


@app.route('/show-profiles')
def show_profiles():
    profiles = Profile.query.all()
    return render_template("show-profiles.html", profiles=profiles)