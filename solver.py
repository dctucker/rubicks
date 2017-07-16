
class Solver:
	sequences = {
		'flip_edge': ['r','U','f','u'],
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
			self.move( block, self.sequences['flip_edge'] )

	def move(self, block, sequence):
		for s in sequence:
			self.block_queue.append(block)
			self.queue.append(s)
			self.countdown += 1
	
	def tick(self):
		if self.countdown > 0:
			if self.cube.rotating_axle is None:
				#self.white_cross()
				self.cube.select_block( self.block_queue.pop() )
				self.countdown -= 1

