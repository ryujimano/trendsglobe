import requests
from flask import Flask, render_template, request

try:
	import json
except ImportError:
	import simplejson as json

from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream

ACCESS_TOKEN = "<access_token>"
ACCESS_SECRET = "<access_secret>"
CONSUMER_KEY = "<consumer_key>"
CONSUMER_SECRET = "<consumer_secret>"

oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

twitter = Twitter(auth=oauth)

app = Flask(__name__)

#get coordinates for a given woeid using yql api
def getLocation(woeid):
	if not woeid:
		return
	url = "https://query.yahooapis.com/v1/public/yql?q=select+*+from+geo.places+where+woeid+=+%s&format=json"% woeid
	req = requests.get(url)
	locs = req.json()
	if locs["query"]["count"] == 0:   #check if there are any results
		return
	return [locs["query"]["results"]["place"]["centroid"]["latitude"], locs["query"]["results"]["place"]["centroid"]["longitude"]]


#called when app is run
@app.route('/')
def index():
	with open("static/locations.json") as f:
		for line in f:
			if (line == ""):
				initialSetup()   #setup json file if there is no content initially
				break
			else:
				break
	return render_template("index.html")   #display index.html


#setup of json file when app is launched and when refresh button is clicked
@app.route('/initialSetup', methods=["POST"])
def initialSetup():
	trends = twitter.trends.available()
	trendLocs = []
	idx = 0
	for trend in trends:
		idx += 1
		if idx == 1:
			continue
		loc = getLocation(trend["woeid"])
		trendLocs += (str(loc[0]), str(loc[1]), str(1))
	f = open("static/locations.json", "rb+")
	f.truncate()
	f.write("""[["trends", [%s]]]"""% (",".join(trendLocs)))
	f.close()
	return render_template("index.html")


if __name__ == "__main__":
	app.run()
