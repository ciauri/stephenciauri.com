from flask import Blueprint, render_template, jsonify, request, Response
from app.database import parking_db_session as session

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

# from app import db, app

from app.mod_parking.models import SpotCount, ParkingStructure, StructureLevel, alchemyencoder
# from datetime import date, datetime
import json
# import datetime
from enum import Enum
import dateutil.parser
from sqlalchemy import text

class QueryType(Enum):
    all = 0
    latest = 1
    since = 2


mod_parking = Blueprint('parking', __name__)


@mod_parking.route('/parking/counts', methods=['GET'])
def allCounts():
    return __buildJSON(QueryType.all)


@mod_parking.route('/parking/counts/latest', methods=['GET'])
def latestCounts():
    return __buildJSON(QueryType.latest)


@mod_parking.route('/parking/counts/since/<string(length=23):dateString>', methods=['GET'])
def allCountsSince(dateString):
    try:
        json = __buildJSON(QueryType.since, dateString)
    except:
        json = jsonify(error=True)

    return json


remoteStructures = None
remoteLevels = None

def updateCounts():
    data = urlopen("https://webfarm.chapman.edu/parkingservice/parkingservice/counts").read().decode('utf8')
    jsonData = json.loads(data)

    for structure in jsonData["Structures"]:
        structureID = _getStructure(structure)
        for level in structure["Levels"]:
            levelID = __getLevel(level, structureID)
            count = level["CurrentCount"]
            c = SpotCount(count=count, level=levelID)
            session.add(c)

    session.commit()


def __buildJSON(type, dateString=None):
    jsonData = {}
    jsonData["structures"] = []
    for (index, structure) in enumerate(ParkingStructure.query.all()):
        jsonData["structures"].append({"name": structure.name,
                                       "lat": structure.latitude,
                                       "long": structure.longitude,
                                       "address": structure.address,
                                       "image": structure.image,
                                       "levels": []})
        for (levelIndex, level) in enumerate(
                StructureLevel.query.filter(StructureLevel.structure == structure.id).all()):
            jsonData["structures"][index]["levels"].append({"name": level.name,
                                                            "capacity": level.capacity,
                                                            "counts": []})

            # deltaQuery = SpotCount.query.from_statement(
            #     text(
            #             'select *\
            #             from parking_spots p\
            #             where p.count <>\
            #                     (select count\
            #                     from parking_spots p2\
            #                     where p.level = p2.level and p.timestamp < p2.timestamp\
            #                     order by p2.timestamp ASC\
            #                     limit 1)\
            #             and p.level=:level\
            #             or p.id = (select min(id) from parking_spots where level = p.level)\
            #             order by p.timestamp ASC'
            #     )
            # ).params(level=level.id)


            if type is QueryType.all:
                # counts = deltaQuery.all()
                counts = SpotCount.query.filter(SpotCount.level == level.id).all()
            elif type is QueryType.latest:
                counts = [
                    SpotCount.query.filter(SpotCount.level == level.id).order_by(SpotCount.timestamp.desc()).first()]
            elif type is QueryType.since and dateString is not None:
                date = dateutil.parser.parse(dateString)
                print(date)
                print(dateString)
                counts = SpotCount.query.filter(SpotCount.level == level.id, SpotCount.timestamp > date).all()
                print(counts)
            else:
                counts = []

            for count in counts:
                # if isinstance(count.timestamp, str):
                #     ts = dateutil.parser.parse(count.timestamp).isoformat()
                # else:
                #     ts = count.timestamp.isoformat()

                jsonData["structures"][index]["levels"][levelIndex]["counts"].append({"count": count.count,
                                                                                      "timestamp": count.timestamp.isoformat()})
    return jsonify(**jsonData)


def _getStructure(structureJSON):
    name = structureJSON["Name"]
    lat = structureJSON["Latitude"]
    long = structureJSON["Longitude"]
    address = structureJSON["Address"]
    image = structureJSON["XhdpiDetailImage"]
    print("lat: {}, long: {}".format(lat, long))

    struct = session.query(ParkingStructure).filter(ParkingStructure.name == name,
                                                    ParkingStructure.latitude == lat,
                                                    ParkingStructure.longitude == long).one_or_none()


    if not struct:
        print("making new struct")
        s = ParkingStructure(name=name, latitude=lat, longitude=long, address=address, image=image)
        session.add(s)
        session.commit()
        return s.id
    else:
        print("using existing struct")
        return struct.id


def __getLevel(levelJSON, structureID):
    name = levelJSON["FriendlyName"]
    capacity = levelJSON["Capacity"]

    level = session.query(StructureLevel).filter(StructureLevel.name == name,
                                                 StructureLevel.capacity == capacity,
                                                 StructureLevel.structure == structureID).one_or_none()

    if not level:
        l = StructureLevel(name=name, capacity=capacity, structure=structureID)
        session.add(l)
        session.commit()
        return l.id
    else:
        return level.id
