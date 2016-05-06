from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup, Link, Separator, Text
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config.from_object('config')

# Database Creation
db = SQLAlchemy(app)
db.create_all()

# Bootstrap / Nav Init
Bootstrap(app)
nav = Nav()
nav.init_app(app)

from app.mod_index.controllers import mod_index as index
app.register_blueprint(index)

from app.mod_login.controllers import mod_login as login
app.register_blueprint(login)

from app.mod_socks.controllers import mod_socks as socks
app.register_blueprint(socks)

from app.mod_parking.controllers import mod_parking as parking

app.register_blueprint(parking)
# app.register_blueprint(home)

db.create_all()

from app.mod_socks.controllers import getTweets
from app.mod_parking.controllers import updateCounts

# The supposed 'cron'
@app.before_first_request
def initialize(*args, **kwargs):
    print("before first request!!")
    apsched = BackgroundScheduler()
    apsched.start()
    apsched.add_job(func=getTweets, trigger='cron', minute="*", id="queryTwitter", max_instances=1)
    apsched.add_job(func=updateCounts, trigger='cron', minute="*", id="queryChapman", max_instances=1)



@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@nav.navigation()
def navbar():
    return Navbar(
        'Stephen Ciauri',
        View('Home', 'index.index'),
        Subgroup(
            'Projects',
            View('Login Fun', 'login.signin'),
            View('Sock Counter', 'socks.index')
        ),
        Subgroup(
            'Docs',
            Link('Flask-Bootstrap', 'http://pythonhosted.org/Flask-Bootstrap'),
            Link('Flask-AppConfig', 'https://github.com/mbr/flask-appconfig'),
            Link('Flask-Debug', 'https://github.com/mbr/flask-debug'),
            Separator(),
            Text('Bootstrap'),
            Link('Getting started', 'http://getbootstrap.com/getting-started/'),
            Link('CSS', 'http://getbootstrap.com/css/'),
            Link('Components', 'http://getbootstrap.com/components/'),
            Link('Javascript', 'http://getbootstrap.com/javascript/'),
            Link('Customize', 'http://getbootstrap.com/customize/'),
        ),
    )
