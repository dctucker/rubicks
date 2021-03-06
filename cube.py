from visual import *

epsilon = 0.0000001
face_g = 0.04 # box thinness
face_w = 0.45 # size of surfaces
face_z = 0.75 # z distance of surfaces
face_d = 0.5  # x/y distance of surfaces
axle_pos = 0.60 # position of axles
axle_opacity = 0.0
axle_shade = 0.2  # color coefficient of axles

def zero_epsilon(vec):
	for i in range(len(vec)):
		if abs(vec[i]) < epsilon:
			vec[i] = 0.0
	return vec

class Face:
	def __init__(self, cube, c, rotate, sign):
		self.color = c
		self.surfaces = []
		self.labels = []
		size = (face_w,face_w,face_g)
		if sign == 0:
			normal = vector(0,0,1)
			#normal = 3
		elif sign == 2:
			normal = vector(0,0,-1)
			#normal = -3
		else:
			normal = vector(0,0,-sign).cross(rotate)
			#normal = rotate[0] * sign + 2 * rotate[1] * sign
		for i in [-1, 0, 1]:
			for j in [-1, 0, 1]:
				surface = box( frame=cube.frame, pos=(j*face_d, i*face_d, face_z), size=size, color=c )
				surface.rotate( angle = sign * pi / 2.0, axis = rotate, origin = (0,0,0) )
				surface.opacity = 0.75
				surface.normal = normal
				#surface.coordinate = vector(i, j, normal)
				#surface.expected_coordinate = vector(i, j, normal)
				self.surfaces.append( surface )
				#lab = label( pos=surface.pos, text="%d,%d,%d" % (normal,i,j) )

class Block(sphere):
	def __init__(self, cube, px,py,pz):
		self.expected_coordinate = vector(int(px), int(py), int(pz))
		self.coordinate = vector(px, py, pz)
		sphere.__init__(self, frame=cube.frame, pos=(px*face_z, py*face_z, pz*face_z), radius=face_w*0.3 )
		self.opacity = 0.0
		self.material = materials.shiny
		self.surfaces = []

		pos = vector(px, py, pz) * (face_d - 0.5*face_g)
		size = vector(face_w,face_w,face_w) * (1.0 + 2.0 * face_g)
		self.blind = box( frame=cube.frame, pos=pos, size=size, color=(1,1,1) )
	
	def get_colors(self):
		for s in self.surfaces:
			yield s.color

	def collision(self, box):
		return \
			abs(self.pos.x - box.pos.x) <= (2 * self.radius + box.length*0.5) and \
			abs(self.pos.y - box.pos.y) <= (2 * self.radius + box.height*0.5) and \
			abs(self.pos.z - box.pos.z) <= (2 * self.radius + box.width *0.5)
	
	def rotate(self, angle, axis, origin):
		self.coordinate = zero_epsilon( self.coordinate.rotate(angle=angle,axis=axis) )
		self.blind.rotate(self, angle=angle, axis=axis, origin=origin)
		sphere.rotate(self, angle=angle, axis=axis, origin=origin)

class Axle:
	def __init__(self, cube, pos, size, color):
		self.cube = cube
		self.box = box( frame=self.cube.frame, pos=pos, size=size, color=color )
		self.north = radians(0)
		self.box.opacity = axle_opacity
		self.pos = self.box.pos
		self.size = self.box.size
		self.length = self.box.length
		self.height = self.box.height
		self.width  = self.box.width
		self.color = self.box.color

		n = norm(self.pos)
		r = 2 * face_d - face_g
		#self.blind = box( frame=self.cube.frame, pos=n * face_w * 0.5, size=(r,r,r), axis=n, color=(0,0,0) )

	def get_blocks(self):
		ret = []
		for block in self.cube.blocks:
			if block.collision(self):
				ret.append(block)
		assert( len(ret) == 9 )
		return ret

	def get_center_block(self):
		for b in self.get_blocks():
			if mag(b.coordinate) == 1.0:
				return b

	def get_edge_blocks(self):
		ret = []
		edge = mag((1,1,0))
		for b in self.get_blocks():
			if abs(mag(b.coordinate) - edge) < epsilon:
				ret.append(b)
		return ret

	def get_corner_blocks(self):
		ret = []
		corner = mag((1,1,1))
		for b in self.get_blocks():
			if mag(b.coordinate) - corner < epsilon:
				ret.append(b)
		return ret

	def get_face_surfaces(self):
		ret = []
		center_block = self.get_center_block()
		center = center_block.surfaces[0].normal
		for b in self.get_blocks():
			for s in b.surfaces:
				if mag(s.normal - center) < epsilon:
					ret.append( (b,s) )
		ret.sort(key=lambda v: 8*v[0].coordinate.x+4*v[0].coordinate.y+v[0].coordinate.z)
		return ret

	def rotate(self, angle, axis, origin):
		self.box.rotate(self.box, angle=angle, axis=axis, origin=origin)
		self.north = (self.north + angle) % radians(360)
		#self.blind.rotate(self.blind, angle=angle, axis=axis, origin=origin)



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

	def __init__(self):
		self.d_theta = Cube.normal_d_theta
		self.frame = frame( axis=(0,0,-1) )

		self.orient()

		self.clockwise = 1
		#self.centroid = sphere( frame=self.frame, pos=( 0, 0, 0 ), radius=face_z-face_g, color=( 0, 0, 0 ) )

		self.faces = []
		self.faces.append( Face( self, self.palette[0], (1,0,0), -1) )
		self.faces.append( Face( self, self.palette[1], (1,0,0),  1) )
		self.faces.append( Face( self, self.palette[2], (0,1,0), -1) )
		self.faces.append( Face( self, self.palette[3], (0,1,0),  1) )
		self.faces.append( Face( self, self.palette[4], (1,0,0),  0) )
		self.faces.append( Face( self, self.palette[5], (1,0,0),  2) )

		z2 = face_z * 2
		z3 = face_z / 3.0
		k = axle_pos
		self.axles = []
		self.axles.append( Axle( self, pos=(  0, k, 0 ), size=( z2, z3, z2 ), color=axle_shade * self.palette[0] ) )
		self.axles.append( Axle( self, pos=(  0,-k, 0 ), size=( z2, z3, z2 ), color=axle_shade * self.palette[1] ) )
		self.axles.append( Axle( self, pos=( -k, 0, 0 ), size=( z3, z2, z2 ), color=axle_shade * self.palette[2] ) )
		self.axles.append( Axle( self, pos=(  k, 0, 0 ), size=( z3, z2, z2 ), color=axle_shade * self.palette[3] ) )
		self.axles.append( Axle( self, pos=(  0, 0, k ), size=( z2, z2, z3 ), color=axle_shade * self.palette[4] ) )
		self.axles.append( Axle( self, pos=(  0, 0,-k ), size=( z2, z2, z3 ), color=axle_shade * self.palette[5] ) )

		#k = face_w * 0.5
		#self.blinds = []
		#self.blinds.append( ring( frame=self.frame, pos=(  0, k, 0 ), radius=face_z-face_g, axis=(0,1,0), color=(0,0,0) ) )
		#self.blinds.append( ring( frame=self.frame, pos=(  0,-k, 0 ), radius=face_z-face_g, axis=(0,1,0), color=(0,0,0) ) )
		#self.blinds.append( ring( frame=self.frame, pos=( -k, 0, 0 ), radius=face_z-face_g, axis=(1,0,0), color=(0,0,0) ) )
		#self.blinds.append( ring( frame=self.frame, pos=(  k, 0, 0 ), radius=face_z-face_g, axis=(1,0,0), color=(0,0,0) ) )
		#self.blinds.append( ring( frame=self.frame, pos=(  0, 0,-k ), radius=face_z-face_g, axis=(0,0,1), color=(0,0,0) ) )
		#self.blinds.append( ring( frame=self.frame, pos=(  0, 0, k ), radius=face_z-face_g, axis=(0,0,1), color=(0,0,0) ) )

		#k = face_w * 0.5
		#self.blinds = []
		#self.blinds.append( box( frame=self.frame, pos=(  0, k, 0 ), radius=face_z-face_g, axis=(0,1,0), color=(0,0,0) ) )
		#self.blinds.append( box( frame=self.frame, pos=(  0,-k, 0 ), radius=face_z-face_g, axis=(0,1,0), color=(0,0,0) ) )
		#self.blinds.append( box( frame=self.frame, pos=( -k, 0, 0 ), radius=face_z-face_g, axis=(1,0,0), color=(0,0,0) ) )
		#self.blinds.append( box( frame=self.frame, pos=(  k, 0, 0 ), radius=face_z-face_g, axis=(1,0,0), color=(0,0,0) ) )
		#self.blinds.append( box( frame=self.frame, pos=(  0, 0,-k ), radius=face_z-face_g, axis=(0,0,1), color=(0,0,0) ) )
		#self.blinds.append( box( frame=self.frame, pos=(  0, 0, k ), radius=face_z-face_g, axis=(0,0,1), color=(0,0,0) ) )

		self.blocks = []
		for i in [-1, 0, 1]:
			for j in [-1, 0, 1]:
				for k in [-1, 0, 1]:
					if i == 0 and j == 0 and k == 0:
						continue
					self.blocks.append( Block( self, i, j, k ) )

		self.rotating_time = 0
		self.rotating_surfaces = []
		self.rotating_blocks = []
		self.rotating_axle = None
		for axle in self.axles:
			axle.opacity = axle_opacity

		self.load_surfaces_into_blocks()

		self.selected_block = len(self.blocks) - 1
		self.previous_colors = []

	def get_axle(self, direction):
		return self.axles[ self.axlemap[ direction ] ]

	def orient(self, front=None, up=None):
		if front is None and up is None:
			self.axlemap = { 'U': 0, 'D': 1, 'L': 2, 'R': 3, 'F': 4, 'B': 5 }
			return
		if front is None:
			front = self.get_axle('F')
		left = front.rotate(angle=radians(90), axis=up)
		if up is None:
			up = self.get_axle('U').pos
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
		for b in range(len(self.blocks)):
			avg_color = vector(0,0,0)
			block = self.blocks[b]
			for s in block.surfaces:
				avg_color += s.color
			avg_color /= len(block.surfaces)
			block.color = avg_color
			block.blind.color = avg_color * 0.2


	def rotate(self, d):
		if self.rotating_axle is not None or self.rotating_time != 0:
			return

		for axle in self.axles:
			axle.opacity = 0.0

		if d == d.lower():
			self.clockwise = -1;
		else:
			self.clockwise =  1
		self.start_rotation( self.get_axle( d.upper() ) )

	def start_rotation(self, axle):
		self.rotating_axle = axle
		self.rotating_surfaces = []
		self.rotating_blocks = []

		blocks = axle.get_blocks()
		for block in blocks:
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

	def tick(self):
		self.do_rotation()

	def do_rotation(self):
		if self.rotating_axle:
			axle = self.rotating_axle
			axle.rotate(angle=radians(-self.d_theta * self.clockwise), axis=axle.pos, origin=axle.pos)
			for s in self.rotating_surfaces:
				s.rotate(angle=radians(-self.d_theta * self.clockwise), axis=axle.pos, origin=axle.pos)
				s.normal = zero_epsilon( s.normal.rotate(angle=radians(-self.d_theta * self.clockwise), axis=axle.pos) )
			for b in self.rotating_blocks:
				b.rotate(angle=radians(-self.d_theta * self.clockwise), axis=axle.pos, origin=axle.pos)
			self.rotating_time += self.d_theta
			if self.rotating_time >= 90:
				self.stop_rotation()

	def stop_rotation(self):
		print self.rotating_axle.north
		#print self.rotating_blocks[0].coordinate
		#print self.blocks[ self.selected_block ].coordinate
		self.rotating_axle = None
		self.rotating_surfaces = []
		self.rotating_blocks = []
		self.rotating_time = 0
		for axle in self.axles:
			axle.opacity = axle_opacity

	def select_block(self, select):
		if isinstance(select, tuple) or isinstance(select, vector):
			for b in range(len(self.blocks)):
				#print self.blocks[b].coordinate
				if mag(self.blocks[b].coordinate - select) < epsilon:
					select = b
					break
			if not isinstance(select, int):
				print "invalid selection ", select
				return
		select %= len(self.blocks)
		block = self.blocks[ self.selected_block ]
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
		block.opacity = 0.2
	
