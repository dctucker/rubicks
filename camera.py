from visual import *

epsilon = 0.0000001

class Camera:
	def __init__(self, scene, cube):
		self.d_theta_x = 0
		self.d_theta_y = 0
		self.d_theta_z = 0
		self.axis = vector(1,0,0)
		self.x_axis = vector(0,0,0)
		self.theta_remaining = 0

		self.mirrors = []
		self.scene = scene
		self.cube = cube
		self.scene.fov = radians(30)

	def tick(self):
		if self.cube.rotating_axle is None:
			self.x_axis = self.cube.frame.frame_to_world( self.cube.get_axle('U').get_center_block().pos )
		if self.theta_remaining == 0:
			self.cube.frame.rotate( angle=self.d_theta_x, axis=self.x_axis )
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

		#if self.d_theta_y != 0:
		#	for mirror in self.mirrors:
		#		if mirror.axle == 'L':
		#			mirror.frame.rotate(angle=-self.d_theta_y, axis=(0,0,1))
		#		if mirror.axle == 'R':
		#			mirror.frame.rotate(angle=self.d_theta_y, axis=(0,0,1))
		#if self.d_theta_x != 0:
		#	for mirror in self.mirrors:
		#		if mirror.axle == 'U':
		#			mirror.frame.rotate(angle=self.d_theta_x, axis=(0,0,1))
		#		elif mirror.axle == 'D':
		#			mirror.frame.rotate(angle=-self.d_theta_x, axis=(0,0,1))

		for mirror in self.mirrors:
			mirror.tick()

	def orient(self):
		f = self.cube.frame
		self.cube.orient(f.world_to_frame(self.scene.forward), f.world_to_frame(self.scene.up))
		for mirror in self.mirrors:
			mirror.needs_update = True

	def snap_to_block(self):
		origin = vector(self.cube.frame.axis)

		sel_pos = self.cube.frame.frame_to_world( self.cube.blocks[ self.cube.selected_block ].pos )
		sel_pos = norm(sel_pos)
		n = -scene.forward
		angle = -diff_angle( n, sel_pos )
		axis = n.cross( sel_pos )
		#self.cube.frame.rotate( angle=angle, axis=axis )

		self.theta_remaining = angle
		self.axis = axis

class Double:
	def __init__(self, cube):
		self.cube = cube
		self.frame = frame( pos=(-3.5,-2.5, -7) )
		shield   = box( frame=self.frame, pos=(-0.5,   0, 2), size=(4.4,2.9,0), color=color.gray(0.1), opacity=0.3, material=materials.shiny)
		backdrop = box( frame=self.frame, pos=(-0.7,-0.75,-2), size=(4  ,  4,0), color=(0.1,0.15,0.2), opacity=0.4, material=materials.unshaded)
		#shield.rotate(angle=radians(-15), axis=(1,0,0), origin=(0,0,0))
		#shield.rotate(angle=radians( 15), axis=(0,1,0), origin=(0,0,0))
		self.blocks = []
		self.surfaces = []
		for b in range(len(self.cube.blocks)):
			self.blocks.append([])
			for s in range(len(self.cube.blocks[b].surfaces)):
				surface = self.cube.blocks[b].surfaces[s]
				size = vector(0.35,0.35,0.35) * 0.5
				newbox = box( frame=self.frame, pos=surface.pos, size=size, color=surface.color )
				newbox.rotate(angle=radians(45), axis=(1,1,0), origin=(0,0,0))
				newbox.material = materials.rough
				self.blocks[b].append( newbox )

	def tick(self):
		for b in range(len(self.cube.blocks)):
			for s in range(len(self.cube.blocks[b].surfaces)):
				surface = self.cube.blocks[b].surfaces[s]
				pos = -surface.pos * 0.5
				self.blocks[b][s].pos = self.cube.frame.frame_to_world( pos )
				#self.blocks[b][s].axis = surface.axis

class Mirror:
	def __init__(self, cube, axle, pos, rotate):
		self.frame = frame( pos=pos )
		self.needs_update = True
		self.axle = axle
		#self.ref_axle = ref_axle
		self.rotate = rotate
		self.cube = cube
		self.facets = [];
		size = 0.2
		for i in [ -1, 0, 1 ]:
			self.facets.append([])
			for j in [ -1, 0, 1 ]:
				p = vector(j, i, 0) * size * 1.05
				self.facets[i+1].append( box( frame=self.frame, pos=p, size=(size,size,0.01), color=(1,0,1) ) )

	def tick(self):
		if self.cube.rotating_axle is not None:
			self.needs_update = True
			return
		if not self.needs_update:
			return
		axle = self.cube.get_axle(self.axle)
		center = axle.get_center_block()
		axes = []
		rot = self.rotate
		tilt = diff_angle( self.cube.get_axle('U').pos, axle.pos )
		#print center.coordinate, ref_center.coordinate, rot
		for i in range(len(center.coordinate)):
			if abs(center.coordinate[i]) < epsilon:
				axes.append(i)

		for b in axle.get_blocks():
			v = vector( b.coordinate[ axes[0] ], b.coordinate[ axes[1] ] )
			v = v.rotate(angle=rot, axis=(0,0,1))
			v = v.rotate(angle=tilt, axis=(0,0,1))
			bi = int(round(v.x))
			bj = int(round(v.y))
			for s in b.surfaces:
				if mag(s.normal - center.surfaces[0].normal) < epsilon:
					#print v, bi,bj
					self.facets[ bi + 1 ][ bj + 1 ].color = s.color

		self.needs_update = False
