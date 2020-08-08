
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

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"localhost:5000/api/v1.0/precipitation<br/>"
        f"localhost:5000/api/v1.0/stations<br/>"
        f"localhost:5000/api/v1.0/tobs"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a precipitation for the last 12 months"""
    # Design a query to retrieve the last 12 months of precipitation data and plot the results

    # Calculate the date 1 year ago from the last data point in the database
    data = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    last_date = datetime.strptime(data[0], '%Y-%m-%d') - dt.timedelta(days=365)

    data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > last_date).all()

    session.close()

        # Create a dictionary from the row data and append to a list of all_passengers
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

    """return date on the most active station"""

    active = session.query(Measurement.station)\
            .group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()

    date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    last_date = datetime.strptime(date[0], '%Y-%m-%d') - dt.timedelta(days=365)

    sel = [Measurement.station, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs), func.count(Measurement.tobs)]
    tobs_results = session.query(*sel).filter(Measurement.station == active[0]).filter(Measurement.date > last_date).all()

    session.close()

    # Convert list of tuples into normal list
    tobs = list(np.ravel(tobs_results))

    return jsonify(tobs)

if __name__ == '__main__':
    app.run(debug=True)
