import pandas as pd
import gmplot

import math
import numpy

RSSI_RANGE = 90
REAL_MAX_RSSI = 48 # experimentally obtained value
REAL_MIN_RSSI = REAL_MAX_RSSI-RSSI_RANGE # -42 # tipical values range rssi [-120, -30]
MIN_RSSI = 0 # goal
MAX_RSSI = REAL_MAX_RSSI+abs(REAL_MIN_RSSI)

def get_gw_max_dist(dev_lats, dev_lons, gw_lats, gw_lons):
	# approximate maximum gataway covarage area
	rest_lats = [x-y for x,y in zip(dev_lats, gw_lats)]
	rest_lons = [x-y for x,y in zip(dev_lons, gw_lons)]
	sq_lats = [x**2 for x in rest_lats]
	sq_lons = [x**2 for x in rest_lons]
	sq_sum = [x+y for x,y in zip(sq_lats, sq_lons)]
	sqrt_res = [math.sqrt(x) for x in sq_sum]

	return max(sqrt_res)

raw_data = pd.read_csv("lca_data.csv")

# Store our latitude, longitude ...
dev_lats = raw_data["dev_latitude"]
dev_lons = raw_data["dev_longitude"]
rssi = raw_data['rssi']
gw_lats = raw_data['gw_latitude']
gw_lons = raw_data['gw_longitude']

max_dist = get_gw_max_dist(dev_lats, dev_lons, gw_lats, gw_lons)

# apox zoom value using linear interpolaion
# TODO: make approximation more global (this one was done based on local scale values)
aprox_zoom = round(17 - (max_dist-0.0014458727468248552)*(17-11)/(0.1831712819958427-0.0014458727468248552))

# set focus on the gw
# TODO: consider multiple gws
gmap = gmplot.GoogleMapPlotter(float(gw_lats[1]), float(gw_lons[1]), aprox_zoom)
gmap.apikey = "AIzaSyAwNrwJLFQwoqfmcn6EBHEsyXZI1ngAXDs"

# size = aprox value. It will allways be near the gw coverage border
gmap.scatter_point(39.993396, -0.068703, '#888888', size = int(max_dist*110000), marker = False)

# normalized rssi values, that is, in range [0, MAX_RSSI]
rssi_norm = [x+abs(REAL_MIN_RSSI) for x in rssi]

# gmap.heatmap(lats, lons)

# Overlay device positions and its signal intensities onto the map
# Draw lines from device locataions to the gw location
for i in range(len(rssi)):
	color_r_8 = hex(math.floor((int(rssi_norm[i])/MAX_RSSI)*255))
	color_b_8 = hex(math.floor(255-(int(rssi_norm[i])/MAX_RSSI)*255))
	gmap.scatter_point(dev_lats[i], dev_lons[i], '#'+color_r_8[2:]+'00'+color_b_8[2:], size = 10, marker = False)
	gmap.plot([dev_lats[i], gw_lats[i]], [dev_lons[i], gw_lons[i]], 'cornflowerblue', edge_width = 2.5)

# gmap.heatmap_weighted(lats, lons, rssi)

# Generate the heatmap into an HTML file
gmap.draw("coverage_map.html")
