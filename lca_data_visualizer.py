import pandas as pd
import gmplot

import math
import numpy
from statistics import mean 

RSSI_RANGE = 90 # taken from the datasheet
REAL_MAX_RSSI = 50 # experimentally obtained value
REAL_MIN_RSSI = REAL_MAX_RSSI-RSSI_RANGE # -42 # tipical values range rssi [-120, -30]
NORM_MIN_RSSI = 0 # goal
NORM_MAX_RSSI = REAL_MAX_RSSI+abs(REAL_MIN_RSSI)

GW_COVERAGE_SIZE_COEF = 110000 # obtained empirically

def get_gw_max_dist(dev_lats, dev_lons, gw_lats, gw_lons):
	# approximate maximum gataway covarage area
	sq_lats = [(x-y)**2 for x,y in zip(dev_lats, gw_lats)]
	sq_lons = [(x-y)**2 for x,y in zip(dev_lons, gw_lons)]
	sqrt_res = [math.sqrt(x+y) for x,y in zip(sq_lats, sq_lons)]

	return max(sqrt_res)

raw_data = pd.read_csv("lca_data.csv")

# Store latitude, longitude ...
dev_lats = raw_data['dev_latitude']
dev_lons = raw_data['dev_longitude']
rssi = raw_data['rssi']
gw_lats = raw_data['gw_latitude']
gw_lons = raw_data['gw_longitude']

max_dist = get_gw_max_dist(dev_lats, dev_lons, gw_lats, gw_lons)

# apox zoom value using linear interpolaion
# TODO: make approximation more global (this one was done based on local scale values)
aprox_zoom = round(17 - (max_dist-0.0014458727468248552)*(17-11)/(0.1831712819958427-0.0014458727468248552))

# set focus on the mean point among gws
gmap = gmplot.GoogleMapPlotter(float(mean(gw_lats)), float(mean(gw_lons)), aprox_zoom)
# put your google api key for clean map representation
gmap.apikey = "AIzaSyAwNrwJLFQwoqfmcn6EBHEsyXZI1ngAXDs"

# size = aprox value. It will allways be near the gw coverage border
gmap.scatter_point(float(gw_lats[0]), float(gw_lons[0]), '#888888', size = int(max_dist*GW_COVERAGE_SIZE_COEF), marker = False)

# normalized rssi values, that is, in range [0, MAX_RSSI]
rssi_norm = [x+abs(REAL_MIN_RSSI) for x in rssi]

gmap.heatmap(dev_lats, dev_lons)

# Overlay device positions and its signal intensities onto the map
# Draw lines from device locataions to the corresponding gw location
for i in range(len(rssi)):
	color_r_8 = hex(math.floor((int(rssi_norm[i])/NORM_MAX_RSSI)*255))
	color_b_8 = hex(math.floor(255-(int(rssi_norm[i])/NORM_MAX_RSSI)*255))
	gmap.scatter_point(dev_lats[i], dev_lons[i], '#'+color_r_8[2:]+'00'+color_b_8[2:], size = 10, marker = False)
	gmap.plot([dev_lats[i], gw_lats[i]], [dev_lons[i], gw_lons[i]], 'cornflowerblue', edge_width = 2.5)


# Generate the heatmap into an HTML file
gmap.draw("coverage_map.html")
