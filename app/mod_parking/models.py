# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from app import db
import datetime, decimal


# Define a base model for other database tables to inherit
class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())


class SpotCount(Base):
    __tablename__ = 'parking_spots'

    count = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    level = db.Column(db.Integer, db.ForeignKey('parking_level.id'), nullable=False)

    def __init__(self, count, level):
        self.count = count
        self.timestamp = db.func.current_timestamp()
        self.level = level


class ParkingStructure(Base):
    __tablename__ = 'parking_structure'

    name = db.Column(db.String, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=False)

    def __init__(self, name, latitude, longitude, address, image):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.address = address
        self.image = image


class StructureLevel(Base):
    __tablename__ = 'parking_level'

    name = db.Column(db.String, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    structure = db.Column(db.Integer, db.ForeignKey('parking_structure.id'), nullable=False)

    def __init__(self, name, capacity, structure):
        self.name = name
        self.capacity = capacity
        self.structure = structure


def alchemyencoder(obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)


        # def __repr__(self):
        #     json = "capacity:{},count:{},timestamp:{},structure:{},level:{}".format(self.capacity, self.count, 1234,self.structure, self.level)
        #     return json
        #     # return 'In {} on level {} there were {} spots at {}'.format(self.structure, self.level, self.count, self.timestamp)
