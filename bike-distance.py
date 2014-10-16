
import urllib2
import urllib
import datetime
import json
import csv
import sys
import os

fd = open("bike-stations-distance.csv", "wb")
bikewriter = csv.writer(fd, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
fd = open("bike-stations-speed.csv", "wb")
bikewriter2 = csv.writer(fd, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

# load stations from API
url = "http://localhost:8080/otp/routers/default/bike_rental"
req = urllib2.Request(url, None, {'Accept':'application/json'}) 
res = urllib2.urlopen(req)
response = res.read()

stations = json.loads(response)

# header row of coordinates
row_distance = [""]
row_speed = [""]

for s in stations['stations']: 
	row_distance.append( "%s,%s" % (s['y'], s['x']) )
	row_speed.append( "%s,%s" % (s['y'], s['x']) )

bikewriter.writerow(row_distance)
bikewriter2.writerow(row_speed)

_cached = {}
cnt = 0

_cached_loaded = False

if _cached_loaded: _cached = json.load(open("bike-cache.dat", "rb"))

from collections import OrderedDict

"""
import glob
g=glob.glob('tmp/*')
print len(g)
for file in g:
	fp=open(file, "r")
	resp = json.loads(fp.read())
	fp.close()
	
	# debugOutput totalTime
	# requestParameters

	d = OrderedDict()
	d["fromPlace"] = resp['requestParameters']['fromPlace']
	d["toPlace"] = resp['requestParameters']['toPlace']
	d["time"] = resp['requestParameters']['time']
	d["date"] = resp['requestParameters']['date']
	d["mode"] = resp['requestParameters']['mode']
	d["maxWalkDistance"] = resp['requestParameters']['maxWalkDistance']
	d["arriveBy"] = "false"
	d["showIntermediateStops"] = "false"
			
	_cached["%s-%s" % (d['fromPlace'], d['toPlace'])] = resp
	
print len(_cached)
fp=open("bike-cache.dat", "wb")
fp.write(json.dumps(_cached))
fp.close()
sys.exit(0)
"""


for s in stations['stations']:
	row_distance = ["%s,%s" % (s['y'], s['x'])]
	row_speed = ["%s,%s" % (s['y'], s['x'])]
	
	for y in stations['stations']:
	
		if s == y: 
			row_distance.append("-") 
			row_speed.append("-")
			continue
	
		d = OrderedDict()
		d["fromPlace"] = "%s,%s" % (s['y'], s['x'])
		d["toPlace"] = "%s,%s" % (y['y'], y['x'])
		d["time"] = datetime.datetime.strftime(datetime.datetime.now(), "%H:%M%p")
		d["date"] = datetime.datetime.strftime(datetime.datetime.now(), "%m/%d/%Y")
		d["mode"] = "CAR,TRANSIT,WALK"
		d["maxWalkDistance"] = 750
		d["arriveBy"] = "false"
		d["showIntermediateStops"] = "false"
		
		v = []
		url = "http://localhost:8080/otp/routers/default/plan?"
		for x in d: v.append( "%s=%s" % (x,urllib.quote( str(d[x])) ) )
		url += '&'.join(v)
		
		key = "%s-%s" % (d['fromPlace'], d['toPlace'])
		key2 = "%s-%s" % (d['toPlace'], d['fromPlace'])
		
		if key in _cached: 
			response = _cached[key]
		elif key2 in _cached:
			response = _cached[key2]
		else:
			if _cached_loaded:
				print url
				raise Exception("Should be cached")
			
			req = urllib2.Request(url, None, {'Accept':'application/json'}) 
			res = urllib2.urlopen(req)
			response = json.loads(res.read())
		
			_cached[url] = response
			
		if 'error' in response: 
			row_distance.append("N/A")
			row_speed.append("N/A")
		else:		
			best_time = sys.maxint
			best = {}
			
			for i in response['plan']['itineraries']:
				local = {"walk":{'dist':0, 'time':0}, 'car':{'dist':0, 'time':0}}
				overall_time = 0
				
				for l in i['legs']:					
					m = l['mode'].lower()
					if m == "bus": m = "car" # GRR
					if m not in local: raise Exception("Unknown mode %s" % l['mode'])
										
					local[m]['dist'] += l['distance']
					local[m]['time'] += l['duration']
					overall_time += l['duration']
					
				if overall_time < best_time: 
					best_time = overall_time
					best = local
			
			row_distance.append(', '.join(["%s=%d" % (x.upper(), best[x]['dist']) for x in best]))
			row_speed.append(', '.join(["%s=%d" % (x.upper(), best[x]['time']) for x in best]))
			
	
	cnt += 1
	print "%d of %d" % (cnt, len(stations['stations']))
		
	bikewriter.writerow(row_distance)
	bikewriter2.writerow(row_speed)
	
fp=open("bike-cache.dat", "wb")
fp.write(json.dumps(_cached))
fp.close()
