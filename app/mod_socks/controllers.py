from flask import Blueprint, render_template, jsonify, request
from app import app
from app.database import misc_db_session as session

from app.mod_socks.models import SockCount, Tweet
from datetime import date, datetime
import json
import tweepy


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
    result = Tweet.query.order_by(Tweet.id.desc()).first()
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
        session.add(t)
        session.commit()


def getAvailableDates():
    dates = []
    for row in session.query(Tweet.timestamp).group_by(Tweet.timestamp):
        # Guarantees 2 character date fields
        dates.append("{:02d}-{:02d}-{:02d}".format(row.timestamp.year, row.timestamp.month, row.timestamp.day))
    return dates


def authenticateTwitterClient():
    auth = tweepy.OAuthHandler(app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'])
    auth.set_access_token(app.config['ACCESS_TOKEN'], app.config['ACCESS_TOKEN_SECRET'])
    return tweepy.API(auth, wait_on_rate_limit=True)
