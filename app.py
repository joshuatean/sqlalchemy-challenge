import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, request

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurements = Base.classes.measurement
stns = Base.classes.station

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
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end</br>"
        f"Please note: Enter dates in the appropriate format: YYYY-MM-DD/YYYY-MM-DD"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation data for the past 12 months"""
    # Query precipitation for the past 12 months
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(measurements.date, measurements.prcp).\
                filter(measurements.date >= query_date).all()
    
    session.close()

    # Create a dictionary from the row data and append to a list of precipitation data
    prcp_data = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Return all stations in the DB
    results = session.query(stns.station).all()
    
    session.close()
    
    #Converting list of tuples into normal list
    all_stations = list(np.ravel(results))
    
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Find the date to get the previous 12 months of temperature data
    querytemp_date = dt.date(2017, 8, 18) - dt.timedelta(days=365)
    
    #Query of the most active station for the previous year of temperature data
    results = session.query(measurements.date, measurements.tobs).\
                filter(measurements.date >= querytemp_date, measurements.station == stns.station, stns.id == 6).all()
    
    session.close()
    
    # Create a dictionary from the row data and append to a list of temperature data
    tobs_data = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_data.append(tobs_dict)
       
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine) 
    # Convert supplied input to datetime format
    query_date = dt.datetime.strptime(start, '%Y-%m-%d').date()

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date."""

    # Query for min, average, and max temperature where query date is greater than or equal supplied date in URL
    start_data = session.query(func.min(measurements.tobs),func.avg(measurements.tobs),func.max(measurements.tobs)).\
        filter(func.strftime('%Y-%m-%d', measurements.date) >= query_date).all()
    
    session.close() 

    return (
        f"Temperature data from {start} to 2017-08-23:<br/>"
        f"Minimum temperature: {round(start_data[0][0], 1)} °C<br/>"
        f"Maximum temperature: {round(start_data[0][1], 1)} °C<br/>"
        f"Average temperature: {round(start_data[0][2], 1)} °C"
    )

@app.route("/api/v1.0/<start>/<end>")
def date_start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Convert supplied input to datetime format
    query_startdate = dt.datetime.strptime(start, '%Y-%m-%d').date()
    query_enddate = dt.datetime.strptime(end, '%Y-%m-%d').date()

    # Retrieve the temperature data between the query dates
    date_temp = session.query(func.min(measurements.tobs),func.avg(measurements.tobs),func.max(measurements.tobs)).\
                filter(func.strftime('%Y-%m-%d', measurements.date) >= query_startdate).\
                filter(func.strftime('%Y-%m-%d', measurements.date) <= query_enddate).all()
    
    # Close Session
    session.close()

    return (
        f"Temperature data from {start} to {end}:<br/>"
        f"Minimum temperature: {round(date_temp[0][0], 1)} °C<br/>"
        f"Maximum temperature: {round(date_temp[0][1], 1)} °C<br/>"
        f"Average temperature: {round(date_temp[0][2], 1)} °C"
    )

if __name__ == '__main__':
    app.run(debug=True)