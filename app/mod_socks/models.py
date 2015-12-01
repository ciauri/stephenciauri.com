# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from app import db


# Define a base model for other database tables to inherit
class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())


# Define a SockCount model
class SockCount(Base):
    __tablename__ = 'socks'

    # Number of Socks
    count = db.Column(db.Integer, nullable=False)

    # Id of the last tweet in this call
    last_id = db.Column(db.Integer, nullable=False, unique=True)

    # New instance instantiation procedure
    def __init__(self, count, last_id):
        self.count = count
        self.last_id = last_id

    def __repr__(self):
        return '<Number of socks at {}: {}>'.format(self.date_created, self.count)


class Tweet(Base):
    __tablename__ = 'tweet'

    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, nullable=False)
    tweet_id = db.Column(db.Integer, nullable=False, unique=True)

    def __init__(self, timestamp, tweet_id, lat=None, lng=None):
        self.timestamp = timestamp
        self.lat = lat
        self.lng = lng
        self.tweet_id = tweet_id

    def __repr__(self):
        return '<Timestamp: {}, Coords: ({},{})'.format(self.timestamp, self.lat, self.lng)
