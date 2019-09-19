import sys, os, re
import time
from flask import Flask, render_template, request
from pymongo import MongoClient
from bson import json_util
import config
import json

from elasticsearch import Elasticsearch
#elastic = Elasticsearch(config.ELASTIC_URL)
elastic = Elasticsearch()

# Process Elasticsearch hits and return flights records
def process_search(results):
  records = []
  total = 0
  if results['hits'] and results['hits']['hits']:
    total = results['hits']['total']['value']
    hits = results['hits']['hits']
    for hit in hits:
      record = hit['_source']
      records.append(record)

  print('Total:'+ str(total) )     
  return records, total

# Calculate offsets for fetching lists of flights from MongoDB
def get_navigation_offsets(offset1, offset2, increment):
  offsets = {}
  offsets['Previous'] = {'top_offset': max(offset2 - increment, 0), 
 'bottom_offset': max(offset1 - increment, 0)} # Don't go < 0
 
  offsets['Next'] = {'top_offset': offset2 + increment, 'bottom_offset': 
  offset1 + increment}
  return offsets

# Strip the existing start and end parameters from the query string
def strip_place(url):
  try:
    p = re.match('(.+)&start=.+&end=.+', url).group(1)
  except AttributeError as e:
    return url
  return p

# Set up Flask and Mongo
app = Flask(__name__)
client = MongoClient() 

# Controller: Fetch a flight and display it
@app.route("/on_time_performance")
def on_time_performance():
  
  carrier = request.args.get('Carrier')
  flight_date = request.args.get('FlightDate')
  flight_num = request.args.get('FlightNum')
 
  
  flight = client.agile_data_science.on_time_performance.find_one({
    'Carrier': carrier,
    'FlightDate': flight_date,
    'FlightNum': int(flight_num)
  })
  return render_template('flight.html', flight=flight, carrier=carrier,flight_date=flight_date, flight_num=flight_num)

# Controller: Fetch all flights between cities on a given day and display them
@app.route("/flights/<origin>/<dest>/<flight_date>")
def list_flights(origin, dest, flight_date):
  
  start = request.args.get('start') or 0
  start = int(start)
  end = request.args.get('end') or config.RECORDS_PER_PAGE
  end = int(end)
  width = end - start
  
  nav_offsets = get_navigation_offsets(start, end, config.RECORDS_PER_PAGE)
  
  flights = client.agile_data_science.on_time_performance.find(
    {
      'Origin': origin,
      'Dest': dest,
      'FlightDate': flight_date
    },
    sort = [
      ('DepTime', 1),
      ('ArrTime', 1)
    ]
  )
  flight_count = flights.count()
  flights = flights.skip(start).limit(width)
    
  return render_template(
    'flights.html', 
    flights=flights, 
    flight_date=flight_date, 
    flight_count=flight_count,
    nav_path=request.path,
    nav_offsets=nav_offsets
    )

@app.route("/flights/search")
@app.route("/flights/search/")
def search_flights():
  
  # Search parameters
  carrier = request.args.get('Carrier')
  flight_date = request.args.get('FlightDate')
  origin = request.args.get('Origin')
  dest = request.args.get('Dest')
  tail_number = request.args.get('TailNum')
  flight_number = request.args.get('FlightNum')
  
  # Pagination parameters
  start = request.args.get('start') or 0
  start = int(start)
  end = request.args.get('end') or config.RECORDS_PER_PAGE
  end = int(end)
  
  print(request.args)
  # Navigation path and offset setup
  nav_path = strip_place(request.url)
  nav_offsets = get_navigation_offsets(start, end, config.RECORDS_PER_PAGE)
  
  # Build the base of our Elasticsearch query
  query = {
    'query': {
      'bool': {
        'must': []}
    },
   # 'sort': [
   #   {'FlightDate': {'order': 'asc', 'ignore_unmapped' : True} },
   #   {'DepTime': {'order': 'asc', 'ignore_unmapped' : True} },
   #   {'Carrier': {'order': 'asc', 'ignore_unmapped' : True} },
   #   {'FlightNum': {'order': 'asc', 'ignore_unmapped' : True} },
   #   '_score'
   # ],
    'from': start,
    'size': config.RECORDS_PER_PAGE
  }
  
  # Add any search parameters present
  if carrier:
    query['query']['bool']['must'].append({'match': {'Carrier': carrier}})
  if flight_date:
    query['query']['bool']['must'].append({'match': {'FlightDate': flight_date}})
  if origin: 
    query['query']['bool']['must'].append({'match': {'Origin': origin}})
  if dest: 
    query['query']['bool']['must'].append({'match': {'Dest': dest}})
  if tail_number: 
    query['query']['bool']['must'].append({'match': {'TailNum': tail_number}})
  if flight_number: 
    query['query']['bool']['must'].append({'match': {'FlightNum': int(flight_number)}})
  
  # Query Elasticsearch, process to get records and count
  print("QUERY")
  print(carrier, flight_date, origin, dest, tail_number, flight_number)
  print(json.dumps(query))
  results = elastic.search(index='agile_data_science',body=query)
  flights, flight_count = process_search(results)
  
  # Persist search parameters in the form template
  return render_template(
    'search.html', 
    flights=flights, 
    flight_date=flight_date, 
    flight_count=flight_count,
    nav_path=nav_path,
    nav_offsets=nav_offsets,
    carrier=carrier,
    origin=origin,
    dest=dest,
    tail_number=tail_number,
    flight_number=flight_number
    ,query=request.url
    )

if __name__ == "__main__":
  app.run(debug=True)

