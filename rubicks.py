#!/usr/local/bin/python2.7

from visual import *

rotating_camera = False
camera_time = 0
cam_dx = 0
cam_dy = 0
cam_dz = 0

g = 0.10 # box thinness
w = 0.45 # size of surfaces
z = 0.70 # z distance of surfaces
d = 0.5  # x/y distance of surfaces
axle_pos = 0.60 # position of axles
c = 0.2  # color coefficient of axles
axle_opacity = 0.2
d_theta = 5

def collision(box1, box2):
	return \
		abs(box1.pos.x - box2.pos.x) * 2 <= (box1.length + box2.length) and \
		abs(box1.pos.y - box2.pos.y) * 2 <= (box1.height + box2.height) and \
		abs(box1.pos.z - box2.pos.z) * 2 <= (box1.width  + box2.width )
	#return \
	#	(box1.pos.x >= box2.pos.x - box2.length and box1.pos.x <= box2.pos.x + box2.length) and \
	#	(box1.pos.y >= box2.pos.y - box2.height and box1.pos.y <= box2.pos.y + box2.height) and \
	#	(box1.pos.z >= box2.pos.z - box2.width  and box1.pos.z <= box2.pos.z + box2.width )

class Face:
	def __init__(self, c, rotate, sign):
		self.color = c
		self.surfaces = []
		self.labels = []
		size = (w,w,g)
		if sign == 0:
			normal = 3
		elif sign == 2:
			normal = -3
		else:
			normal = rotate[0] * sign + 2 * rotate[1] * sign
		for i in [-1, 0, 1]:
			for j in [-1, 0, 1]:
				surface = box( pos=(j*d, i*d, z), size=size, color=c )
				surface.rotate( angle = sign * pi / 2.0, axis = rotate, origin = (0,0,0) )
				surface.opacity = 0.9
				surface.coordinate = (normal, i, j)
				self.surfaces.append( surface )
				#lab = label( pos=surface.pos, text="%d,%d,%d" % (normal,i,j) )

class Block(sphere):
	def __init__(self, px,py,pz):
		sphere.__init__(self, pos=(px*z, py*z, pz*z), radius=w/4 )
		self.opacity = 0.5
		self.surfaces = []

	def collision(self, box):
		return \
			abs(self.pos.x - box.pos.x) * 2 <= abs(2*self.radius + box.length) and \
			abs(self.pos.y - box.pos.y) * 2 <= abs(2*self.radius + box.height) and \
			abs(self.pos.z - box.pos.z) * 2 <= abs(2*self.radius + box.width )

	#def collision(self, box):
	#	bminx = min(box.pos[0] - box.size[0], box.pos[0] + box.size[0])
	#	bmaxx = max(box.pos[0] - box.size[0], box.pos[0] + box.size[0])
	#	bminy = min(box.pos[1] - box.size[1], box.pos[1] + box.size[1])
	#	bmaxy = max(box.pos[1] - box.size[1], box.pos[1] + box.size[1])
	#	bminz = min(box.pos[2] - box.size[2], box.pos[2] + box.size[2])
	#	bmaxz = max(box.pos[2] - box.size[2], box.pos[2] + box.size[2])
	#	bx = max(bminx, min(self.x, bmaxx))
	#	by = max(bminy, min(self.y, bmaxy))
	#	bz = max(bminz, min(self.z, bmaxz))

	#	distance = sqrt( \
	#		(bx - self.x) ** 2 + \
	#		(by - self.y) ** 2 + \
	#		(bz - self.z) ** 2 )
  
	#	return distance < self.radius


class Cube:
	def __init__(self):
		self.clockwise = 1
		self.centroid = box( pos=( 0, 0, 0 ), size=( 1.2*z, 1.2*z, 1.2*z ), color=( 0, 0, 0 ) )

		self.faces = []
		self.faces.append( Face( color.white,  (1,0,0), -1) )
		self.faces.append( Face( color.yellow, (1,0,0),  1) )
		self.faces.append( Face( color.red,    (0,1,0), -1) )
		self.faces.append( Face( color.orange, (0,1,0),  1) )
		self.faces.append( Face( color.blue,   (1,0,0),  0) )
		self.faces.append( Face( color.green,  (1,0,0),  2) )

		z2 = z * 2
		z3 = z / 3.0
		k = axle_pos
		self.axles = []
		self.axles.append( box( pos=(  0, k, 0 ), size=( z2, z3, z2 ), color=(c, c, c) ) )
		self.axles.append( box( pos=(  0,-k, 0 ), size=( z2, z3, z2 ), color=(c, c, 0) ) )
		self.axles.append( box( pos=( -k, 0, 0 ), size=( z3, z2, z2 ), color=(c, 0, 0) ) )
		self.axles.append( box( pos=(  k, 0, 0 ), size=( z3, z2, z2 ), color=(c, c/2, 0) ) )
		self.axles.append( box( pos=(  0, 0, k ), size=( z2, z2, z3 ), color=(0, 0, c) ) )
		self.axles.append( box( pos=(  0, 0,-k ), size=( z2, z2, z3 ), color=(0, c, 0) ) )

		self.blocks = []
		for i in [-1, 0, 1]:
			for j in [-1, 0, 1]:
				for k in [-1, 0, 1]:
					if i == 0 and j == 0 and k == 0:
						continue
					self.blocks.append( Block( i, j, k ) )

		self.rotating_time = 0
		self.rotating_surfaces = []
		self.rotating_blocks = []
		self.rotating_axle = None
		for axle in self.axles:
			axle.opacity = axle_opacity

		self.load_surfaces_into_blocks()

		self.selected_block = len(self.blocks) - 1
		self.previous_colors = []


	def load_surfaces_into_blocks(self):
		for block in self.blocks:
			for face in self.faces:
				for surface in face.surfaces:
					if block.collision(surface):
						block.surfaces.append(surface)

	def rotate(self, d):
		axlemap = { 'U': 0, 'D': 1, 'L': 2, 'R': 3, 'F': 4, 'B': 5 }

		if self.rotating_axle is not None or self.rotating_time != 0:
			return

		for axle in self.axles:
			axle.opacity = 0.0

		if d == d.lower():
			self.clockwise = -1;
		else:
			self.clockwise =  1
		axle_index = self.axles[ axlemap[ d.upper() ] ]
		self.start_rotation( axle_index )

	def start_rotation(self, axle):
		self.rotating_axle = axle
		self.rotating_surfaces = []
		self.rotating_blocks = []

		for block in self.blocks:
			if block.collision(axle):
				self.rotating_blocks.append(block)
				for surface in block.surfaces:
					print "surface"
					if surface not in self.rotating_surfaces:
						self.rotating_surfaces.append(surface)
					else:
						print "attempting to add surface again"

		#for face in self.faces:
		#	for s in face.surfaces:
		#		if collision(s, axle):
		#			self.rotating_surfaces.append(s)

		if len(self.rotating_surfaces) != 21:
			print "wrong number of surfaces %d" % len(self.rotating_surfaces)
		axle.opacity = 1.0

	def do_rotation(self):
		if self.rotating_axle:
			axle = self.rotating_axle
			axle.rotate(angle=radians(-d_theta * self.clockwise), axis=axle.pos, origin=axle.pos)
			for s in self.rotating_surfaces:
				s.rotate(angle=radians(-d_theta * self.clockwise), axis=axle.pos, origin=axle.pos)
			for b in self.rotating_blocks:
				b.rotate(angle=radians(-d_theta * self.clockwise), axis=axle.pos, origin=axle.pos)
			self.rotating_time += d_theta
			if self.rotating_time >= 90:
				self.stop_rotation()

	def stop_rotation(self):
		self.rotating_axle = None
		self.rotating_surfaces = []
		self.rotating_blocks = []
		self.rotating_time = 0
		for axle in self.axles:
			axle.opacity = axle_opacity

	def print_positions(self):
		for face in self.faces:
			print
			for surface in face.surfaces:
				print surface.pos

	
	def select_block(self, select):
		select %= len(self.blocks)
		if len(self.previous_colors) == len(self.blocks[self.selected_block].surfaces):
			n = 0
			self.blocks[self.selected_block].color = (1,1,1)
			for s in self.blocks[self.selected_block].surfaces:
				s.color = self.previous_colors[n]
				n += 1

		self.selected_block = select
		self.previous_colors = []
		for s in self.blocks[self.selected_block].surfaces:
			self.previous_colors.append( s.color )
			s.color = (0,1,1)
		self.blocks[self.selected_block].color = (1,0,1)


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
	print vars(evt)
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

scene = display( title="Rubick.py", x=800, y=400, width=800, height=600, scale=(0.5,0.5,0.5), background=(0.2,0.2,0.3) )
scene.forward = (0.5, -0.5, -1)
scene.bind('keydown', keydown)

cube = Cube()
#cube.print_positions()

#print cube.blocks[0].pos
#print cube.faces[1].surfaces[0].pos
#print cube.faces[2].surfaces[0].pos
#print cube.faces[5].surfaces[6].pos
#for s in cube.blocks[0].surfaces:
#	s.color = (0,1,1)

while 1:
	rate(60)
	cube.do_rotation()
	rotate_camera()


