import random
from cube import *

class Solver:
	stages = {
		'north_cross':[
			'rotate_top_edges',
			'flip_top_edge',
		],
		'north_corners':[
			'top_corner_down',
			'bottom_corner_up',
		],
		'middle_layer':[
			'top_edge_to_right',
			'top_edge_to_left',
		],
		'south_edges':[
			'make_bend',
			'make_line',
			'make_bend',
		],
		'south_corners':[
			'toggle_corners',
			'swap_corners',
		],
		'south_edges':[
			'efgh_clockwise',
			'efgh_counter',
		],
		'centers':[
			'center_90',
			'center_180',
			'center_270',
		],
	}
	sequences = {
		'rotate_top_edges':  ['l','l','r','r','D','D','L','L','R','R'],
		'flip_top_edge':     ['r','U','f','u'],
		'bottom_corner_up':  ['r','d','R','D'],
		'top_corner_down':   ['r','d','R'],
		'top_edge_to_right': ['U','R','u','r','u','f','U','F'],
		'top_edge_to_left':  ['u','l','U','L','U','F','u','f'],
		'make_bend':         ['F','U','R','u','r','f'],
		'make_line':         ['F','R','U','r','u','f'],
		'toggle_corners':    ['R','U','r','U','R','u','u','r'],
		'swap_corners':      ['r','F','r','B','B','R','f','r','B','B','R','R','u'],
		'efgh_clockwise':    ['F','F','U','L','r','F','F','l','R','U','F','F'],
		'efgh_counter':      ['F','F','u','L','r','F','F','l','R','u','F','F'],
		# requires V,v,H,h moves
		'center_90':         ['v','h','V','U','v','H','V','u'],
		'center_180':        ['U','R','L','U','U','r','l','U','R','L','U','U','r','l'],
		'center_270':        ['U','v','h','V','u','v','H','V'],
		# non-solid pattern solutions
		'multi_cross':       ['R','R','L','L','U','U','D','D','F','F','B','B'],
		'middle_square':     ['R','l','U','d','f','B','R','l'],
	}
	def __init__(self, cube):
		self.block_queue = []
		self.queue = []
		self.countdown = 0
		self.cube = cube

	def locate(self, colors):
		c0 = set([self.cube.palette[x].astuple() for x in colors])
		#print c0
		for block in self.cube.blocks:
			c1 = set([b.color for b in block.surfaces])
			#print c1
			if c0 == c1:
				return self.cube.blocks.index(block)

	def orient_front(self, c):
		cube.orient( cube.axles[c].pos )

	def orient_top(self, c):
		cube.orient( None, cube.axles[c].pos )

	def north_cross(self):
		top_c = 0
		if top_c % 2 == 0:
			bottom_c = top_c + 1
		else:
			bottom_c = top_c - 1

		self.orient_top(top_c)
		for c in range(0,5):
			self.orient_front(c)
			if c == top_c or c == bottom_c:
				continue
			block = self.locate([top_c, c])
			self.move('flip_edge', block)

	def move(self, sequence, block=None):
		for s in self.sequences[sequence]:
			self.block_queue.insert(0, block)
			self.queue.insert(0, s)
			self.countdown += 1
	
	def tick(self):
		self.check_queue()
		if self.countdown > 0:
			if self.cube.rotating_axle is None:
				#self.white_cross()
				block = self.block_queue.pop()
				if block:
					self.cube.select_block( block )
				self.countdown -= 1

	def scramble(self):
		self.cube.d_theta = 15
		for t in range(20):
			rnd = random.randint(0,11)
			self.queue.append(['U','D','L','R','F','B','u','d','l','r','f','b'][rnd])

	def check_queue(self):
		if len(self.queue) > 0:
			if self.cube.rotating_axle is None:
				rot = self.queue.pop()
				self.cube.rotate(rot)
		else:
			self.cube.d_theta = Cube.normal_d_theta


	def overall_metric(self):
		N = 0
		for b in self.cube.blocks:
			m = mag(b.coordinate - b.expected_coordinate)
			if m < epsilon:
				m = 0
			N -= m
		return N

	def face_metric(self, direction):
		axle = self.cube.get_axle( direction )
		blocks = axle.get_blocks()
		center_block = axle.get_center_block()
		center = center_block.surfaces[0].normal
		N = 0
		for b in blocks:
			for s in b.surfaces:
				if s.color == center_block.surfaces[0].color:
					if mag(s.normal - center) < epsilon:
						N += 1
		return N

	def face_edge_metric(self, direction):
		axle = cube.get_axle(direction)
		center_block = axle.get_center_block()
		for b in axle.get_edge_blocks():
			print [c for c in b.get_colors()]
