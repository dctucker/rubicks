#!/usr/local/bin/python2.7

from PIL import Image
import records
import nvector as nv
from visual import *

def keydown(evt):
	global iata_code, iata_label, total_distance
	k = evt.key

	if k == 'esc':
		exit()
	elif k == 'left':
		earth_frame.rotate( angle=radians(10), axis=(0,1,0) )
	elif k == 'right':
		earth_frame.rotate( angle=radians(-10), axis=(0,1,0) )
	elif k == 'down':
		earth_frame.rotate( angle=radians(-10), axis=(1,0,0) )
	elif k == 'up':
		earth_frame.rotate( angle=radians(10), axis=(1,0,0) )
	elif (k >= 'A' and k <= 'Z') or (k >='a' and k <='z'):
		iata_code += k
		iata_label.visible = True
		iata_label.text = iata_code
	elif k == '\n':
		total_distance = 0
		iata_label.text = ''
		iata_label.visible = False
		load_iata()
	else:
		print vars(evt)

def keyup(evt):
	k = evt.key
	if k in ('left','right'):
		camera.d_theta_x = 0
	elif k in ('up','down'):
		camera.d_theta_y = 0
	elif k in ('page up','page down'):
		camera.d_theta_z = 0

def mousemove(evt):
	return
	pick = scene.mouse.pick
	if pick in shapes:
		if hasattr(pick, 'iata_code'):
			for s in shapes:
				if hasattr(s, 'iata_code'):
					s.opacity = 0.3
			pick.opacity = 1.0

def click(evt):
	global iata_code, shapes, total_distance
	pick = scene.mouse.pick
	if pick in shapes:
		if hasattr(pick, 'iata_code'):
			iata_code = pick.iata_code
			total_distance += pick.distance
			load_iata()


def poi( latitude, longitude, altitude=0 ):
	lat =  radians(latitude)
	lon = -radians(longitude)
	#curvature = 1.0 / sqrt( 1 - eccentricity ** 2 * sin( latitude ) )
	curv = 0
	pos = vector( \
		(curv + e_radius + altitude) * cos( lat ) * cos( lon ), \
		(curv * (1 - eccentricity ** 2) + e_radius + altitude) * sin( lat ), \
		(curv + e_radius + altitude) * cos( lat ) * sin( lon ) \
	)
	vector.longitude = longitude
	vector.latitude  = latitude
	vector.altitude  = altitude
	return pos

def poi_sphere( latitude, longitude, color=(1,1,0) ):
	s = sphere( pos=poi(latitude, longitude), color=color, radius=50, opacity=0.3 )
	s.longitude = longitude
	s.latitude = latitude
	return s

def arc( poi1, poi2 ):
	points = []
	frame_E = nv.FrameE(a=e_radius * 1000, f=0)
	gp1 = frame_E.GeoPoint(latitude=poi1.latitude, longitude=poi1.longitude, degrees=True)
	gp2 = frame_E.GeoPoint(latitude=poi2.latitude, longitude=poi2.longitude, degrees=True)

	distance, _azia, _azib = gp1.distance_and_azimuth(gp2)
	distance = max(1, int(distance/50000))
	path = nv.GeoPath(gp1, gp2)
	for i in range(0, distance+1):
		geo = path.interpolate((1.0/distance)*i).to_geo_point()
		points += [ poi( geo.latitude_deg, geo.longitude_deg, 10 ) ]
	return points

def load_iata():
	global shapes, iata_code, routes, routes_index, source_airport, source, total_distance
	print total_distance

	code = ''+iata_code
	iata_code = ''
	source_airport = db.query("""
		SELECT latitude, longitude, iata_code, country_name
		FROM airports
		WHERE iata_code='%s'
	""" % (code))[0]

	routes = db.query("""
		SELECT airports.latitude, airports.longitude, airports.country_name, airports.iata_code, airports.city_name,
			MIN(airline_code) AS airline_code,
			atan2( airports.latitude - source.latitude, airports.longitude - source.longitude ) AS direction,
			haversine( source.latitude, source.longitude, airports.latitude, airports.longitude ) as distance
		FROM routes
		INNER JOIN airports ON airports.iata_code = routes.destination_airport_code
		INNER JOIN airports AS source ON source.iata_code = routes.source_airport_code
		WHERE routes.source_airport_code='%s'
		-- AND airline_code='DL'
		GROUP BY airports.latitude, airports.longitude, airports.country_name, airports.iata_code, airports.city_name,
			source.latitude, source.longitude
		ORDER BY direction DESC
	""" % (code)).all()

	for s in shapes:
		s.visible = False
		del s

	shapes = []
	source = poi_sphere(source_airport.latitude, source_airport.longitude)
	source.iata_code = code
	shapes += [source]
	routes_index = 0

def load_next_route():
	global shapes, source_airport, routes, routes_index, source

	if routes_index >= len(routes):
		return

	r = routes[ routes_index ]
	routes_index += 1

	if source_airport.country_name != r.country_name:
		color=(1,1,1)
	else:
		color=(0.6,0.6,0.6)

	if r.airline_code == 'DL':
		color = (1,0,0)
	elif r.airline_code in ('AA','UA'):
		color = (0.2,0.6,1)
	elif r.airline_code == 'WN':
		color = (1.0,0.8,0.15)

	dest = poi_sphere( r.latitude, r.longitude, color=color )
	dest.iata_code = r.iata_code
	dest.distance = r.distance
	waypoints = points( pos=arc( source, dest ), color=color )
	text = r.iata_code
	try:
		text += ' - ' + r.city_name.encode('ascii')
	except UnicodeDecodeError:
		pass
	dest_label = label( pos=dest.pos, text=text, box=False, line=False, opacity=0, yoffset=10, space=20 )
	#print r.latitude, r.longitude
	shapes += [ dest, waypoints, dest_label ]

# CONSTANTS
sun_radius = 695700
e_distance = 149597870.7
e_radius = 6371
moon_earth_distance = 384400
moon_radius = 1738

# SCENE
scene = display( title="Earth", width=1200, height=800, background=(0.0,0.0,0.0) )
scene.center = (0,0,0)
scene.range = (2*e_radius, 2*e_radius, 2*e_radius)
#scene.autoscale = False
scene.lights = [
	distant_light(direction=(0, 0, 1), color=color.gray(0.6)),
	#distant_light(direction=(0,  3, -3), color=color.gray(0.9)),
	#local_light(  pos=(0, 0, 5), color=color.gray(0.3)),
	#local_light(  pos=(3, -1, 3), color=color.gray(0.3)),
	#local_light(  pos=(-3, -1, 3), color=color.gray(0.3)),
	local_light(  pos=(e_distance, 0, 0), color=color.gray(1.0)),
	local_light(  pos=(-e_distance, 0, 0), color=color.gray(0.5))
]
scene.bind('keydown', keydown)
scene.bind('keyup'  , keyup)
scene.bind('mousemove', mousemove)
scene.bind('click', click)


# TEXTURES
im = Image.open('moonmap4k.jpg')
im = im.resize((4096,2048), Image.ANTIALIAS)
moon_tex = materials.texture(data=im, mapping="spherical")

im = Image.open('PathfinderMap.jpg')
#im = im.resize((2048,2048), Image.ANTIALIAS)
earth_tex = materials.texture(data=im, mapping="spherical")

earth_frame = frame()
#sun = sphere( pos=(e_distance,0,0), radius=sun_radius, material=materials.emissive, color=(1,1,1) )
moon = sphere( frame=earth_frame, pos=(moon_earth_distance, 0, 0), radius=moon_radius, material=moon_tex )
earth = sphere( frame=earth_frame, pos=(0,0,0), radius=e_radius, material=earth_tex )
earth.rotate( angle=radians(90), axis=(0,1,0), origin=earth.pos )
flattening = 0  # 1.0 / 298.257223563
eccentricity = 2 * flattening - flattening ** 2

total_distance = 0
routes = []
routes_index = 0
shapes = []
iata_code = 'SAN'
source_airport = {}
source = {}
iata_label = label(pos=scene.up, visible=False)

db = records.Database('mysql+pymysql://casey@localhost:3306/lang')
load_iata()

while 1:
	rate(60)
	load_next_route()

