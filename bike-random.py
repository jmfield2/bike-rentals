
import random

import urllib2
import urllib
import datetime
import json
import csv
import sys
import os

stations = json.load(open("station-list.csv", "r+"))

if len(stations) <= 0: 
	# load stations from API
	url = "http://localhost:8080/otp/routers/default/bike_rental"
	req = urllib2.Request(url, None, {'Accept':'application/json'}) 
	res = urllib2.urlopen(req)
	response = res.read()

	stations = json.loads(response)

	if len(stations) > 0: 
		json.dump(stations, open("station-list.csv", "w+"))

class BikeTest():

	def __init__(stations, vehicle_capacity=10):
		self.stations = stations
		self.vehicle_capacity = vehicle_capacity
		
	# even distribution
	def generate_uniform(self, nodes, hubs, hub_capacity):
		""" even/uniform distribution """
		
		sample = []

		racks = random.sample(range(0,len(self.stations['stations'])), nodes)
		hubs = [racks[x] for x in random.sample(random.randint(0, nodes), hubs)]
	
		current = 0
		for s in racks:
	
			station = self.stations['stations'][s]
			
			bikes = random.uniform(0, hub_capacity)
			
			if bikes+current > nodes: bikes = nodes-current
			
			if bikes > station['spacesAvailable']: bikes = station['spacesAvailable']
			current += bikes
			
			if s in hubs: sample.append( {'x': station['x'], 'y': station['y'], 'bikes': bikes, 'spaces':hub_capacity, 'hub': "true" ] )
			else: sample.append( {'x': station['x'], 'y': station['y'], 'bikes': bikes, 'spaces':station['spacesAvailable'], 'hub': "false" ] )
		
		#assert( current == nodes )
		
		return sample
		
	def generate_normal(self, nodes, hubs, hub_capacity):
		""" inventories from mu=0 std dev=1 """
		
		sample = []

		racks = random.sample(range(0,len(self.stations['stations'])), nodes)
		hubs = [racks[x] for x in random.sample(random.randint(0, nodes), hubs)]
	
		current = 0
		for s in racks:
	
			station = self.stations['stations'][s]
			
			bikes = math.abs(random.normalvariate(0, 1)) * hub_capacity
			
			if bikes+current > nodes: bikes = nodes-current
			
			if bikes > station['spacesAvailable']: bikes = station['spacesAvailable']
			current += bikes
			
			if s in hubs: sample.append( {'x': station['x'], 'y': station['y'], 'bikes': bikes, 'spaces':hub_capacity, 'hub': "true" ] )
			else: sample.append( {'x': station['x'], 'y': station['y'], 'bikes': bikes, 'spaces':station['spacesAvailable'], 'hub': "false" ] )
		
		#assert( current == nodes )
		
		return sample
		
	def generate_sparse(self, nodes, hubs, hub_capacity):
		""" >= 50% of racks has 0 inventory """
		
		sample = []
		racks = random.sample(range(0,len(self.stations['stations'])), nodes)
		hubs = [racks[x] for x in random.sample(random.randint(0, nodes), hubs)]
	
		current = 0
		for s in racks:
	
			station = self.stations['stations'][s]
			
			bikes = random.randint(0, hub_capacity)
			
			if bikes+current > nodes: bikes = nodes-current
			
			if bikes > station['spacesAvailable']: bikes = station['spacesAvailable']
			current += bikes
			
			if s in hubs: sample.append( {'x': station['x'], 'y': station['y'], 'bikes': bikes, 'spaces':hub_capacity, 'hub': "true" ] )
			else: sample.append( {'x': station['x'], 'y': station['y'], 'bikes': bikes, 'spaces':station['spacesAvailable'], 'hub': "false" ] )
		
		#assert( current == nodes )
		
		return sample
		
	def generate_dense(self, nodes, hubs, hub_capacity):
		""" all racks must have at least 1 bike """
		
		sample = []
		racks = random.sample(range(0,len(self.stations['stations'])), nodes)
		hubs = [racks[x] for x in random.sample(random.randint(0, nodes), hubs)]
	
		current = 0
		for s in racks:
	
			station = self.stations['stations'][s]
			
			bikes = random.randint(1, hub_capacity/2)
			
			if bikes+current > nodes: bikes = nodes-current
			
			if bikes > station['spacesAvailable']: bikes = station['spacesAvailable']
			current += bikes
			
			if s in hubs: sample.append( {'x': station['x'], 'y': station['y'], 'bikes': bikes, 'spaces':hub_capacity, 'hub': "true" ] )
			else: sample.append( {'x': station['x'], 'y': station['y'], 'bikes': bikes, 'spaces':station['spacesAvailable'], 'hub': "false" ] )
		
		#assert( current == nodes )
		
		return sample
		
	def generate_violate_capacity(self, nodes, hubs, hub_capacity, num_violate=1):
		""" Randomly select num_violate racks and generate greater inventory than vehicle_capacity """
		
		sample = []
		racks = random.sample(range(0,len(self.stations['stations'])), nodes)
		hubs = [racks[x] for x in random.sample(random.randint(0, nodes), hubs)]
	
		current = 0
		for s in racks:
	
			station = self.stations['stations'][s]
			
			bikes = math.abs(random.normalvariate(0, 1)) * hub_capacity
			
			if bikes+current > nodes: bikes = nodes-current
			
			if bikes > station['spacesAvailable']: bikes = station['spacesAvailable']
			current += bikes
			
			if s in hubs: sample.append( {'rack': s, 'x': station['x'], 'y': station['y'], 'bikes': bikes, 'spaces':hub_capacity, 'hub': "true" ] )
			else: sample.append( {'rack': s, 'x': station['x'], 'y': station['y'], 'bikes': bikes, 'spaces':station['spacesAvailable'], 'hub': "false" ] )

		while num_violate > 0:
			id = random.randint(0, len(sample))
			if sample[id]['rack'] in hubs: continue
			
			sample[id]['bikes'] = self.vehicle_capacity * 2
			
			num_violate -= 1
			
		#assert( current == nodes )
		
		return sample
		
	def write_file(self, file, sample):
		fd = open(file, "wb")
		
		bikewriter = csv.writer(fd, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

		for row in sample:
			bikewriter.writerow( [ row['x'], row['y'], row['bikes'], row['spaces'], row['hub'] ] )

		fd.close()
		
	
b = BikeTest(stations)

# nodes, hubs, hub_capacity
cases = [ (10, 1, 10), (10, 1, 20), 
		  
		  (20, 1, 10), (20, 1, 20),
		  (20, 2, 10), (20, 2, 20),
		  
		  (30, 2, 10), (30, 2, 20),		  
		  (30, 3, 10), (30, 3, 20),
		  
		  (40, 2, 10), (40, 2, 20),		  
		  (40, 4, 10), (40, 4, 20),
		  
		  (50, 3, 10), (50, 3, 20),		  
		  (50, 5, 10), (50, 5, 20),
		  
		  (60, 4, 10), (60, 4, 20),		  
		  (60, 6, 10), (60, 6, 20),
		  
		  (70, 4, 10), (70, 4, 20),		  
		  (70, 7, 10), (70, 7, 20),
		  
		  (80, 5, 10), (80, 5, 20),
		  (80, 8, 10), (80, 8, 20),
		  
		  (90, 6, 10), (90, 6, 20),
		  (90, 9, 10), (90, 9, 20),
		  
		  (100, 6, 10), (100, 6, 20),
		  (100, 10, 10), (100, 10, 20),
		  
		  (110, 7, 10), (110, 7, 20),
		  (110, 11, 10), (110, 11, 20),
		  
		  (120, 8, 10), (120, 8, 20),
		  (120, 12, 10), (120, 12, 20),
		  		  
		  (130, 8, 10), (130, 8, 20),
		  (130, 13, 10), (130, 13, 20),
		  
		  (140, 9, 10), (140, 9, 20),
		  (140, 14, 10), (140, 14, 10),
		  
		  (147, 10, 10), (147, 10, 20),
		  (147, 15, 10), (147, 15, 20),
		  		  
		]
		
for i in cases:
	row = cases[i]
	
	s = b.generate_normal(row[0], row[1], row[2])
	b.write_file("normal-case%d.csv" % i, s)

	s = b.generate_sparse(row[0], row[1], row[2])
	b.write_file("sparse-case%d.csv" % i, s)

	s = b.generate_dense(row[0], row[1], row[2])
	b.write_file("demse-case%d.csv" % i, s)

	s = b.generate_violate_capacity(row[0], row[1], row[2])
	b.write_file("capacity-case%d.csv" % i, s)
	
sys.exit(0)

# 10 nodes, 1 hub, 9 racks, 10 capacity, 10 total
fd = open("bike-case1.csv", "wb")
bikewriter = csv.writer(fd, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

racks = random.sample(range(0,len(stations['stations'])), 10)
hub = racks[random.randint(0, 9)]

total = 10
current = 0
for s in racks:
	
	station = stations['stations'][s]
	
	bikes = random.randint(0, total-1)		
	if bikes+current > total: bikes = total-current
	
	if bikes > station['spacesAvailable']: bikes = station['spacesAvailable']
	current += bikes
	
	if s == hub: bikewriter.writerow( [ station['x'], station['y'], bikes, total, "true" ] )
	else: bikewriter.writerow( [ station['x'], station['y'], bikes, station['spacesAvailable'], "false" ] )

# 10 nodes, 1 hub, 9 racks, 15 capacity, 15 total
fd = open("bike-case2.csv", "wb")
bikewriter = csv.writer(fd, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

racks = random.sample(range(0,len(stations['stations'])), 10)
hub = racks[random.randint(0, 9)]

total = 15
current = 0
for s in racks:
	
	station = stations['stations'][s]
	
	bikes = random.randint(0, total-1)	
	if bikes+current > total: bikes = total-current
	
	if bikes > station['spacesAvailable']: bikes = station['spacesAvailable']	
	current += bikes
	
	if s == hub: bikewriter.writerow( [ station['x'], station['y'], bikes, total, "true" ] )
	else: bikewriter.writerow( [ station['x'], station['y'], bikes, station['spacesAvailable'], "false" ] )

# case 3-4

# 20 nodes, 1 hub, 19 racks, 10 capacity, 10 total
fd = open("bike-case3.csv", "wb")
bikewriter = csv.writer(fd, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

racks = random.sample(range(0,len(stations['stations'])), 20)
hub = racks[random.randint(0, 19)]

total = 10
current = 0
for s in racks:
	
	station = stations['stations'][s]
	
	bikes = random.randint(0, total-1)	
	if bikes+current > total: bikes = total-current
	
	if bikes > station['spacesAvailable']: bikes = station['spacesAvailable']
	current += bikes
	
	if s == hub: bikewriter.writerow( [ station['x'], station['y'], bikes, total, "true" ] )
	else: bikewriter.writerow( [ station['x'], station['y'], bikes, station['spacesAvailable'], "false" ] )

# 20 nodes, 1 hub, 19 racks, 15 capacity, 15 total
fd = open("bike-case4.csv", "wb")
bikewriter = csv.writer(fd, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

racks = random.sample(range(0,len(stations['stations'])), 20)
hub = racks[random.randint(0, 19)]

total = 15
current = 0
for s in racks:
	
	station = stations['stations'][s]
	
	bikes = random.randint(0, total-1)	
	if bikes+current > total: bikes = total-current
	
	if bikes > station['spacesAvailable']: bikes = station['spacesAvailable']
	current += bikes
	
	if s == hub: bikewriter.writerow( [ station['x'], station['y'], bikes, total, "true" ] )
	else: bikewriter.writerow( [ station['x'], station['y'], bikes, station['spacesAvailable'], "false" ] )

