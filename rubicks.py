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
			x_axis = self.cube.frame.frame_to_world( self.cube.get_axle('U').get_center_block().pos )
			self.cube.frame.rotate( angle=self.d_theta_x, axis=x_axis )
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

class Mirror:
	def __init__(self, cube, axle, ref_axle):
		self.axle = axle
		self.ref_axle = ref_axle
		self.cube = cube
		self.blocks = [];
		size = 0.2
		for i in [ -1, 0, 1 ]:
			self.blocks.append([])
			for j in [ -1, 0, 1 ]:
				pos = vector(0,2,0) + vector(i, j, 0) * size
				self.blocks[i+1].append( box( pos=pos, size=(size,size,0.01), color=(1,0,1) ) )

	def tick(self):
		ref_axle = self.cube.get_axle(self.ref_axle)
		axle = self.cube.get_axle(self.axle)
		center = axle.get_center_block()
		ref_center = ref_axle.get_center_block()
		axis = center.coordinate.cross(ref_center.coordinate)
		axes = []
		for i in range(len(center.coordinate)):
			if abs(center.coordinate[i]) < epsilon:
				axes.append(i)
		#print axes
				
		for (b,s) in axle.get_face_surfaces():
			#coord = axis - b.coordinate #b.coordinate.rotate(angle=radians(-90), axis=axis)
			#coord = s.normal.cross(b.coordinate)
			i = int(b.coordinate[ axes[0] ])
			j = int(b.coordinate[ axes[1] ])
			#print i,j
			self.blocks[ i +1 ][ j + 1 ].color = s.color
		#print


def keydown(evt):
	keymap = {
		't': 'u',
		'y': 'U',
		'b': 'D',
		'n': 'd',
		'e': 'l',
		'd': 'L',
		'i': 'R',
		'k': 'r',
		'g': 'f',
		'h': 'F',
		'f': 'B',
		'j': 'b',
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
		camera.d_theta_y = radians(-2)
	elif k == 'up':
		camera.d_theta_y = radians(2)
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
	elif k == '\\':
		snap_to_block()
	elif k == '?':
		#print solver.overall_metric()
		#print solver.face_metric('U')
		for b in cube.get_axle('U').get_edge_blocks():
			#print [c for c in b.get_colors()]
			print b.coordinate
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


scene = display( title="Rubick.py", x=800, y=400, width=800, height=600, background=(0.2,0.2,0.3) )
scene.bind('keydown', keydown)
scene.bind('keyup'  , keyup)
scene.bind('mousemove', mousemove)

cube = Cube()
solver = Solver(cube)
camera = Camera(scene, cube)
mirror = Mirror(cube,'U','B')

#pointer = arrow( pos=(0,0,0), axis=cube.frame.axis)
queue_label   = label( title="Q: ", pos=(-1.8,-1,0), xoffset=1, box=False )
forward_label = label( title=""   , pos=(0, 1.0, 0), xoffset=1, box=False )

while 1:
	rate(60)
	cube.tick()
	camera.tick()
	solver.tick()
	mirror.tick()

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

