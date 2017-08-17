#!/usr/local/bin/python2.7

from visual import *

def keydown(evt):
	keymap = {
		'r': 'U',
		'u': 'u',
		't': 'U',
		'y': 'u',
		'b': 'd',
		'v': 'd',
		's': 'd',
		'l': 'd',
		'n': 'D',
		'e': 'l',
		'd': 'L',
		'i': 'R',
		'k': 'r',
		'f': 'f',
		'j': 'F',
		'g': 'B',
		'h': 'b',
	}
	k = evt.key

	if k in keymap:
		solver.queue.insert(0, keymap[k])
		return

	if k in ('esc','Q','q'):
		exit()
	#elif k.upper() in ('R','L','U','D','B','F'):
	#	solver.queue.insert(0,k)
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
	elif k == ',':
		select_block((-1,0,0))
	elif k == '.':
		select_block((1,0,0))
	elif k == ';':
		select_block((0,-1,0))
	elif k == "'":
		select_block((0,1,0))
	elif k == "[":
		select_block((0,0,-1))
	elif k == "]":
		select_block((0,0,1))

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

scene = display( title="Earth", width=800, height=600, background=(0.0,0.0,0.0) )
scene.autoscale = False
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
earth = sphere( pos=(0,0,0), radius=e_radius, material=materials.earth )
earth.rotate( angle=radians(90), axis=(0,1,0), origin=earth.pos )
flattening = 0 #1/298.257223563
eccentricity = 2 * flattening - flattening ** 2
height = e_radius

def poi( latitude, longitude ):
	latitude  = radians(latitude)
	longitude = -radians(longitude)
	#curvature = 1.0 / sqrt( 1 - eccentricity ** 2 * sin( latitude ) )
	curvature = 0
	pos = vector( \
		(curvature + height) * cos( latitude ) * cos( longitude ), \
		(curvature * (1 - eccentricity ** 2) + height) * sin( latitude ), \
		(curvature + height) * cos( latitude ) * sin( longitude ) \
	)
	return pos

def poi_sphere( latitude, longitude ):
	return sphere( pos=poi(latitude, longitude), color=(1,1,0), radius=100 )

san_diego = poi_sphere(32.75, -117)
mexico_city = poi_sphere(19.43333, -99.13333)
san_jose = poi_sphere(9.9333, -84.08333)

arc = curve( pos=[ san_diego.pos, 1.05*san_diego.pos, 1.05*mexico_city.pos, mexico_city.pos ] )

scene.center = (0,0,0)
#scene.range = (4*e_distance, 4*e_distance, 4*e_distance)
scene.range = (2*e_radius, 2*e_radius, 2*e_radius)

while 1:
	rate(60)

