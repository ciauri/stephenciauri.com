# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
# from app import db
from sqlalchemy import String, Column, Integer, ForeignKey, TIMESTAMP, func, DECIMAL
from app.database import PBase
import datetime, decimal


# Define a base model for other database tables to inherit
class BaseParking(PBase):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    date_created = Column(TIMESTAMP, default=func.current_timestamp())


# TODO: Decode and leverage timestamp given by server
class SpotCount(BaseParking):
    __tablename__ = 'parking_spots'

    count = Column(Integer, nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False, index=True, default=func.current_timestamp())
    level = Column(Integer, ForeignKey('parking_level.id'), nullable=False)

    def __init__(self, count, level):
        self.count = count
        self.level = level


class ParkingStructure(BaseParking):
    __tablename__ = 'parking_structure'

    name = Column(String(length=128), nullable=False)
    latitude = Column(DECIMAL(precision='10,6'), nullable=False)
    longitude = Column(DECIMAL(precision='10,6'), nullable=False)
    address = Column(String(length=128), nullable=False)
    image = Column(String(length=128), nullable=False)

    def __init__(self, name, latitude, longitude, address, image):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.address = address
        self.image = image


class StructureLevel(BaseParking):
    __tablename__ = 'parking_level'

    name = Column(String(length=128), nullable=False)
    capacity = Column(Integer, nullable=False)
    structure = Column(Integer, ForeignKey('parking_structure.id'), nullable=False)

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
