#!/usr/local/bin/python2.7

from visual import *
from cube import *
from solver import *

rotating_camera = False
camera_time = 0
cam_dx = 0
cam_dy = 0
cam_dz = 0

def rotate_camera():
	global rotating_camera, camera_time, cam_dx, cam_dy, cam_dz
	if rotating_camera:
		cx = scene.forward[0]
		cy = scene.forward[1]
		cz = scene.forward[2]
		scene.forward = ( cx + cam_dx, cy + cam_dy, cz + cam_dz )
		camera_time += d_theta
		if camera_time >= 90:
			camera_time = 0
			cam_dx = 0
			cam_dy = 0
			cam_dz = 0
			rotating_camera = False

def keydown(evt):
	global rotating_camera, cam_dx, cam_dy, cam_dz, selected_block
	k = evt.key
	#print vars(evt)
	if evt.alt:
		if k == 'up':
			rotating_camera = True
			cam_dy = radians(5)
		elif k == 'down':
			rotating_camera = True
			cam_dy = -radians(5)
		if k == 'left':
			rotating_camera = True
			cam_dx = radians(5)
		elif k == 'right':
			rotating_camera = True
			cam_dx = -radians(5)
		return
	if evt.shift:
		if k == 'up':
			cube.rotate('R')
		elif k == 'down':
			cube.rotate('r')
		elif k == 'right':
			cube.rotate('D')
		elif k == 'left':
			cube.rotate('d')
	else:
		if k == 'esc':
			exit()
		elif k == 'left':
			cube.rotate('U')
		elif k == 'right':
			cube.rotate('u')
		elif k == 'down':
			cube.rotate('L')
		elif k == 'up':
			cube.rotate('l')
		elif k == 'home':
			cube.rotate('f')
		elif k == 'end':
			cube.rotate('F')
		elif k == 'page up':
			cube.rotate('b')
		elif k == 'page down':
			cube.rotate('B')
		elif k in ('1','2','3','4','5','6','7','8','9','0'):
			block = cube.blocks[int(k)]
			block.color = (1,0,1)
			for s in block.surfaces:
				print s.pos
		elif k == '.':
			select = cube.selected_block + 1
			cube.select_block(select)
		elif k == ',':
			select = cube.selected_block + len(cube.blocks) - 1
			cube.select_block(select)
		elif k == '\n':
			solver.white_cross()

def check_queue():
	if len(queue) > 0:
		if cube.rotating_axle is None:
			rot = queue.pop()
			cube.rotate(rot)
	else:
		Cube.d_theta = Cube.normal_d_theta

def scramble():
	Cube.d_theta = 15
	for t in range(10):
		rnd = random.randint(0,5)
		queue.append(['u','d','l','r','f','b'][rnd])


scene = display( title="Rubick.py", x=800, y=400, width=800, height=600, scale=(0.5,0.5,0.5), background=(0.2,0.2,0.3) )
scene.fov = radians(30)
scene.forward = (0.5, -0.5, -1)
scene.bind('keydown', keydown)

queue = []
cube = Cube()
solver = Solver(cube, queue)
#scramble()
#cube.print_positions()

#print cube.blocks[0].pos
#print cube.faces[1].surfaces[0].pos
#print cube.faces[2].surfaces[0].pos
#print cube.faces[5].surfaces[6].pos
#for s in cube.blocks[0].surfaces:
#	s.color = (0,1,1)

while 1:
	rate(60)
	check_queue()
	cube.do_rotation()
	rotate_camera()
	solver.tick()
