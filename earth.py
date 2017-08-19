#!/usr/local/bin/python2.7

from PIL import Image
import records
import nvector as nv
from visual import *

def keydown(evt):
	global iata_code
	k = evt.key

	if k == 'esc':
		exit()
	elif k == 'left':
		camera.d_theta_x = radians(-2)
	elif k == 'right':
		camera.d_theta_x = radians(2)
	elif k == 'down':
		camera.d_theta_y = radians(2)
	elif k == 'up':
		camera.d_theta_y = radians(-2)
	elif k == 'page up':
		camera.d_theta_z = radians(-0.5)
	elif k == 'page down':
		camera.d_theta_z = radians(0.5)
	elif (k >= 'A' and k <= 'Z') or (k >='a' and k <='z'):
		iata_code += k
	elif k == '\n':
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
	pick = scene.mouse.pick


sun_radius = 695700
e_distance = 149597870.7
e_radius = 6371
moon_earth_distance = 384400

scene = display( title="Earth", width=1200, height=800, background=(0.0,0.0,0.0) )
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
#background = box( pos=(0,0,-10), size=(20,20,0.01), color=(0.2,0.1,0.0), material=materials.wood )
scene.bind('keydown', keydown)
scene.bind('keyup'  , keyup)
scene.bind('mousemove', mousemove)

#sun = sphere( pos=(e_distance,0,0), radius=sun_radius, material=materials.emissive, color=(1,1,1) )
im = Image.open('moonmap4k.jpg')
im = im.resize((4096,2048), Image.ANTIALIAS)
moon_tex = materials.texture(data=im, mapping="spherical")
moon = sphere( pos=(moon_earth_distance, 0, 0), radius=1738, material=moon_tex )

im = Image.open('PathfinderMap.jpg')
#im = im.resize((2048,2048), Image.ANTIALIAS)
earth_tex = materials.texture(data=im, mapping="spherical")
earth = sphere( pos=(0,0,0), radius=e_radius, material=earth_tex )
earth.rotate( angle=radians(90), axis=(0,1,0), origin=earth.pos )
flattening = 0 #1/298.257223563
eccentricity = 2 * flattening - flattening ** 2

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
	distance = int(distance/50000)
	path = nv.GeoPath(gp1, gp2)
	for i in range(0, distance+1):
		geo = path.interpolate((1.0/distance)*i).to_geo_point()
		points += [ poi( geo.latitude_deg, geo.longitude_deg, 10 ) ]
	return points

db = records.Database('mysql://localhost/lang')

def load_iata():
	global shapes, iata_code
	code = ''+iata_code
	iata_code = ''
	source_airport = db.query("""
		SELECT latitude, longitude, iata_code, country_name
		FROM airports
		WHERE iata_code='%s'
	""" % (code))[0]

	routes = db.query("""
		SELECT DISTINCT latitude, longitude, country_name, iata_code, airports.city_name
		FROM routes
		INNER JOIN airports on airports.iata_code = routes.destination_airport_code
		WHERE source_airport_code='%s'
		-- AND airline_code='DL'
	""" % (code))

	for s in shapes:
		s.visible = False
		del s

	shapes = []
	source = poi_sphere(source_airport.latitude, source_airport.longitude)
	shapes += [source]
	for r in routes:
		if source_airport.country_name != r.country_name:
			color=(1,1,0)
		else:
			color=(0,1,1)
		dest = poi_sphere( r.latitude, r.longitude, color=color )
		waypoints = points( pos=arc( source, dest ), color=color )
		dest_label = label( pos=dest.pos, text=r.city_name+" - "+r.iata_code, box=False, line=False, opacity=0, yoffset=10, space=20 )
		print r.latitude, r.longitude
		shapes += [ dest, waypoints, dest_label ]
	return shapes


scene.center = (0,0,0)
#scene.range = (4*e_distance, 4*e_distance, 4*e_distance)
scene.range = (2*e_radius, 2*e_radius, 2*e_radius)
shapes = []
iata_code = 'ILM'
shapes = load_iata()

while 1:
	rate(60)

