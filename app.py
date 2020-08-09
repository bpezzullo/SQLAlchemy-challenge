
import numpy as np

import datetime as dt
from datetime import datetime

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import pandas as pd
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/api/v1.0/")
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/Start date<br/>"
        f"/api/v1.0/Start date/end date"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a precipitation for the last 12 months"""
    # Design a query to retrieve the last 12 months of precipitation data and plot the results

    # Calculate the date 1 year from the last data point in the database
    data = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    last_date = datetime.strptime(data[0], '%Y-%m-%d') - dt.timedelta(days=365)

    # pull the data from that point (last_date)
    data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > last_date).all()

    session.close()

    # Create a dictionary from the row data and append to a dictionary of all the results
    results_list = []
    for date, prcp in data:
        Precipitation_dict = {}
        Precipitation_dict["Date"] = date
        Precipitation_dict["prcp"] = prcp
        results_list.append(Precipitation_dict)

    return jsonify(results_list)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations and activity"""

    # fine the stations and provide the results of how active they are.
    active = session.query(Measurement.station, func.count(Measurement.station))\
            .group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    session.close()

    # Convert list of tuples into normal list
    active_stations = list(np.ravel(active))

    return jsonify(active_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """return temperature observations"""

    # Find the most active station
    active = session.query(Measurement.station)\
            .group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()

    # find the last date in the database
    date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # subtract an year (365 days)
    last_date = datetime.strptime(date[0], '%Y-%m-%d') - dt.timedelta(days=365)

    # use the results to query the database for the min, max, and average
    sel = [Measurement.station, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs), func.count(Measurement.tobs)]
    tobs_results = session.query(*sel).filter(Measurement.station == active[0]).filter(Measurement.date > last_date).all()

    session.close()

    # Convert list of tuples into tobs list
    tobs = list(np.ravel(tobs_results))

    return jsonify(tobs)

@app.route("/api/v1.0/<start>", defaults={"end": None})
@app.route("/api/v1.0/<start>/<end>")
def vacation(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """return temperature information on the range provided"""
    # check the start date.  Is is a date and in the right format.
    try:
        valid_start_date = datetime.strptime(start, "%Y-%m-%d")
    except:
        # if not then the exception will be thrown.  Close the session and return
        session.close()
        return f"Invalid start date.  Please provide a date in the format YYYY-MM-DD"
    # do the same thing for the end date, but first check to see if there is an end date provided
    try:
        # IF end date is None then nothing was provided so use the last date of the database
        if end is None:
            last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
            end = last_date[0]

        # Verify the correct format
        valid_end_date = datetime.strptime(end, "%Y-%m-%d")

    except:
        # if not then the exception will be thrown.  Close the session and return
        session.close()
        return f"Invalid end date.  Please provide a date in the format YYYY-MM-DD or leave blank"

    # use the dates to pul the min, max and average dates for the timeperiod
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs), func.count(Measurement.tobs)]
    vac_results = session.query(*sel).filter(Measurement.date >= valid_start_date)\
        .filter(Measurement.date <= valid_end_date).all()

    session.close()

    # Convert list of tuples into vac list
    vac = list(np.ravel(vac_results))

    return jsonify(vac)

if __name__ == '__main__':
    app.run(debug=True)
