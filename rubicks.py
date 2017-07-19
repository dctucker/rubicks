#!/usr/local/bin/python2.7

from visual import *
from cube import *
from solver import *

class Camera:
	def __init__(self, scene, cube):
		self.d_theta_x = 0
		self.d_theta_y = 0
		self.d_theta_z = 0
		self.axis = vector(1,0,0)
		self.theta_remaining = 0

		self.scene = scene
		self.cube = cube
		self.scene.fov = radians(30)

	def tick(self):
		if self.theta_remaining == 0:
			self.cube.frame.rotate( angle=self.d_theta_x, axis=(0,1,0) )
			self.cube.frame.rotate( angle=self.d_theta_y, axis=(1,0,0) )
			self.cube.frame.rotate( angle=self.d_theta_z, axis=(0,0,1) )
			if self.d_theta_x == 0 and self.d_theta_y == 0:
				if self.d_theta_z == 0:
					self.orient()
			#	if abs(self.cube.frame.axis.x * self.cube.frame.axis.y * self.cube.frame.axis.z) > radians(1):
			#		self.d_theta_z = radians(1)
			#	else:
			#		self.d_theta_z = 0
		else:
			self.theta_remaining = sign(self.theta_remaining) * ( abs(self.theta_remaining) - radians(1) )
			self.cube.frame.rotate( angle=radians(1) * sign(self.theta_remaining), axis=self.axis )
			if abs(self.theta_remaining) < radians(8):
				self.theta_remaining = 0
				self.orient()

	def orient(self):
		f = self.cube.frame
		self.cube.orient(f.world_to_frame(self.scene.forward), f.world_to_frame(self.scene.up))

	def snap_to_block(self):
		origin = vector(self.cube.frame.axis)

		sel_pos = self.cube.frame.frame_to_world( self.cube.blocks[ self.cube.selected_block ].pos )
		sel_pos = norm(sel_pos)
		n = -scene.forward
		angle = -diff_angle( n, sel_pos )
		axis = n.cross( sel_pos )
		#self.cube.frame.rotate( angle=angle, axis=axis )

		camera.theta_remaining = angle
		camera.axis = axis

def keydown(evt):
	k = evt.key
	if k in ('esc','Q','q'):
		exit()
	elif k.upper() in ('R','L','U','D','B','F'):
		solver.queue.insert(0,k)
	elif k == 'left':
		camera.d_theta_x = radians(-2)
	elif k == 'right':
		camera.d_theta_x = radians(2)
	elif k == 'down':
		camera.d_theta_y = radians(-2)
	elif k == 'up':
		camera.d_theta_y = radians(2)
	elif k == 'page up':
		camera.d_theta_z = radians(-2)
	elif k == 'page down':
		camera.d_theta_z = radians(2)
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
		camera.orient()
	elif k == '\\':
		snap_to_block()
	else:
		print vars(evt)

def keyup(evt):
	k = evt.key
	#print vars(evt)
	if k in ('left','right'):
		camera.d_theta_x = 0
	elif k in ('up','down'):
		camera.d_theta_y = 0
	elif k in ('page up','page down'):
		camera.d_theta_z = 0

def mousemove(evt):
	if isinstance(scene.mouse.pick, Block):
		if cube.blocks[ cube.selected_block ] != scene.mouse.pick:
			cube.select_block( scene.mouse.pick.coordinate )

def select_block(coord):
	cube.select_block(coord)
	camera.snap_to_block()


scene = display( title="Rubick.py", x=800, y=400, width=800, height=600, background=(0.2,0.2,0.3) )
scene.bind('keydown', keydown)
scene.bind('keyup'  , keyup)
scene.bind('mousemove', mousemove)

cube = Cube()
solver = Solver(cube)
camera = Camera(scene, cube)

#pointer = arrow( pos=(0,0,0), axis=cube.frame.axis)
queue_label   = label( title="Q: ", pos=(-1.8,-1,0), xoffset=1, box=False )
forward_label = label( title=""   , pos=(0, 1.0, 0), xoffset=1, box=False )

while 1:
	rate(60)
	cube.tick()
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

