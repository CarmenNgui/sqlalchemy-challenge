import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

##Home page
##List all routes that are available

@app.route("/")
def home():
    """List all available api routes."""
    return (f"Welcome to the Surfs Up Weather API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/percipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/(Y-M-D)<br/>"
        f"/api/v1.0(start=Y-M-D)/(end=Y-M-D)<br/>"
    )

##Convert the query results to a dictionary using date as the key and prcp as the value.
##Return the JSON representation of your dictionary.
@app.route("/api/v1.0/percipitation")
def percipitation():

    # Query all Measurement
    results = session.query(Measurement).all()

    session.close()

    prcp_data = []
    for result in results:
            prcp_data_dict = {}
            prcp_data_dict["date"] = result.date
            prcp_data_dict["prcp"] = result.prcp
            prcp_data.append(prcp_data_dict)

    return jsonify(prcp_data)

##Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():

    # Query all stations
    results = session.query(Station.station).all()

    session.close()

    all_station = list(np.ravel(results))

    return jsonify(all_station)

##Query the dates and temperature observations of the most active station for the last year of data.
##Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def temperature():

	# Find last date in database then subtract one year
	Last_Year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

	# Query tempurature observations
	temperature_results = session.query(Measurement.tobs).filter(Measurement.date > Last_Year).all()
	
	session.close()

	temperature_list = list(np.ravel(temperature_results))

	# Jsonify summary
	return jsonify(temperature_list)

##Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
##When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
##When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>")
def startdate(start):
	# Set up for user to enter date
	Start_Date = dt.datetime.strptime(start,"%Y-%m-%d")

	# Query Min, Max, and Avg based on date
	summary_stats = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.round(func.avg(Measurement.tobs))).\
	filter(Measurement.date >= Start_Date).all()
	
	session.close() 
	
	summary = list(np.ravel(summary_stats))

	# Jsonify summary
	return jsonify(summary)

@app.route("/api/v1.0/<start>/<end>")
def dates(start,end):
	# Set up for user to enter dates 
	Start_Date = dt.datetime.strptime(start,"%Y-%m-%d")
	End_Date = dt.datetime.strptime(end,"%Y-%m-%d")

	# Query Min, Max, and Avg based on dates
	summary_stats = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.round(func.avg(Measurement.tobs))).\
	filter(Measurement.date.between(Start_Date,End_Date)).all()
	# Close the Query
	session.close()    
	
	summary = list(np.ravel(summary_stats))

	# Jsonify summary
	return jsonify(summary)

if __name__ == '__main__':
    app.run(debug=True)
