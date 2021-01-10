# Import dependencies
import numpy as np
import pandas as pd
import datetime as dt
import collections

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# create an engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table

Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"please choose one of the next routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2010-01-01<br/>"
        f"/api/v1.0/2010-01-01/2017-08-23<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query
    max_date = dt.datetime(2017, 8, 23)
    min_date = dt.datetime(2016, 8, 23)

    precip_score = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date <= max_date).filter(Measurement.date >= min_date).all()
    
    #close session
    session.close()

    # empty list
    all_prcp = []
    # create a loop
    for date, prcp in  precip_score:
        precipitation = {}
        precipitation["date"] = date
        precipitation["prcp"] = prcp
        all_prcp.append(precipitation)

    #return Json
    return jsonify(all_prcp)

# declare stations 
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #make a query
    stati = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    query = session.query(*stati).all()
    #close session
    session.close()
    #empty list
    stations = []
    #loop
    for station,name,lat,lon,el in query:
        station_dic = {}
        station_dic["Station"] = station
        station_dic["Name"] = name
        station_dic["Lat"] = lat
        station_dic["Lon"] = lon
        station_dic["Elevation"] = el
        #append the list
        stations.append(station_dic)
    #return jason
    return jsonify(stations)

# declare tobs function 

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
   #Query the dates and temperature observations of the most active station for the last year of data.
    max_date = dt.datetime(2017, 8, 23)
    min_date = dt.datetime(2016, 8, 23)
    #query and filter
    temp_ = session.query(Measurement.date, Measurement.tobs, Measurement.station, Measurement.id).\
    filter(Measurement.date <= max_date).filter(Measurement.date >= min_date).\
        group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).all()
        #append the result in a list
    result = list(np.ravel(temp_))
    #return Json
    return jsonify(result)
    
#declare star funtion 
@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # query and filter
    query = session.query(func.min(Measurement.tobs),\
         func.avg(Measurement.tobs),\
              func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    #close the session
    session.close()
    #declare an empty list
    tobs_list = []
    #loop, declare and fill a dictionary
    for min,avg,max in query:
        tobsd = {}
        tobsd["Min"] = min
        tobsd["Average"] = avg
        tobsd["Max"] = max
        #append the list
        tobs_list.append(tobsd)
    #return Json
    return jsonify(tobs_list)

#declare start_end funtion 
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #query and filter
    query = session.query(func.min(Measurement.tobs),\
         func.avg(Measurement.tobs),\
              func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    session.close()
    #loop, declare and fill a dictionary
    tobs_list2 = []
    for min,avg,max in query:
        tobsd2 = {}
        tobsd2["Min"] = min
        tobsd2["Average"] = avg
        tobsd2["Max"] = max
        #append the list
        tobs_list2.append(tobsd2)
    #return jason 
    return jsonify(tobs_list2)

if __name__ == '__main__':
    app.run(debug=False)
