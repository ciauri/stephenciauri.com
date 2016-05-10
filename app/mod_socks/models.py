# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
# from app import db
from sqlalchemy import Float, DateTime, Column, Integer, func
from app.database import MiscBase

# Define a base model for other database tables to inherit
class BaseSock(MiscBase):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    date_created = Column(DateTime, default=func.current_timestamp())


# Define a SockCount model
class SockCount(BaseSock):
    __tablename__ = 'socks'

    # Number of Socks
    count = Column(Integer, nullable=False)

    # Id of the last tweet in this call
    last_id = Column(Integer, nullable=False, unique=True)

    # New instance instantiation procedure
    def __init__(self, count, last_id):
        self.count = count
        self.last_id = last_id

    def __repr__(self):
        return '<Number of socks at {}: {}>'.format(self.date_created, self.count)


class Tweet(BaseSock):
    __tablename__ = 'tweet'

    lat = Column(Float)
    lng = Column(Float)
    timestamp = Column(DateTime, nullable=False)
    tweet_id = Column(Integer, nullable=False, unique=True)

    def __init__(self, timestamp, tweet_id, lat=None, lng=None):
        self.timestamp = timestamp
        self.lat = lat
        self.lng = lng
        self.tweet_id = tweet_id

    def __repr__(self):
        return '<Timestamp: {}, Coords: ({},{})'.format(self.timestamp, self.lat, self.lng)
