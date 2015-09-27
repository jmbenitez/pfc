import math

class Punto3:
	def __init__(self, *args, **coords):
		self.x = coords['x'] if 'x' in coords else 0
		self.y = coords['y'] if 'y' in coords else 0
		self.z = coords['z'] if 'z' in coords else 0
		if len(args) == 3:
			self.x = args[0]
			self.y = args[1]
			self.z = args[2]
				

	def __str__( self ):
		return '(%.4f, %.4f, %.4f)' % (self.x, self.y, self.z)
	def __repr__(self):
		return str(self)
	def __add__(self, punto):
		return Punto3(self.x + punto.x, self.y + punto.y, self.z + punto.z)

	def __sub__(self, punto):
		return Punto3(self.x - punto.x, self.y - punto.y, self.z - punto.z)

	def __mul__(self, factor):
		return Punto3(self.x * factor, self.y * factor, self.z * factor)


	def __div__(self, factor):
		return Punto3(self.x / factor, self.y / factor, self.z/factor)

	def distancia(self, punto):
		return self - punto

	def copy(self):
		return Punto3(self.x, self.y, self.z)

	def crossProduct(v1, v2):
		x = v1.y*v2.z - v1.z*v2.y
		y = v1.z*v2.x - v1.x*v2.z
		z = v1.x*v2.y - v1.y*v2.x
		return Punto3(x,y,z)

	def norma(self):
		return math.sqrt(self.x**2 + self.y**2 + self.z**2)


	# Calcula el angulo de dos puntos respecto al origen
	def angulo(self, punto3):
		# Para medir los angulos hay que ir poniendo las coordenadas a 0
		cross = Punto3.crossProduct(self, punto3)

		vector1 = self.copy()
		vector2 = punto3.copy()
		vector1.x = 0
		vector2.x = 0
		num = vector1.z * vector2.z + vector1.y * vector2.y
		den = vector1.norma() * vector2.norma()
		anguloX = 0		
		if den != 0:
			anguloX = math.degrees(math.acos(num/den))
		if cross.x < 0:
			anguloX = - anguloX


		vector1 = self.copy()
		vector2 = punto3.copy()
		vector1.y = 0
		vector2.y = 0
		num = vector1.x * vector2.x + vector1.z * vector2.z
		den = vector1.norma() * vector2.norma()
		anguloY = 0
		if den != 0:
			anguloY = math.degrees(math.acos(num/den))
		if cross.y < 0:
			anguloY = - anguloY

		vector1 = self.copy()
		vector2 = punto3.copy()
		vector1.z = 0
		vector2.z = 0
		num = vector1.x * vector2.x + vector1.y * vector2.y
		den = vector1.norma() * vector2.norma()
		anguloZ = 0
		if den != 0:
			menor = min(1, num/den)
			anguloZ = math.degrees(math.acos(menor))
		if cross.z > 0:
			anguloZ = - anguloZ


		return Punto3(anguloX, anguloY, anguloZ)

		


	# Agujas del reloj = negativo
	def rotacionZ(self, rotacion):
		rotacion = - math.radians(rotacion)

		# rotacionZ
		x = self.x * math.cos(rotacion) - self.y * math.sin(rotacion)
		y = self.x * math.sin(rotacion) + self.y * math.cos(rotacion)
		z = self.z

		self.x = x
		self.y = y
		self.z = z

	def rotacionX(self, rotacion):
		rotacion = math.radians(rotacion)

		# rotacionX
		x = self.x
		y = self.y * math.cos(rotacion) - self.z * math.sin(rotacion)
		z = self.y * math.sin(rotacion) + self.z * math.cos(rotacion)

		self.x = x
		self.y = y
		self.z = z

	def rotacionY(self, rotacion):
		rotacion = math.radians(rotacion)

		# rotacionY
		x = self.x * math.cos(rotacion) + self.z * math.sin(rotacion)
		y = self.y
		z = - self.x * math.sin(rotacion) + self.z * math.cos(rotacion)

		self.x = x
		self.y = y
		self.z = z
