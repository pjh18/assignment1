import os
import uuid
import json
import redis
from flask import Flask, render_template, redirect, request, url_for, make_response
import boto
import time
import requests

if 'VCAP_SERVICES' in os.environ:
    VCAP_SERVICES = json.loads(os.environ['VCAP_SERVICES'])
    CREDENTIALS = VCAP_SERVICES["rediscloud"][0]["credentials"]
    r = redis.Redis(host=CREDENTIALS["hostname"], port=CREDENTIALS["port"], password=CREDENTIALS["password"])
else:
    r = redis.Redis(host='redis-11762.c14.us-east-1-2.ec2.cloud.redislabs.com', port='11762', password='nope')

app = Flask(__name__)
my_uuid = str(uuid.uuid1())
BLUE = "#777799"
GREEN = "#99CC99"

COLOR = BLUE
	
@app.route('/')
def mainmenu():

    return """
    <html lang="en">
	<head>
	<title>Main Page</title>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
	<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
	</head>	
	
    <body bgcolor="{}">
    
    <div class="container">
        <div class="jumbotron">
            <h1>Main Menu</h1>
			<p>Hi, I'm GUID:<br/>{}<br/></p>
        </div>
 
        <div class="row marketing">
            <div class="col-lg-6">
                <p><a href="/pitemp">View Current Conditions at the Raspberry Pi</a></p>
                <p></p>
 
                <p><a href="/outtemp">View Current Outside Conditions</a></p>
                <p></p>
             </div>
        </div>
        <footer class="footer">
            <p>&copy; Compuglobalhypermeganet 2017</p>
        </footer>
    </div>    
    <font size=1><a href="/dumpsurveys">Dump Results</a></font>
	</center>
    </body>
    </html>
    """.format(COLOR,my_uuid,)
	
@app.route('/pitemp')
def pitemp():
	global r
	epoch_time = int(time.time()) - 1
	epoch_key = "assignment" + str(epoch_time)
	#for eachresult in r.keys(epoch_key):
	current_value = r.hget(epoch_key,'photoresistor')
	
	return """
	<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">

	<head>
	<title>Refresh Example</title>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
	<meta http-equiv="refresh" content="1" />
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
	<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
	</head>

	<body>
		<div class="container">
			<div class="jumbotron">
				<h1>{} degrees C</h1>
				<p>Conditions  at the Raspberry Pi as of {}</p>
			</div>
			<p><a href="/">Home</a>
		</div>
	</body>

	</html>
	""".format(current_value, time.ctime(epoch_time))

@app.route('/outtemp')
def outtemp():
	data = requests.get('http://api.wunderground.com/api/d4fbad1a5750256c/geolookup/conditions/q/Australia/Canberra.json').json()
	location = data['location']['city']
	temp_c = data['current_observation']['temp_c']
	current_weather = data['current_observation']['weather']
	#print "Current temperature in %s is: %s C" % (location, temp_c)
	data1 = requests.get('http://api.wunderground.com/api/d4fbad1a5750256c/forecast/q/Australia/Canberra.json').json()
	
	
	return """
	<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">

	<head>
	<title>Refresh Example</title>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
	<meta http-equiv="refresh" content="1" />
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
	<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
	</head>

	<body>
		<div class="container">
			<div class="jumbotron">
				<h1>{} degrees C and {}</h1>
				<p>Current conditions in {}</p>
			</div>
			<p><a href="/">Home</a>
		</div>
	</body>

	</html>
	""".format(temp_c, current_weather, location)
	
@app.route('/dumpsurveys')	
def dumpsurveys():

    global r
    response = "Dump of all results so far<br>"
    response += "-----------------------------<br>"
    print "Reading back from Redis"
    for eachsurvey in r.keys('assignment*'):
		#response += "Time: " + r.hget(eachsurvey,'epoch_key') + "<br>"
		response += "Photoresistor Value : " + r.hget(eachsurvey,'photoresistor') + "<br>"
		response += "-----------------------------<br>"

    return response	

if __name__ == "__main__":
	app.run(debug=False,host='0.0.0.0', port=int(os.getenv('PORT', '5000')))
