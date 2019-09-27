import math
import urllib.request
import json
'''
map, street, node, car
'''
class Node:
    lat=0.00
    lon=0.00
    type=""
    def __init__(self, la, lo, t):  #lat, lon geo coordinates, edge node type: "START" or "END" of road
        self.lat=la
        self.lon=lo
        self.type=t

class Car: #might add type and subsequent mpg and maybe estimate time in congestion radius
    lat = 0.00
    lon = 0.00
    type=''
    def __init__(self, la, lo, ty):
        self.lat=la
        self.lon=lo
        self.type=ty

class Street:
    start=None
    end=None
    length=0.0 #miles
    avgspeed=0.0
    passingcount=0 #int number of cars that pass street in 24 hrs. If -1 it means data's unavailable
    addfee=0.00 #additional fee costs to flat rate
    name=""
    cRank=0.0
    def __init__(self, na, st, en, av, le, pv, fe):  #start and end edge nodes,
        self.name=na
        self.start=st
        self.end=en
        self.avgspeed=av
        self.length=le
        self.passingcount=pv
        self.addfee=fe
    def __str__(self):
        string=self.name+", avg. car speed: "+str(self.avgspeed)+"mph, street length: "+str(self.length)+" mi, passing car count per day: "+str(self.passingcount)+" Street fee (to do): $"+str(self.addfee)+" Congestion Rank: #"+str(self.cRank)
        return string

class shapeArea:
    type="" #rectangle, square, circle
    centerlat=0.0
    centerlon=0.0
    radius=0.0 #-1.00 for these values if not need for specific type
    width=0.0
    height=0.0
    flatfee=0.0
    def __init__(self, la, lo, ra, wi, he, ff):
        self.centerlat=la
        self.centerlon=lo
        self.radius=ra
        self.width=wi
        self.height=he
        self.flatfee=ff

class Map:
    streetarray=[]
    congestionAreas=[] #where pricing occurs. Could be list specific streets too
    def __init__(self, sa, cpa):  # street array
        self.streetarray=sa
        self.congestionArea=cpa

count=0
streets = []
pricingareas = []
with urllib.request.urlopen("https://data.cityofchicago.org/resource/sxs8-h27x.json") as url:  # link of new data
    data = json.loads(url.read().decode())
    # keys=["segmentid", "street", "_direction", "_fromst", "_tost", "_length", "_strheading", "start_lon", "_lif_lat", "_lit_lon", "_lit_lat", "_traffic", "_last_updt"]
    # https://data.cityofchicago.org/api/assets/3F039704-BD76-4E6E-8E42-5F2BB01F0AF8 for data info

    # if -1 speed then look at https://data.cityofchicago.org/resource/chicago-traffic-tracker-historical-congestion-estimates-by-segment.json data and grab it. if still -1 set street speed to 0
    # "https://data.cityofchicago.org/resource/n4j6-wkkf.json" <-historic 2018- data 2nd link to find
    # [{"last_update": "2018-05-03T12:01:31.000", "segment_id": "1308", "bus_count": "0", "msg_count": "0", "traffic": "-1"}
    # {"time":"2019-06-30T17:40:32.000","segment_id":"1151","speed":"21","street":"Harlem","direction":"NB","from_street":"Madison","to_street":"Chicago","length":"1.00590031083","street_heading":"S","comments":"Outside City Limits","bus_count":"1","message_count":"7","hour":"17","day_of_week":"1","month":"6","record_id":"1151-201906302240","start_latitude":"41.8796992839","start_longitude":"-87.8045488066","end_latitude":"41.8942683013","end_longitude":"-87.8051007941","start_location":{"type":"Point","coordinates":[-87.8045488066,41.8796992839]},"end_location":{"type":"Point","coordinates":[-87.8051007941,41.8942683013]},":@computed_region_6mkv_f3dw":"26615"}
    #grab needed data
    for d in data:  # "segmentid"
        stnode = Node(float(d["start_latitude"]), float(d["start_longitude"]), "START")  # la, lo, t
        ennode = Node(float(d["end_latitude"]), float(d["end_longitude"]), "END")
        shortestdist=math.inf
        closestval = None
        name = ""
        # provide a close approximation to the actual number of vehicles passing through a given location on an average weekday
        # FIND CLOSEST STREET FOR GEO COORD ON THE PASSING VOLUME DATA
        with urllib.request.urlopen("https://data.cityofchicago.org/resource/4ndg-wq3w.json") as url2:
            '''
            https://data.cityofchicago.org/resource/4ndg-wq3w.json
              {
              "total_passing_vehicle_volume" : "10800",
              "street" : "Cottage Grove Ave",
              "traffic_volume_count_location_address" : "4107 South",
              "date_of_count" : 1143705600,
              "latitude" : "41.820171",
              "location" : {
                "latitude" : "41.820171",
                "needs_recoding" : false,
                "longitude" : "-87.606798"
              },
              "id" : "14",
              "vehicle_volume_by_each_direction_of_traffic" : "North Bound: 5600 / South Bound: 5200",
              "longitude" : "-87.606798"
            '''
            # Haversine formula method
            data2 = json.loads(url2.read().decode())
            for d2 in data2:
                # start pts here
                R = 6372800  # Earth radius in meters
                phi1 = math.radians(stnode.lat)
                phi2 = math.radians(float(d2["latitude"]))
                dphi = math.radians(float(d2["latitude"]) - stnode.lat)
                dlambda = math.radians(float(d2["longitude"]) - stnode.lon)
                a = math.sin(dphi / 2) ** 2 + \
                    math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
                pdstart = 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                pdstart = pdstart * 0.000621371192  # convert to miles
                # end points here
                phi1 = math.radians(ennode.lat)
                phi2 = math.radians(float(d2["latitude"]))
                dphi = math.radians(float(d2["latitude"]) - ennode.lat)
                dlambda = math.radians(float(d2["longitude"]) - ennode.lon)
                a = math.sin(dphi / 2) ** 2 + \
                    math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
                pdend = 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                pdend = pdend * 0.000621371192  # convert to miles
                pdvalue = 0.0
                if pdend <= pdstart:
                    pdvalue = pdend
                else:
                    pdvalue = pdstart
                if pdvalue < shortestdist:
                    shortestdist=pdvalue
                    name = d2["traffic_volume_count_location_address"]
                    closestval = d2["total_passing_vehicle_volume"] #pass count provide a close approximation to the actual number of vehicles passing through a given location on an average weekday
        street = Street(name, stnode, ennode, float(d["speed"]), float(d["length"]), float(closestval), 0.00)  # st, en, av, le, pv, fee):
        if street.avgspeed < 0.00:
            street.avgspeed = 0.00
            # find backup data for speed
            with urllib.request.urlopen("https://data.cityofchicago.org/resource/n4j6-wkkf.json") as url3:  # link of new data
                data3 = json.loads(url3.read().decode())
                for d3 in data3:
                    if d3["segmentid"] == d["segment_id"]:
                        street.avgspeed = float(d3["_traffic"])
        streets.append(street)

#now that data's grabbed we can calculate total congestion pricing revenue over a WEEKDAY period in the city
TOTALREVENUE=0.00 #per day
#establish hour by hour Downstate Illinois Non-Interstate (Urban) Traffic patterns into an array -> pg 8 on https://idot.illinois.gov/Assets/uploads/files/Transportation-System/Reports/OP&P/Travel-Stats/2017ITS%20Traffic%20Patterns.pdf
xtimes=[] ##by hour
for i in range(1, 25): #25 not inclusive
    xtimes.append(i)
#establish pricing areas here
ydata=[.9,.6,.4,.5,1.1,2.4,4.3,5.7,5.6,5.2,5.2,5.4,6.0,6.1,6.5,7.3,7.7,7.5,6.4,5.0,3.5,2.8,2.4,1.5] #by % of total traffic, which we assume correlates to traffic on the road
for street in streets:
    # if still -1.0 we can estimate daily car speed
    if street.avgspeed < 0.00:
        '''
        Reasoning for using 30.0 mph: "The state has a statutory speed limit of 30 miles per hour on urban streets, so not on expressway streets, and it's the default speed limit for the state of Illinois. As long as the speed limit is 30 miles per hour, you don't have to post signs," said Luann Hamilton, CDOT Deputy Commissioner, Division of Project Development.
        '''
        avgcrosstime = 1.0 / (30.0 / street.length)  # avg time for a car to cross the road (in hrs) 30.0 mph is max legal speed in urban road so that can be the base speed
        avgcardensity = sum(ydata) / len(ydata)
        #find average passing car count and speed for street of same length
        sumpassing=0.0
        sumspeed=0.0
        sumcount=0.0
        for st in streets:
            if st.avgspeed>=0.0 and st.name==street.name and st.passingcount==street.passingcount and st.length==street.length: #use speed of a street with same attributes
                street.avgspeed=st.avgspeed
            elif round(st.length, 1)==round(street.length, 1): #approximate street length comparison
                #sumpassing+=st.passingcount
                sumspeed+=st.avgspeed
                sumcount+=1.0
        if street.avgspeed<0.0:
            if sumcount>0:
                street.avgspeed=sumspeed/sumcount #if still cant find road speed use the avg speed of all roads of the same length
            '''avgpassing=sumpassing/sumcount
            passingcarratio=street.passingcount/avgpassing #lesser than average car count-> greater avg speed
            for h in range(len(ydata)):
                adjtime = (ydata[h] / avgcardensity) * avgcrosstime * passingcarratio  # adjust car cross time based on the (car density at time t/average density) * average time to cross the road
                street.avgspeed += (street.length / adjtime)  # speed=street length (distance in mi)/time (hr)
            street.avgspeed = street.avgspeed / 24.0  # estimated avg car speed for the day in mi/hr'''
sortBySpeed=sorted(streets, key=lambda x: x.avgspeed)
sortByCarCount=sorted(streets, key=lambda x: x.passingcount, reverse=True)
print("Start Lat: "+str(streets[0].start.lat)+", Start Lon: "+str(streets[0].start.lon))
print("end lat: "+str(streets[0].end.lat)+", end Lon: "+str(streets[0].end.lon))
sim = Map(streets, [])
print(str(len(sim.streetarray)))
finalTaxSort=[]
for t in sim.streetarray:
    carCountRank=0.0
    speedRank=0.0
    for index, st in enumerate(sortBySpeed):
        if st.start.lat==t.start.lat and st.start.lon==t.start.lon and st.end.lat==t.start.lat and st.end.lon==t.start.lon:
            break
        speedRank+=1.0
    for index, st in enumerate(sortByCarCount):
        if st.start.lat==t.start.lat and st.start.lon==t.start.lon and st.end.lat==t.start.lat and st.end.lon==t.start.lon:
            break
        carCountRank+=1.0
    t.cRank=(speedRank+carCountRank)/2.0
    finalTaxSort.append(t)
    finalTaxSort = sorted(finalTaxSort, key=lambda x: x.cRank)
finalTaxSort = sorted(finalTaxSort, key=lambda x: x.cRank)
#1 base rate +1 + percentage rate increase by higher ranking
taxSize=len(sim.streetarray)*.1 #top 10% congested
for i in range(0, len(finalTaxSort)):
    if i<taxSize:
        finalTaxSort[i].addfee=1.00+0.005*(taxSize-i)
        finalTaxSort[i].addfee=round(finalTaxSort[i].addfee, 2)
        TOTALREVENUE=TOTALREVENUE+(finalTaxSort[i].addfee*finalTaxSort[i].passingcount)
    print(str(finalTaxSort[i]))
    print("")
print(str(TOTALREVENUE))
