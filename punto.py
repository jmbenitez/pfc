import math

class Punto:
	def __init__(self, *args, **coords):
		self.x = coords['x'] if 'x' in coords else 0
		self.y = coords['y'] if 'y' in coords else 0	
		if len(args) == 2:
			self.x = int(args[0])
			self.y = int(args[1])
		if not isinstance(self.x, int):
			self.x = int(self.x)
		if not isinstance(self.y, int):
			self.y = int(self.y)
				

	def __str__( self ):
		return '(%d, %d)' % (self.x, self.y)
	def __repr__(self):
		return str(self)
	def __add__(self, punto):
		return Punto(int(self.x + punto.x), int(self.y + punto.y))

	def __sub__(self, punto):
		return Punto(self.x - punto.x, self.y - punto.y)

	def __mul__(self, factor):
		return Punto(self.x * factor, self.y * factor)

	def __div__(self, factor):
		return Punto(self.x / factor, self.y / factor)

	def distancia(self, punto):
		return math.sqrt( (self.x - punto.x) ** 2 + (self.y - punto.y) ** 2 )

	def copy(self):
		return Punto(self.x, self.y)

	# Agujas del reloj = negativo
	def giro(self, punto, giro):
		giro = -giro
		rx = self.x - punto.x
		ry = self.y - punto.y

		x = rx * math.cos( math.radians( giro ) ) - ry * math.sin( math.radians( giro ) )
		y = rx * math.sin( math.radians( giro ) ) + ry * math.cos( math.radians( giro ) ) 

		self.x = int(x) + punto.x
		self.y = int(y) + punto.y
