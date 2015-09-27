from __future__ import division
from punto import *
import math

class Recta:
	def __init__(self, *args, **coefs):
		# Especificada cada variable por separado (a=1, b=2, c=3)
		self.a = coefs['a'] if 'a' in coefs else 0
		self.b = coefs['b'] if 'b' in coefs else 0
		self.c = coefs['c'] if 'c' in coefs else 0
		# Especificado directamente
		if len(args) == 3:	
			self.a = args[0]
			self.b = args[1]
			self.c = args[2]
		# Una recta a partir de 2 puntos
		if len(args) == 2:		
			punto1 = args[0]
			punto2 = args[1]
			self.a = punto2.y - punto1.y
			self.b = punto1.x - punto2.x
			self.c = ( punto2.x * punto1.y ) - ( punto1.x * punto2.y )
			

	def __str__( self ):
		return '%.2fx %.2fy %.2f' % (self.a, self.b, self.c)
	def __repr__(self):
		return str(self)

	def pendiente(self):
		# Recta vertical
		if self.b == 0:
			return float('inf')
		# Otras
		else:
			return - ( self.a / self.b )

	def pertenece(self, punto):
		if punto == None:
			raise Exception('Argumento con valor None')
		if self.b == 0:
			return (- self.c/self.a) == punto.x
		return int(self.resolver(x=punto.x)) == punto.y


	def distanciaAPunto(self, punto):
		if punto == None:
			raise Exception('Argumento con valor None')
		if self.b == 0:
			return abs(self.resolver(y=0) - punto.x)

		return abs( (self.a * punto.x + self.b * punto.y + self.c) / (math.sqrt(self.a**2 + self.b**2)) )

	def rectaPerpendicularEnPunto(self, punto):
		if self.b == 0:
			return Recta( Punto(self.resolver(y=0), punto.y), punto)
		
		m = - self.pendiente**-1
		a = m
		b = -1 
		c = punto.y - (punto.x * m)
		return Recta(a,b,c)
	
	def resolver(self, **valor):
		if 'x' in valor:
			return (- self.a * valor['x'] - self.c)/self.b
		if 'y' in valor:
			return (- self.b * valor['y'] - self.c)/self.a



	def puntoCorte(self, recta):
		# Rectas paralelas		
		if self.paralelas(recta):
			print "Rectas paralelas"
			return inf('inf')

		# Alguna recta es vertical
		if self.b == 0:
			return Punto(self.resolver(y=0), recta.resolver(x=(- self.c/self.a)))
		if recta.b == 0:
			return Punto(recta.resolver(y=0), self.resolver(x=(- recta.c/recta.a)))

		#Metodo reduccion (reducimos la x)
		recta *= ( -self.a/recta.a )		
		div = self + recta #Recta con A=0
		y = - div.c/div.b
		x = self.resolver(y=y)
		return Punto(x,y)
		
	def paralelas(self, recta):
		# Ambas rectas verticales
		if self.b == None and recta.b == None:
			return True
		# Solo una vertical
		elif self.b == None or recta.b == None:
			return False
		# Ninguna vertical
		else:
			try:
				return (self.a/recta.a)==(self.b/recta.b)
			except:
				print "No se pudo dividir"
				print self, recta

	def angulo(self, recta):
		if self.paralelas(recta):
			return "Rectas paralelas"

		vector1 = Punto( - self.b , self.a )
		vector2 = Punto( - recta.b, recta.a )
		num = abs(vector1.x * vector2.x + vector1.y * vector2.y)
		den = math.sqrt(vector1.x**2 + vector1.y**2) * math.sqrt(vector2.x**2 + vector2.y**2)
		return math.degrees(math.acos(num/den))


	def giro (self, punto, giro):
		punto1 = Punto( self.resolver(y = 1000), 1000 )
		punto2 = Punto( self.resolver(y = -1000), -1000 )

		punto1.giro(punto, giro)
		punto2.giro(punto, giro)

		recta = Recta(punto1, punto2)
		self.a = recta.a
		self.b = recta.b
		self.c = recta.c

	def desplazar(self, x, y):
		self.c += (- x * self.a) + (y * self.b)


	def copy(self):
		return Recta(self.a, self.b, self.c)

	def __add__(self, recta):		
		return Recta(self.a + recta.a, self.b + recta.b, self.c + recta.c)

	def __mul__(self, factor):
		return Recta(self.a * factor, self.b * factor, self.c * factor)

	def __eq__(self, other):
		return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)

	def __ne__(self, other):
		return not self.__eq__(other)

