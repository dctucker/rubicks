from visual import *

g = 0.05 # box thinness
w = 0.45 # size of surfaces
z = 0.75 # z distance of surfaces
d = 0.5  # x/y distance of surfaces
axle_pos = 0.60 # position of axles
c = 0.2  # color coefficient of axles
axle_opacity = 0.0

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
				surface.opacity = 0.75
				surface.coordinate = (normal, i, j)
				surface.expected_coordinate = (normal, i, j)
				self.surfaces.append( surface )
				#lab = label( pos=surface.pos, text="%d,%d,%d" % (normal,i,j) )

class Block(sphere):
	def __init__(self, px,py,pz):
		self.expected_coordinate = vector(px, py, pz)
		self.coordinate = vector(px, py, pz)
		sphere.__init__(self, pos=(px*z, py*z, pz*z), radius=w*0.3 )
		self.opacity = 0.0
		self.material = materials.shiny
		self.surfaces = []

	def collision(self, box):
		return \
			abs(self.pos.x - box.pos.x) <= (2 * self.radius + box.length*0.5) and \
			abs(self.pos.y - box.pos.y) <= (2 * self.radius + box.height*0.5) and \
			abs(self.pos.z - box.pos.z) <= (2 * self.radius + box.width *0.5)
	
	def rotate(self, angle, axis, origin):
		self.coordinate = self.coordinate.rotate(angle=angle,axis=axis)
		sphere.rotate(self, angle=angle, axis=axis, origin=origin)

class Cube:
	palette = [
		vector(1,1,1),   #white
		vector(1,1,0),   #yellow
		vector(1,0,0),   #red
		vector(1,0.5,0), #orange
		vector(0,0,1),   #blue
		vector(0,1,0),   #green
	]

	normal_d_theta = 5
	d_theta = 5

	def __init__(self):
		self.orient()

		self.clockwise = 1
		self.centroid = sphere( pos=( 0, 0, 0 ), radius=z-g, color=( 0, 0, 0 ) )

		self.faces = []
		self.faces.append( Face( self.palette[0], (1,0,0), -1) )
		self.faces.append( Face( self.palette[1], (1,0,0),  1) )
		self.faces.append( Face( self.palette[2], (0,1,0), -1) )
		self.faces.append( Face( self.palette[3], (0,1,0),  1) )
		self.faces.append( Face( self.palette[4], (1,0,0),  0) )
		self.faces.append( Face( self.palette[5], (1,0,0),  2) )

		z2 = z * 2
		z3 = z / 3.0
		k = axle_pos
		self.axles = []
		self.axles.append( box( pos=(  0, k, 0 ), size=( z2, z3, z2 ), color=c * self.palette[0] ) )
		self.axles.append( box( pos=(  0,-k, 0 ), size=( z2, z3, z2 ), color=c * self.palette[1] ) )
		self.axles.append( box( pos=( -k, 0, 0 ), size=( z3, z2, z2 ), color=c * self.palette[2] ) )
		self.axles.append( box( pos=(  k, 0, 0 ), size=( z3, z2, z2 ), color=c * self.palette[3] ) )
		self.axles.append( box( pos=(  0, 0, k ), size=( z2, z2, z3 ), color=c * self.palette[4] ) )
		self.axles.append( box( pos=(  0, 0,-k ), size=( z2, z2, z3 ), color=c * self.palette[5] ) )

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

	def orient(self, front=None, up=None):
		if front is None and up is None:
			self.axlemap = { 'U': 0, 'D': 1, 'L': 2, 'R': 3, 'F': 4, 'B': 5 }
			return
		if front is None:
			front = self.axes[ self.axlemap['F'] ].pos
		left = front.rotate(angle=radians(90), axis=up)
		if up is None:
			up = self.axes[ self.axlemap['U'] ].pos
		directions = {
			'U': -up,
			'D':  up,
			'L': -left,
			'R':  left,
			'B': -front,
			'F':  front,
		}
		closest = {
			'U': 0,
			'D': 0,
			'L': 0,
			'R': 0,
			'B': 0,
			'F': 0,
		}
		for d,pos in directions.items():
			for a in range(len(self.axles)):
				if mag(pos - self.axles[closest[d]].pos) < mag(pos - self.axles[a].pos):
					closest[d] = a
		self.axlemap = closest

	def load_surfaces_into_blocks(self):
		for block in self.blocks:
			for face in self.faces:
				for surface in face.surfaces:
					if block.collision(surface):
						block.surfaces.append(surface)

	def rotate(self, d):

		if self.rotating_axle is not None or self.rotating_time != 0:
			return

		for axle in self.axles:
			axle.opacity = 0.0

		if d == d.lower():
			self.clockwise = -1;
		else:
			self.clockwise =  1
		axle_index = self.axles[ self.axlemap[ d.upper() ] ]
		self.start_rotation( axle_index )

	def start_rotation(self, axle):
		self.rotating_axle = axle
		self.rotating_surfaces = []
		self.rotating_blocks = []

		for block in self.blocks:
			if block.collision(axle):
				self.rotating_blocks.append(block)
				for surface in block.surfaces:
					if surface not in self.rotating_surfaces:
						self.rotating_surfaces.append(surface)
					else:
						print "attempting to add surface again"

		if len(self.rotating_surfaces) != 21:
			print "wrong number of surfaces %d" % len(self.rotating_surfaces)
		axle.opacity = 1.0

		#print self.rotating_blocks[0].coordinate

	def do_rotation(self):
		if self.rotating_axle:
			axle = self.rotating_axle
			axle.rotate(angle=radians(-Cube.d_theta * self.clockwise), axis=axle.pos, origin=axle.pos)
			for s in self.rotating_surfaces:
				s.rotate(angle=radians(-Cube.d_theta * self.clockwise), axis=axle.pos, origin=axle.pos)
			for b in self.rotating_blocks:
				b.rotate(angle=radians(-Cube.d_theta * self.clockwise), axis=axle.pos, origin=axle.pos)
			self.rotating_time += Cube.d_theta
			if self.rotating_time >= 90:
				self.stop_rotation()

	def stop_rotation(self):
		#print self.rotating_blocks[0].coordinate
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
		block = self.blocks[self.selected_block]
		if len(self.previous_colors) == len(block.surfaces):
			n = 0
			block.color = (1,1,1)
			block.opacity = 0.0
			for s in block.surfaces:
				#s.color = self.previous_colors[n]
				s.material = materials.diffuse
				n += 1

		self.selected_block = select
		self.previous_colors = []
		avg_color = vector(0,0,0)
		block = self.blocks[self.selected_block]
		for s in block.surfaces:
			self.previous_colors.append( s.color )
			avg_color += s.color
			#s.color = (0,1,1)
			s.material = materials.unshaded
		avg_color /= len(block.surfaces)
		block.color = avg_color
		block.opacity = 0.4
	
