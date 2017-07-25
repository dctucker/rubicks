#!/usr/local/bin/python2.7

from visual import *
from cube import *
from solver import *
from camera import *

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

	#elif k == '0':
	#	solver.queue.insert(0, 'b')
	#elif k == '.':
	#	solver.queue.insert(0, 'B')
	#elif k == '2':
	#	solver.queue.insert(0, 'd')
	#elif k == '3':
	#	solver.queue.insert(0, 'D')
	#elif k == '4':
	#	solver.queue.insert(0, 'L')
	#elif k == '7':
	#	solver.queue.insert(0, 'l')
	#elif k == '5':
	#	solver.queue.insert(0, 'f')
	#elif k == '6':
	#	solver.queue.insert(0, 'F')
	#elif k == '\n':
	#	solver.queue.insert(0, 'r')
	#elif k == '+':
	#	solver.queue.insert(0, 'R')
	#elif k == '8':
	#	solver.queue.insert(0, 'u')
	#elif k == '9':
	#	solver.queue.insert(0, 'U')

	#elif k in ('1','2','3','4','5','6','7','8','9','0'):
	#	index = 9 + int(k)
	#	index %= 10
	#	sequence = Solver.sequences.keys()[index]
	#	solver.move(sequence)
	elif k == '*':
		solver.scramble()
	elif k == '/':
		camera.orient()
	elif k == '?':
		for axle in cube.axles:
			print axle.pos
		#print solver.overall_metric()
		#print solver.face_metric('U')

		#for b in cube.get_axle('U').get_edge_blocks():
		#	print b.coordinate

		#for (b,s) in cube.get_axle('U').get_face_surfaces():
		#	print b.coordinate
		print



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
	if isinstance(pick, Block):
		if cube.blocks[ cube.selected_block ] != scene.mouse.pick:
			cube.select_block( scene.mouse.pick.coordinate )
	elif isinstance(pick, box):
		for block in cube.blocks:
			for s in block.surfaces:
				if s == pick:
					cube.select_block( block.coordinate )

def select_block(coord):
	coord = cube.blocks[ cube.selected_block ].coordinate + vector(coord)
	print coord
	if coord.x >= -1 and coord.x <= 1 and coord.y >= -1 and coord.y <= 1 and coord.z >= -1 and coord.z <= 1:
		cube.select_block(coord)
		camera.snap_to_block()


scene = display( title="Rubick.py", width=800, height=600, background=(0.1,0.1,0.2) )
scene.lights = [
	#distant_light(direction=(1, 0, 0), color=color.gray(0.6)),
	#distant_light(direction=(0,  3, -3), color=color.gray(0.9)),
	local_light(  pos=(0, 0, 5), color=color.gray(0.3)),
	local_light(  pos=(3, -1, 3), color=color.gray(0.3)),
	local_light(  pos=(-3, -1, 3), color=color.gray(0.3)),
	local_light(  pos=(0, 8, 1), color=color.gray(0.3))
]
scene.range = (3,3,10)
background = box( pos=(0,0,-10), size=(20,20,0.01), color=(0.2,0.1,0.0), material=materials.wood )
#background = box( pos=(-3,-1.5,-9), size=(4,0.1,8), color=(0.0,0.0,0.0), material=materials.rough )
#background = box( pos=(-4,-3,-9), size=(4.5,4,0.1), color=(0.0,0.0,0.0), material=materials.rough )
scene.bind('keydown', keydown)
scene.bind('keyup'  , keyup)
scene.bind('mousemove', mousemove)

cube = Cube()
solver = Solver(cube)
camera = Camera(scene, cube)
rot = 45
#camera.mirrors.append( Mirror(cube,'L', (-1.8,    0,    1), radians(-90 )))
#camera.mirrors.append( Mirror(cube,'R', ( 1.8,    0,    1), radians( 90 )))
#camera.mirrors.append( Mirror(cube,'U', (   0,  1.4,    0), radians(  0 )))
#camera.mirrors.append( Mirror(cube,'D', (   0, -1.4,    0), radians(  0 )))
#camera.mirrors.append( Mirror(cube,'B', ( 1.4, -1.2, -2.5), radians(  0 )))
#camera.mirrors[0].frame.rotate(angle=radians(-45), axis=(0,1,0), origin=camera.mirrors[0].frame.pos)
#camera.mirrors[1].frame.rotate(angle=radians( 45), axis=(0,1,0), origin=camera.mirrors[1].frame.pos)
#camera.mirrors[2].frame.rotate(angle=radians(-45), axis=(1,0,0), origin=camera.mirrors[2].frame.pos)
#camera.mirrors[3].frame.rotate(angle=radians(225), axis=(1,0,0), origin=camera.mirrors[3].frame.pos)
#camera.mirrors[4].frame.rotate(angle=radians(-45), axis=(1,1,0), origin=camera.mirrors[4].frame.pos)

double = Double(cube)

#pointer = arrow( pos=(0,0,0), axis=cube.frame.axis)
queue_label   = label( title="Q: ", pos=(-3,-3,0), xoffset=1, box=False )
forward_label = label( title=""   , pos=(0, 4, 0), xoffset=1, box=False )

while 1:
	rate(60)
	cube.tick()
	double.tick()
	camera.tick()
	solver.tick()

	text = ""
	for item in solver.queue:
		text = item + " "+ text
	queue_label.text = "Q: " + text
	#forward_label.text = str( norm( cube.frame.frame_to_world( cube.blocks[ cube.selected_block ].pos ) ) )
	forward_label.text = str( norm( cube.frame.axis ) )
	#forward_label.text = str( degrees( diff_angle( scene.forward, cube.frame.axis ) ) )
	#forward_label.text = str( scene.forward.cross( cube.frame.axis ) )
	#pointer.axis = cube.frame.axis
	#cube.frame.axis

