import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify, request, url_for


engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=False)

Base = automap_base()
Base.prepare(engine, reflect=True)
session = Session(engine)

Measurement = Base.classes.measurement
Station = Base.classes.station

measurements = session.query(Measurement).all()
query_stations = session.query(Station).all()

precipitations_list = {}
previous_year_tobs_list = {}
stations_list = {}

# Get precipitations_list
for m in measurements:
	precipitations_list[m.date] = m.prcp

# Get stations_list
for s in query_stations:
	# stations.append([s.station, s.name, s.latitude, s.longitude, s.elevation])
	stations_list[s.station] = [s.name, s.latitude, s.longitude, s.elevation]

# Get previous_year_tobs_list
most_recent_date = engine.execute('SELECT max(date) FROM measurement').first()[0]
most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')

start_date = most_recent_date - dt.timedelta(days = 365)

me_sel = [Measurement.date, Measurement.prcp, Measurement.station, Measurement.tobs]
previous_year_measurements = session.query(*me_sel).filter(Measurement.date > start_date).order_by(Measurement.date).all()

for m in previous_year_measurements:
	previous_year_tobs_list[m.date] = m.tobs

# Galculate min, avg, max temperatures
def calc_tobs_for_given_dates(start_date, end_date=None):
	calc_tobs = {}
	sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
	if end_date == None:	    
	    temps = session.query(*sel).filter(Measurement.date >= start_date).all()[0]
	else:
	    temps = session.query(*sel).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()[0]

	calc_tobs['tmin'] = temps[0]
	calc_tobs['tavg'] = temps[1]
	calc_tobs['tmax'] = temps[2]
	calc_tobs['start_date'] = start_date
	calc_tobs['end_date'] = end_date

	return calc_tobs

# from flask import Flask
app = Flask(__name__)


@app.route("/")
def Welcome():
    """List all available api routes."""
    return (
    	f"<h2>Welcome to Climate App api</h2>"
        f"<p>Available Routes:</p>"
        f"<p>/api/v1.0/precipitation, -- it returns daily precipitations in JSON format</p>"
        f"<p>/api/v1.0/stations,  -- it returns a list of weather stations </p>"
        f"<p>/api/v1.0/tobs, -- it returns dates and temperature observations from a year from the most recent data point in the data set</p>"
        f"<p>/api/v1.0/<start>, -- enter the start date after /, it return a list of the minimum temperature, the average temperature, and the max temperature for days after the given start date</p>"
        f"<p>/api/v1.0/<start>/<end>, -- enter the start date and end date, it returns a JSON list of the minimum temperature, the average temperature, and the max temperature for dates between the start date and the end date inclusive.</p>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """it returns daily precipitations in JSON format"""
    return jsonify(precipitations_list)

@app.route("/api/v1.0/stations")
def stations():
    """it returns daily precipitations in JSON format"""
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """it returns daily precipitations in JSON format"""
    return jsonify(previous_year_tobs_list)

@app.route("/api/v1.0/<start>")
def calc_temperatures(start):
    """it returns daily precipitations in JSON format"""
    calculated_tobs = calc_tobs_for_given_dates(start)
    return jsonify(calculated_tobs)

@app.route("/api/v1.0/<start>/<end>")
def calc_temperatures_with_end_date(start, end):
    """it returns daily precipitations in JSON format"""
    calculated_tobs_with_end_date = calc_tobs_for_given_dates(start, end)
    return jsonify(calculated_tobs_with_end_date)

if __name__ == "__main__":
    app.run(debug=True)