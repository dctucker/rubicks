
class Solver:
	sequences = {
		'rotate_top_edges': ['l','l','r','r','D','D','L','L','R','R'],
		'flip_edge': ['r','U','f','u'],
		'bottom_corner_up': ['r','d','R','D'],
	}
	def __init__(self, cube, queue):
		self.block_queue = []
		self.cube = cube
		self.queue = queue
		self.countdown = 0

	def locate(self, colors):
		c0 = set([self.cube.palette[x].astuple() for x in colors])
		#print c0
		for block in self.cube.blocks:
			c1 = set([b.color for b in block.surfaces])
			#print c1
			if c0 == c1:
				return self.cube.blocks.index(block)

	def white_cross(self):
		top_c = 0
		if top_c % 2 == 0:
			bottom_c = top_c + 1
		else:
			bottom_c = top_c - 1
		for c in range(0,5):
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
		if self.countdown > 0:
			if self.cube.rotating_axle is None:
				#self.white_cross()
				block = self.block_queue.pop()
				if block:
					self.cube.select_block( block )
				self.countdown -= 1

