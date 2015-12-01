from flask import Blueprint, render_template, jsonify, request
from app import db
from app.mod_socks.models import SockCount, Tweet
from datetime import date, datetime
import json
import tweepy

CONSUMER_KEY = "3MfRIm1nDoj4mxFRUYNsJbPCe"
CONSUMER_SECRET = "lqUmpH7mAST9kAwUYCkbKCeW5J2kXvmniFlz0Wyix6NkIeeqYQ"
ACCESS_TOKEN = "260134827-ccPniU4me4pDCXC2B8ot8d7ylfPntZikYIKg0Zyb"
ACCESS_TOKEN_SECRET = "AGg2VDYFchBeb5Zr8omPSKo13AeJY9U3yu4uIuytcEGLX"

mod_socks = Blueprint('socks', __name__)


@mod_socks.route('/socks/', methods=['GET'])
def index():
    return render_template("socks/root.html", header="Sock Counter 5000", dates=getAvailableDates())


@mod_socks.route('/socks/_updateCounter', methods=['GET', 'POST'])
def updateClientCounter():
    if request.method == 'POST':
        unformattedDate = json.loads(request.form['date'])
        reqDate = datetime(unformattedDate['year'], unformattedDate['month'], unformattedDate['day'])
        count = Tweet.query.filter(Tweet.timestamp.startswith(
            "{:%Y-%m-%d}".format(reqDate))).group_by("timestamp").count()
    else:
        reqDate = datetime.utcnow()
        count = Tweet.query.filter(
            Tweet.timestamp.startswith("{:%Y-%m-%d}".format(reqDate))).group_by(
            "timestamp").count()

    return jsonify(result=count)


@mod_socks.route('/socks/_graphData', methods=['GET', 'POST'])
def graphData():
    if request.method == 'POST':
        date = json.loads(request.form['date'])
        reqDate = datetime(date['year'], date['month'], date['day'])
        socks = Tweet.query.filter(Tweet.timestamp.startswith(
            "{:%Y-%m-%d}".format(reqDate))).group_by("timestamp").all()
    else:
        reqDate = datetime.utcnow()
        socks = Tweet.query.filter(
            Tweet.timestamp.startswith("{:%Y-%m-%d}".format(reqDate))).group_by(
            "timestamp").all()

    hourly_summary = {}
    for sock in socks:
        if sock.timestamp.hour not in hourly_summary:
            hourly_summary[sock.timestamp.hour] = 1
        else:
            hourly_summary[sock.timestamp.hour] += 1
    return jsonify(result=hourly_summary)


# Method is scheduled to run every minute. Initiated in app init.
def getTweets():
    api = authenticateTwitterClient()
    result = Tweet.query.order_by('-tweet_id').first()
    if result:
        last_id = result.tweet_id
    else:
        last_id = None
    # last_id = Tweet.query.order_by('-tweet_id').first().tweet_id
    cursor = tweepy.Cursor(api.search, q="#socks", since_id=last_id)
    for tweet in cursor.items():
        ts = tweet.created_at
        id = tweet.id

        if tweet.coordinates:
            print(tweet.coordinates)
            lat = tweet.coordinates['coordinates'][1]
            lng = tweet.coordinates['coordinates'][0]
        else:
            lat = None
            lng = None

        t = Tweet(ts, id, lat, lng)
        db.session.add(t)
        db.session.commit()


def getAvailableDates():
    dates = []
    for row in db.session.query(Tweet.timestamp).group_by("strftime('%Y-%m-%d',timestamp)"):
        dates.append("{}-{}-{}".format(row.timestamp.year, row.timestamp.month, row.timestamp.day))
    return dates


def authenticateTwitterClient():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    return tweepy.API(auth, wait_on_rate_limit=True)
