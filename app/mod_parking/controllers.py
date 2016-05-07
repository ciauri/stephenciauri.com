from flask import Blueprint, render_template, jsonify, request, Response
from urllib.request import urlopen
from app import db, app
from app.mod_parking.models import SpotCount, ParkingStructure, StructureLevel, alchemyencoder
from datetime import date, datetime
import json
import datetime
from enum import Enum


class QueryType(Enum):
    all = 0
    latest = 1

mod_parking = Blueprint('parking', __name__)


@mod_parking.route('/parking/counts', methods=['GET'])
def allCounts():
    return __buildJSON(QueryType.all)


@mod_parking.route('/parking/counts/latest', methods=['GET'])
def latestCounts():
    return __buildJSON(QueryType.latest)


def updateCounts():
    data = urlopen("https://webfarm.chapman.edu/parkingservice/parkingservice/counts").read().decode('utf8')
    jsonData = json.loads(data)

    for structure in jsonData["Structures"]:
        structureID = _getStructure(structure)
        for level in structure["Levels"]:
            levelID = __getLevel(level, structureID)
            count = level["CurrentCount"]
            c = SpotCount(count=count, level=levelID)
            db.session.add(c)

    db.session.commit()


def __buildJSON(type):
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
            if type is QueryType.all:
                counts = SpotCount.query.filter(SpotCount.level == level.id).all()
            elif type is QueryType.latest:
                counts = [
                    SpotCount.query.filter(SpotCount.level == level.id).order_by(SpotCount.timestamp.desc()).first()]
            else:
                counts = []

            for count in counts:
                jsonData["structures"][index]["levels"][levelIndex]["counts"].append({"count": count.count,
                                                                                      "timestamp": count.timestamp.isoformat()})
    return jsonify(**jsonData)


def _getStructure(structureJSON):
    name = structureJSON["Name"]
    lat = structureJSON["Latitude"]
    long = structureJSON["Longitude"]
    address = structureJSON["Address"]
    image = structureJSON["XhdpiDetailImage"]

    struct = db.session.query(ParkingStructure).filter(ParkingStructure.name == name,
                                                       ParkingStructure.latitude == lat,
                                                       ParkingStructure.longitude == long).one_or_none()

    if not struct:
        s = ParkingStructure(name=name, latitude=lat, longitude=long, address=address, image=image)
        db.session.add(s)
        db.session.commit()
        return s.id
    else:
        return struct.id


def __getLevel(levelJSON, structureID):
    name = levelJSON["FriendlyName"]
    capacity = levelJSON["Capacity"]

    level = db.session.query(StructureLevel).filter(StructureLevel.name == name,
                                                    StructureLevel.capacity == capacity,
                                                    StructureLevel.structure == structureID).one_or_none()

    if not level:
        l = StructureLevel(name=name, capacity=capacity, structure=structureID)
        db.session.add(l)
        db.session.commit()
        return l.id
    else:
        return level.id
