#!/usr/local/bin/python2.7

from visual import *
from cube import *
from solver import *

camera_d_theta_x = 0
camera_d_theta_y = 0
camera_d_theta_z = 0

camera_axis = vector(1,0,0)
camera_theta_remaining = 0

def rotate_camera():
	global camera_d_theta_x, camera_d_theta_y, camera_d_theta_z, camera_axis, camera_theta_remaining
	if camera_theta_remaining == 0:
		cube.frame.rotate( angle=camera_d_theta_x, axis=(0,1,0) )
		cube.frame.rotate( angle=camera_d_theta_y, axis=(1,0,0) )
		cube.frame.rotate( angle=camera_d_theta_z, axis=(0,0,1) )
		if camera_d_theta_x == 0 and camera_d_theta_y == 0:
			if camera_d_theta_z == 0:
				orient()
		#	if abs(cube.frame.axis.x * cube.frame.axis.y * cube.frame.axis.z) > radians(1):
		#		camera_d_theta_z = radians(1)
		#	else:
		#		camera_d_theta_z = 0
	else:
		camera_theta_remaining = sign(camera_theta_remaining) * ( abs(camera_theta_remaining) - radians(1) )
		cube.frame.rotate( angle=radians(1) * sign(camera_theta_remaining), axis=camera_axis )
		if abs(camera_theta_remaining) < radians(8):
			camera_theta_remaining = 0
			orient()

def keydown(evt):
	global camera_d_theta_x, camera_d_theta_y, camera_d_theta_z
	k = evt.key
	if k in ('esc','Q','q'):
		exit()
	elif k.upper() in ('R','L','U','D','B','F'):
		push(k)
	elif k == 'left':
		camera_d_theta_x = radians(-2)
	elif k == 'right':
		camera_d_theta_x = radians(2)
	elif k == 'down':
		camera_d_theta_y = radians(-2)
	elif k == 'up':
		camera_d_theta_y = radians(2)
	elif k == 'page up':
		camera_d_theta_z = radians(-2)
	elif k == 'page down':
		camera_d_theta_z = radians(2)
	elif k == '.':
		coord = cube.blocks[ cube.selected_block ].coordinate
		if coord.x < 1:
			coord = vector( coord.x + 1, coord.y, coord.z )
			select_block(coord)
	elif k == ',':
		coord = cube.blocks[ cube.selected_block ].coordinate
		if coord.x > -1:
			coord = vector( coord.x - 1, coord.y, coord.z )
			select_block(coord)
	elif k == ';':
		coord = cube.blocks[ cube.selected_block ].coordinate
		if coord.y > -1:
			coord = vector( coord.x, coord.y - 1, coord.z )
			select_block(coord)
	elif k == "'":
		coord = cube.blocks[ cube.selected_block ].coordinate
		if coord.y < 1:
			coord = vector( coord.x, coord.y + 1, coord.z )
			select_block(coord)
	elif k == "[":
		coord = cube.blocks[ cube.selected_block ].coordinate
		if coord.z > -1:
			coord = vector( coord.x, coord.y, coord.z - 1 )
			select_block(coord)
	elif k == "]":
		coord = cube.blocks[ cube.selected_block ].coordinate
		if coord.z < 1:
			coord = vector( coord.x, coord.y, coord.z + 1 )
			select_block(coord)
	elif k in ('1','2','3','4','5','6','7','8','9','0'):
		index = 9 + int(k)
		index %= 10
		sequence = Solver.sequences.keys()[index]
		solver.move(sequence)
	elif k == '*':
		solver.scramble()
	elif k == '\n':
		#solver.white_cross()
		pass
	elif k == '/':
		orient()
	elif k == '\\':
		snap_to_block()
	else:
		print vars(evt)

def orient():
	f = cube.frame
	cube.orient(f.world_to_frame(scene.forward), f.world_to_frame(scene.up))

def select_block(coord):
	cube.select_block(coord)
	snap_to_block()

def snap_to_block():
	global camera_axis, camera_theta_remaining
	origin = vector(cube.frame.axis)

	sel_pos = cube.frame.frame_to_world( cube.blocks[ cube.selected_block ].pos )
	sel_pos = norm(sel_pos)
	n = -scene.forward
	angle = -diff_angle( n, sel_pos )
	axis = n.cross( sel_pos )
	#cube.frame.rotate( angle=angle, axis=axis )

	camera_theta_remaining = angle
	camera_axis = axis

def keyup(evt):
	global camera_d_theta_x, camera_d_theta_y, camera_d_theta_z
	k = evt.key
	#print vars(evt)
	if k == 'left':
		camera_d_theta_x = 0
	elif k == 'right':
		camera_d_theta_x = 0
	elif k == 'down':
		camera_d_theta_y = 0
	elif k == 'up':
		camera_d_theta_y = 0
	elif k == 'page up':
		camera_d_theta_z = 0
	elif k == 'page down':
		camera_d_theta_z = 0

def mousemove(evt):
	if isinstance(scene.mouse.pick, Block):
		if cube.blocks[ cube.selected_block ] != scene.mouse.pick:
			cube.select_block( scene.mouse.pick.coordinate )

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
		cube.d_theta = Cube.normal_d_theta
		if cube.rotating_axle is None:
			update_queue()

scene = display( title="Rubick.py", x=800, y=400, width=800, height=600, background=(0.2,0.2,0.3) )
scene.bind('keydown', keydown)
scene.bind('keyup'  , keyup)
scene.bind('mousemove', mousemove)

queue = []
cube = Cube()
solver = Solver(cube, queue)

#pointer = arrow( pos=(0,0,0), axis=cube.frame.axis)
queue_label   = label( title="Q: ", pos=(-1.8,-1,0), xoffset=1, box=False )
forward_label = label( title=""   , pos=(0, 1.0, 0), xoffset=1, box=False )

while 1:
	rate(60)
	check_queue()
	cube.do_rotation()
	rotate_camera()
	solver.tick()
	#forward_label.text = str( norm( cube.frame.frame_to_world( cube.blocks[ cube.selected_block ].pos ) ) )
	forward_label.text = str( norm( cube.frame.axis ) )
	#forward_label.text = str( degrees( diff_angle( scene.forward, cube.frame.axis ) ) )
	#forward_label.text = str( scene.forward.cross( cube.frame.axis ) )
	#pointer.axis = cube.frame.axis
	#cube.frame.axis
