#!/usr/local/bin/python2.7

from visual import *
from cube import *
from solver import *

rotating_camera = False
camera_time = 0
cam_d_theta = 0
cam_axis = (0,0,0)

def rotate_camera():
	global rotating_camera, camera_time, cam_dx, cam_dy, cam_dz
	if rotating_camera:
		cx = scene.forward[0]
		cy = scene.forward[1]
		cz = scene.forward[2]
		camera_time += d_theta
		if camera_time >= 90:
			camera_time = 0
			cam_dx = 0
			cam_dy = 0
			cam_dz = 0
			rotating_camera = False

def keydown(evt):
	global rotating_camera, cam_axis, selected_block
	k = evt.key
	#print vars(evt)
	if k in ('esc','Q','q'):
		exit()
	if k.upper() in ('R','L','U','D','B','F'):
		push(k)
	if k == 'left':
		axis = scene.up
		scene.forward = scene.forward.rotate( angle=radians(-5), axis=axis )
		#scene.up = scene.up.rotate( angle=radians(-5), axis=axis )
	elif k == 'right':
		axis = scene.up
		scene.forward = scene.forward.rotate( angle=radians( 5), axis=axis )
		#scene.up = scene.up.rotate( angle=radians( 5), axis=axis )
	elif k == 'down':
		axis = (0,0,1)
		scene.forward = scene.forward.rotate( angle=radians(-5), axis=axis )
		scene.up = scene.up.rotate( angle=radians(-5), axis=axis )
	elif k == 'up':
		axis = (0,0,1)
		scene.forward = scene.forward.rotate( angle=radians( 5), axis=axis )
		scene.up = scene.up.rotate( angle=radians( 5), axis=axis )
	elif k == '.':
		select = cube.selected_block + 1
		cube.select_block(select)
	elif k == ',':
		select = cube.selected_block + len(cube.blocks) - 1
		cube.select_block(select)
	elif k in ('1','2','3','4','5','6','7','8','9','0'):
		index = 9 + int(k)
		index %= 10
		sequence = Solver.sequences.keys()[index]
		solver.move(sequence)
	elif k == '*':
		scramble()
	elif k == '\n':
		#solver.white_cross()
		pass
	elif k == '/':
		cube.orient(scene.forward, scene.up)

def identify_closest():
	pass

def push(item):
	queue.insert(0, item)
	update_queue()

def update_queue():
	text = ""
	for item in queue:
		text = item + " "+ text
	queue_label.text = "Q: " + text

def check_queue():
	text = ""
	if len(queue) > 0:
		if cube.rotating_axle is None:
			update_queue()
			rot = queue.pop()
			cube.rotate(rot)
	else:
		Cube.d_theta = Cube.normal_d_theta
		if cube.rotating_axle is None:
			update_queue()

def scramble():
	Cube.d_theta = 15
	for t in range(20):
		rnd = random.randint(0,11)
		queue.append(['U','D','L','R','F','B','u','d','l','r','f','b'][rnd])


scene = display( title="Rubick.py", x=800, y=400, width=800, height=600, scale=(0.5,0.5,0.5), background=(0.2,0.2,0.3) )
scene.fov = radians(30)
scene.forward = (0.5, -0.5, -1)
scene.bind('keydown', keydown)
queue_label = label( title="Q: ", pos=(-1.8,-1,0), xoffset=1, box=False )
forward_label = label( title="", pos=(0, 1.0, 0), xoffset=1, box=False )

queue = []
cube = Cube()
solver = Solver(cube, queue)
#scramble()
#cube.print_positions()

while 1:
	rate(60)
	check_queue()
	cube.do_rotation()
	rotate_camera()
	solver.tick()
	forward_label.text = str(scene.forward)
