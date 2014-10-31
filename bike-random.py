
import numpy
import random
import math
import urllib2
import urllib
import datetime
import json
import csv
import sys
import os

import numpy as np
import pandas as pd
import random
import xlsxwriter

Nodes = pd.read_excel("Common/Nodes_Capacities_and_Locations.xlsx")
del Nodes['Time']
del Nodes['Date']
Nodes = Nodes.values
Nodes = np.delete(Nodes,0,0)
for n in Nodes:
    if n[3] == 'Iron' or n[3] == 'Iron ':
        n[3] = 2
        
Distance = pd.read_excel("Common/Nodes_Car_Walking_Distance.xlsx")
index = Distance.index
Distance = Distance.values
ind1 = []
for i in range(len(index)):
    ind1.append([i+1,index[i].split(',')])
    ind1[i][1][0] = float(ind1[i][1][0])
    ind1[i][1][1] = float(ind1[i][1][1])
del index

Time = pd.read_excel("Common/Nodes_Car_Walking_Time.xlsx")
index = Time.index
Time = Time.values
ind2 = []
for i in range(len(index)):
    ind2.append([i+1,index[i].split(',')])
    ind2[i][1][0] = float(ind2[i][1][0])
    ind2[i][1][1] = float(ind2[i][1][1])
del index


for n in Nodes:
    for i in ind1:
        if i[1][0] == n[1] and i[1][1] == n[2]:
            n[0] = i[0]
            
N = []
for i in range(1,len(Nodes)+1):
    for j in range(len(Nodes)):
        if Nodes[j][0] == i:
            N.append(list(Nodes[j]))
Nodes = N
Nodes = np.array(Nodes)

n,n = np.shape(Time)
Time_Car = np.zeros((n,n))
Time_Walking = np.zeros((n,n))
for i in range(n):
    for j in range(n):
        if i == j:
            pass
        else:
            data = Time[i,j].split(',')
            Time_Car[i,j] = float(data[0].split('=')[1])
            Time_Walking[i,j] = float(data[1].split('=')[1])
            
n,n = np.shape(Distance)
Distance_Car = np.zeros((n,n))
Distance_Walking = np.zeros((n,n))
for i in range(n):
    for j in range(n):
        if i == j:
            pass
        else:
            data = Distance[i,j].split(',')
            Distance_Car[i,j] = float(data[0].split('=')[1])
            Distance_Walking[i,j] = float(data[1].split('=')[1])

try:
	stations = json.load(open("station-list.csv", "r+")) 
except:
	stations = []

if len(stations) <= 0: 
	# load stations from API
	url = "http://localhost:8080/otp/routers/default/bike_rental"
	req = urllib2.Request(url, None, {'Accept':'application/json'}) 
	res = urllib2.urlopen(req)
	response = res.read()

	stations = json.loads(response)

	if len(stations) > 0: 
		json.dump(stations, open("station-list.csv", "w+"))


		
class BikeTest(object):

	def __init__(self, stations, vehicle_capacity=10):
		# row#, lat, long, capacity
		self.stations = stations
		self.vehicle_capacity = vehicle_capacity		
		
	def random(self, lower=0, upper=1):
		raise NotImplementedError
		
	def get_stations(self, nodes, hubs, hub_capacity):

		self.nodes = nodes
		self.hubs = hubs
		self.hub_capacity = hub_capacity
		
		sample = []

		racks = random.sample(range(0,len(self.stations)), nodes)
		hubs = [racks[x] for x in random.sample(range(0,nodes), hubs)]
	
		current = 0
		for s in racks:
	
			station = self.stations[s]
			
			lower = 0
			upper = 1
			i = 0
			while True:
				bikes = self.random(lower, upper)

				if bikes+current > (len(hubs) * hub_capacity): 
					# continue but exponentially back off the upper limit so we eventually can stop trying
					i += 1
					try:
						upper -= float(upper) * 1.0/(2.0**i)
					except:
						i = sys.maxint
					if i >= 100: break
					continue # get another sample
				else: break
				
			if bikes > station[3]: bikes = station[3]
			current += bikes
								
			if s in hubs: sample.append( {'rack':s, 'x': station[1], 'y': station[2], 'bikes': bikes, 'spaces':hub_capacity, 'hub': True } )
			else: sample.append( {'rack':s, 'x': station[1], 'y': station[2], 'bikes': bikes, 'spaces':station[3], 'hub': False } )
		
		self.sample = sample
		return sample
		
	def optimize(self, stations):
		
		empty = [x for x in stations if x['bikes'] <= 0]
		nonempty = [x for x in stations if x['bikes'] > 0]
		
		while len(empty) > 0:
			work = False
			for s in nonempty:
				if s['bikes'] <= 1: continue # dont process nodes with only 1 bike
				work = True
				try:
					row = empty.pop(0)
				except:
					row = None
				if row is None: break				
				
				pct = int(s['bikes']/2)
				if pct <= 0:
					empty.push(row)
					continue
				
				if pct > row['spaces']: pct = row['spaces']
				s['bikes'] -= pct								
				row['bikes'] = pct
				
			if work is False: break
		
		return stations

	def write_file(self, file, sample):
		fd = open(file, "wb")
		
		bikewriter = csv.writer(fd, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

		for row in sample:
			bikewriter.writerow( [ row['x'], row['y'], row['bikes'], row['spaces'], row['hub'] ] )

		fd.close()
		
	def write_sheet(self, workbook):		
		worksheet = workbook.add_worksheet()
		worksheet.name = str(len(workbook.worksheets()))
		worksheet.write_row(0,0,['Nodes',self.nodes])
		
		R = [x for x in self.sample if x['hub'] is not True]
		H = sorted([x for x in self.sample if x['hub'] is True], cmp=lambda x,y: cmp(x['rack'], y['rack']))
		
		worksheet.write_row(1,0,['Hubs',len(H)])
		worksheet.write_row(1,2,[x['rack'] for x in H])
		worksheet.write_row(2,0,['Racks',len(R)])		
		worksheet.write_row(3,0,['Hub Capacity',self.hub_capacity])
		worksheet.write_row(4,0,['Total Number of Bikes',sum([x['bikes'] for x in self.sample])])
		worksheet.write_row(5,0,['Vehicle Capacity',self.vehicle_capacity])
		
		N = []
		for h in H:
			N.append(h)
		for r in R:
			N.append(r)
		N = sorted(N, cmp=lambda x,y: cmp(x['rack'], y['rack']))
		T_V = np.zeros((len(N),len(N)))
		
		worksheet.write(7,0,'SL No.') # sample id # (1-# of nodes in sample)		
		worksheet.write(8,0,'Node') # node id (the node index that sample[id] references
		worksheet.write(9,0,'Capacity') # the node's capacity
		
		# write all 3 rows at once
		for k in range(len(N)):
			worksheet.write_column(7,k+1,[k+1,N[k]['rack'],N[k]['spaces']]) # sl no, node id, node capacity

		"""
		C = []
		for n in N:
			if n in H:
				C.append(test_cases[i][3])
			else:
				C.append(Nodes[n-1][3])
				
		[I,O] = generate_scenarios(N,np.array(C),test_cases[i][4],H)
		"""
		
		# write the # of bikes at each node
		worksheet.write(10,0,'Inventory')
		worksheet.write_row(10,1,[x['bikes'] for x in N])
		
		# (Not used)
		worksheet.write(11,0,'PreProcessed')
		#worksheet.write_row(11,1,O)
		
		# sum of bike inventory
		worksheet.write_row(12,0,['Bikes in System',np.sum([x['bikes'] for x in N])])
		
		"""
		if np.sum(O) < 0:
			worksheet.write_row(13,0,['Surplus Bikes',-1*np.sum(O)])
		else:
			worksheet.write_row(13,0,['Bike Deficits',np.sum(O)])
		"""
		
		# Matrix holding the vehicle times between nodes [x,y]
		worksheet.write(15,0,'Vehicle Time')
		T_V = np.zeros((len(N),len(N)))
		for k in range(len(N)):
			for l in range(len(N)):
				if k != l:
					T_V[k,l] = Time_Car[N[k]['rack']-1,N[l]['rack']-1]
		for k in range(len(N)):
			worksheet.write_row(16+k,0,T_V[k])
				
		# Matrix holding the walking times between nodes (+ vehicle time)
		worksheet.write(16+len(N)+1,0,'Walking Time')
		T_W = np.zeros((len(N),len(N)))
		for k in range(len(N)):
			for l in range(len(N)):
				if k != l:
					T_W[k,l] = Time_Walking[N[k]['rack']-1,N[l]['rack']-1]
		for k in range(len(N)):
			worksheet.write_row(16+len(N)+2+k,0,T_W[k])	
		
		
class BikeUniform(BikeTest):

	# even distribution
	def random(self, lower=0, upper=1):  #nodes, hubs, hub_capacity):
		""" even/uniform distribution """
		
		r = random.uniform(0, upper)

		return int(r * self.hub_capacity)

	def get_stations(self, nodes, hubs, hub_capacity):
		
		sample = super(BikeUniform, self).get_stations(nodes, hubs, hub_capacity)
		
		# use strategies to fill empty holes 
		sample = self.optimize(sample)
				
		return sample

class BikeNormal(BikeTest):
		
	def random(self, lower=0, upper=1):
	
		return int(math.fabs(random.normalvariate(lower, upper)) * self.hub_capacity)

	def get_stations(self, nodes, hubs, hub_capacity):
		""" inventories from mu=0 std dev=1 """
		
		sample = super(BikeNormal, self).get_stations(nodes, hubs, hub_capacity)
		
		# use strategies to fill empty holes 
		sample = self.optimize(sample)		
		
		return sample

class BikeSparse(BikeTest):
		
	def random(self, lower, upper):
		""" >= 50% of racks has 0 inventory """
		if int(random.normalvariate(0, 1)) == 0: return 0
		
		return random.randint(0, int(upper * self.hub_capacity))
		
	def get_stations(self, nodes, hubs, hub_capacity):
		
		sample = super(BikeSparse, self).get_stations(nodes, hubs, hub_capacity)

		# guarantee sparse?
		
		return sample
		
class BikeDense(BikeTest):
	""" all racks must have at least 1 bike """
		
	def random(self, lower=1, upper=1):
		return random.randint(int(lower * (self.hub_capacity/2)), int(upper * (self.hub_capacity)) )

	def get_stations(self, nodes, hubs, hub_capacity):
		
		sample = super(BikeDense, self).get_stations(nodes, hubs, hub_capacity)

		# use strategies to fill empty holes 
		sample = self.optimize(sample)
		
		return sample

class BikeViolateCapacity(BikeTest):
	""" Randomly select num_violate racks and generate greater inventory than vehicle_capacity """
		
	def random(self, lower, upper):
	
		return int(math.fabs(random.normalvariate(0, 1)) * self.hub_capacity)
			
	def get_stations(self, nodes, hubs, hub_capacity, num_violate=1):
		
		sample = super(BikeViolateCapacity, self).get_stations(nodes, hubs, hub_capacity)

		# use strategies to fill empty holes 
		sample = self.optimize(sample)

		hubs = [x for x in sample if x['hub'] == 'true']
		
		while num_violate > 0:
			id = random.randint(0, len(sample)-1)
			if sample[id]['rack'] in hubs: continue
			
			sample[id]['bikes'] = self.vehicle_capacity * 2
			
			num_violate -= 1
					
		return sample
		

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

		
workbooks = {}

for i, row in enumerate(cases):
	
	# nodes_hubs
	key = "_%d_%d" % (row[0], row[1])
	if "uniform%s" % key not in workbooks: workbooks["uniform%s" % key] = xlsxwriter.Workbook("uniform%s" % key + ".xlsx")
	if "normal%s" % key not in workbooks: workbooks["normal%s" % key] = xlsxwriter.Workbook("normal%s" % key + ".xlsx")
	if "dense%s" % key not in workbooks: workbooks["dense%s" % key] = xlsxwriter.Workbook("dense%s" % key + ".xlsx")
	if "sparse%s" % key not in workbooks: workbooks["sparse%s" % key] = xlsxwriter.Workbook("sparse%s" % key + ".xlsx")
	if "capacity%s" % key not in workbooks: workbooks["capacity%s" % key] = xlsxwriter.Workbook("capacity%s" % key + ".xlsx")
	
	b = BikeUniform(Nodes)
	s = b.get_stations(row[0], row[1], row[2])
	#b.write_file("uniform-case%d.csv" % i, s)
	b.write_sheet(workbooks["uniform%s" % key])
	
	b = BikeNormal(Nodes)
	s = b.get_stations(row[0], row[1], row[2])
	#b.write_file("normal-case%d.csv" % i, s)
	b.write_sheet(workbooks["normal%s" % key])
	
	b = BikeSparse(Nodes)
	s = b.get_stations(row[0], row[1], row[2])
	#b.write_file("sparse-case%d.csv" % i, s)
	b.write_sheet(workbooks["sparse%s" % key])
	
	b = BikeDense(Nodes)
	s = b.get_stations(row[0], row[1], row[2])
	#b.write_file("dense-case%d.csv" % i, s)
	b.write_sheet(workbooks["dense%s" % key])
	
	b = BikeViolateCapacity(Nodes)
	s = b.get_stations(row[0], row[1], row[2])
	#b.write_file("capacity-case%d.csv" % i, s)
	b.write_sheet(workbooks["capacity%s" % key])
	
	
