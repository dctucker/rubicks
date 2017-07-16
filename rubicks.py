#!/usr/local/bin/python2.7

from visual import *

g = 0.05 # box thinness
w = 0.45 # size of surfaces
z = 0.75 # z distance of surfaces
d = 0.5  # x/y distance of surfaces
k = 0.61 # position of axles
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

class Cube:
	def __init__(self):
		self.clockwise = 1

		self.faces = []
		self.faces.append( Face( color.white,  (1,0,0), -1) )
		self.faces.append( Face( color.yellow, (1,0,0),  1) )
		self.faces.append( Face( color.red,    (0,1,0), -1) )
		self.faces.append( Face( color.orange, (0,1,0),  1) )
		self.faces.append( Face( color.blue,   (1,0,0),  0) )
		self.faces.append( Face( color.green,  (1,0,0),  2) )

		z2 = z * 2
		z3 = z / 3.0
		self.axles = []
		self.axles.append( box( pos=(  0, k, 0 ), size=( z2, z3, z2 ), color=(c, c, c) ) )
		self.axles.append( box( pos=(  0,-k, 0 ), size=( z2, z3, z2 ), color=(c, c, 0) ) )
		self.axles.append( box( pos=( -k, 0, 0 ), size=( z3, z2, z2 ), color=(c, 0, 0) ) )
		self.axles.append( box( pos=(  k, 0, 0 ), size=( z3, z2, z2 ), color=(c, c/2, 0) ) )
		self.axles.append( box( pos=(  0, 0, k ), size=( z2, z2, z3 ), color=(0, 0, c) ) )
		self.axles.append( box( pos=(  0, 0,-k ), size=( z2, z2, z3 ), color=(0, c, 0) ) )

		self.centroid = box( pos=( 0, 0, 0 ), size=( 1.2*z, 1.2*z, 1.2*z ), color=( 0, 0, 0 ) )

		self.rotating_time = 0
		self.rotating_surfaces = []
		self.rotating_axle = None
		for axle in self.axles:
			axle.opacity = axle_opacity


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
		self.rotating_surfaces = []
		for face in self.faces:
			for s in face.surfaces:
				if collision(s, axle):
					self.rotating_surfaces.append(s)
					print s.coordinate

		if len(self.rotating_surfaces) < 21:
			print "missing piece"
		axle.opacity = 1.0
		self.rotating_axle = axle

	def do_rotation(self):
		if self.rotating_axle:
			self.rotating_axle.rotate(angle=radians(-d_theta * self.clockwise), axis=self.rotating_axle.pos, origin=self.rotating_axle.pos)
			for s in self.rotating_surfaces:
				s.rotate(angle=radians(-d_theta * self.clockwise), axis=self.rotating_axle.pos, origin=self.rotating_axle.pos)
			self.rotating_time += d_theta
			if self.rotating_time >= 90:
				self.stop_rotation()

	def stop_rotation(self):
		self.rotating_axle = None
		self.rotating_surfaces = []
		self.rotating_time = 0
		for axle in self.axles:
			axle.opacity = axle_opacity
		#self.print_positions()

	def print_positions(self):
		for face in self.faces:
			print
			for surface in face.surfaces:
				print surface.pos


def keydown(evt):
	k = evt.key
	print vars(evt)
	if not evt.shift:
		if k == 'esc':
			exit()
		elif k == 'up':
			cube.rotate('U')
		elif k == 'down':
			cube.rotate('D')
		elif k == 'right':
			cube.rotate('R')
		elif k == 'left':
			cube.rotate('L')
		elif k == 'page up':
			cube.rotate('B')
		elif k == 'page down':
			cube.rotate('F')
	else:
		if k == 'up':
			cube.rotate('u')
		elif k == 'down':
			cube.rotate('d')
		elif k == 'right':
			cube.rotate('r')
		elif k == 'left':
			cube.rotate('l')
		elif k == 'page up':
			cube.rotate('b')
		elif k == 'page down':
			cube.rotate('f')

scene = display( title="Rubick.py", x=800, y=400, width=800, height=600, scale=(0.5,0.5,0.5), background=(0.2,0.2,0.3) )
scene.bind('keydown', keydown)

cube = Cube()
cube.print_positions()

while 1:
	rate(60)
	cube.do_rotation()
