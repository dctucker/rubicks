#!/usr/local/bin/python2.7

from visual import *
from cube import *
from solver import *

camera_d_theta_x = 0
camera_d_theta_y = 0
camera_d_theta_z = 0

def rotate_camera():
	global camera_d_theta_x, camera_d_theta_y, camera_d_theta_z
	cube.frame.rotate( angle=camera_d_theta_x, axis=(0,1,0) )
	cube.frame.rotate( angle=camera_d_theta_y, axis=(1,0,0) )
	cube.frame.rotate( angle=camera_d_theta_z, axis=(0,0,1) )
	if camera_d_theta_x == 0 and camera_d_theta_y == 0:
		if abs(cube.frame.axis.x * cube.frame.axis.y * cube.frame.axis.z) > radians(1):
			camera_d_theta_z = radians(1)
		else:
			camera_d_theta_z = 0

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
		coord = vector( coord.x + 1, coord.y, coord.z )
		if coord.x > 1:
			coord.x = -1
		cube.select_block(coord)
		print cube.blocks[ cube.selected_block ].pos
	elif k == ',':
		coord = cube.blocks[ cube.selected_block ].coordinate
		coord = vector( coord.x - 1, coord.y, coord.z )
		if coord.x < -1:
			coord.x = 1
		cube.select_block(coord)
	elif k == ';':
		coord = cube.blocks[ cube.selected_block ].coordinate
		coord = vector( coord.x, coord.y - 1, coord.z )
		if coord.y < -1:
			coord.y = 1
		cube.select_block(coord)
	elif k == "'":
		coord = cube.blocks[ cube.selected_block ].coordinate
		coord = vector( coord.x, coord.y + 1, coord.z )
		if coord.y > 1:
			coord.y = -1
		cube.select_block(coord)
	elif k == "[":
		coord = cube.blocks[ cube.selected_block ].coordinate
		coord = vector( coord.x, coord.y, coord.z - 1 )
		if coord.z < -1:
			coord.z = 1
		cube.select_block(coord)
	elif k == "]":
		coord = cube.blocks[ cube.selected_block ].coordinate
		coord = vector( coord.x, coord.y, coord.z + 1 )
		if coord.z > 1:
			coord.z = -1
		cube.select_block(coord)
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
		f = cube.frame
		cube.orient(f.world_to_frame(scene.forward), f.world_to_frame(scene.up))
	elif k == '`':
		block_pos = norm( cube.blocks[ cube.selected_block ].pos )
		#block_pos = cube.frame.frame_to_world( block_pos )
		print block_pos

		#block_pos.z = -block_pos.z
		#fwd = vector(scene.forward)
		#f

		fwd = vector(0,0,-1)
		dx = fwd.x - block_pos.x
		dy = fwd.y - block_pos.y
		dz = fwd.z - block_pos.z
		altitude = atan2(dy, sqrt(dx*dx + dz*dz))
		azimuth  = atan2( -dx, -dz )
		projection = atan2(fwd.z, fwd.y) - atan2(block_pos.z, block_pos.y)
		print altitude, azimuth, projection
		#angle = fwd.diff_angle( block_pos )
		#cube.frame.rotate( angle=angle, axis=(1,0,0) )

		#block_pos = block_pos.rotate(angle=radians(90), axis=(1,0,0))
		#cube.frame.axis = norm( block_pos )
		##cube.frame.rotate( angle=cube.frame.axis.diff_angle(block_pos), axis=cross(cube.frame.up, block_pos) )
	elif k == '\\':
		angle = -diff_angle( scene.forward, cube.frame.axis )
		axis = scene.forward.cross( cube.frame.axis )
		cube.frame.rotate( angle=angle, axis=axis )

		sel_pos = cube.frame.frame_to_world( cube.blocks[ cube.selected_block ].pos )
		sel_pos = norm(sel_pos)
		n = -scene.forward
		angle = -diff_angle( n, sel_pos )
		axis = n.cross( sel_pos )
		cube.frame.rotate( angle=angle, axis=axis )
	else:
		print vars(evt)

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


scene = display( title="Rubick.py", x=800, y=400, width=800, height=600, background=(0.2,0.2,0.3) )
scene.bind('keydown', keydown)
scene.bind('keyup'  , keyup)
queue_label   = label( title="Q: ", pos=(-1.8,-1,0), xoffset=1, box=False )
forward_label = label( title=""   , pos=(0, 1.0, 0), xoffset=1, box=False )


queue = []
cube = Cube()
solver = Solver(cube, queue)

pointer = arrow( pos=(0,0,0), axis=cube.frame.axis)


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
	pointer.axis = cube.frame.axis
	#cube.frame.axis
