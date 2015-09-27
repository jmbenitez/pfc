from libreria import *
from punto3 import *

class libDatos:


	def __init__(self):
		''' ========================= VARIABLES GLOBALES ========================='''
		self.GPS 		= None
		self.IMU 		= None
		self.VEL 		= None
		self.throttle	= None

		# Flags
		self.deteccion		 	= False
		self.estimacionDisponible 	= False

		# Calibracion
		self.anguloVision 	= 28.97
		self.centroPistaGPS 	= Punto3( -5.787567,37.147102, 33.5)
		self.orientacionPista	= 246
		self.alturaUmbral 	= 10
		self.distanciaMinima	= 400

		# Rango de aceptacion
		self.anguloAceptacion 		= Punto(18, 14)
		self.margenX	= self.interpolacionLineal(self.anguloAceptacion.x)
		self.margenY	= self.interpolacionLineal(self.anguloAceptacion.y)
		self.cuadroAceptacion	= [Punto(ancho/2-self.margenX, alto/2-self.margenY), Punto(ancho/2-self.margenX,self.margenY + alto/2), Punto(self.margenX + ancho/2, alto/2-self.margenY), Punto(self.margenX + ancho/2, self.margenY + alto/2)]

		# Puntos de inicio
		self.puntoEstimacion1		= None
		self.puntoEstimacion2 		= None

		self.punto1	= None
		self.punto2 = None
		self.punto3 = None

	''' ========================= METODOS ============================= '''
	# Las variables globales necesitan ser declaradas si se van a modificar, si es solo lectura leen
	def calculoPuntoOrigen (self):
		
		# El origen de coordenadas para el avion seran las coordenadas gps
		# self.GPS  es el origen de coordenadas


		# Para hallar el vector AB donde A = avion y B = pista
		#  AB = B - A
		# Nota: se transforma a metros para tener todas las unidades en el mismo sistema
		distanciaGPS 	= self.centroPistaGPS - self.GPS
		distanciaMetros	= coord2metros(distanciaGPS)

		if debug:
			print "GPS", self.GPS
			print "IMU", self.IMU
			print "VEL", self.VEL
			print "dist", distanciaMetros
			print


		norte 		= Punto3(0,1,0)
		vectorObjetivo	= distanciaMetros

		# Hallar angulo hacia la pista
		anguloObjetivo		= norte.angulo(vectorObjetivo)
		if anguloObjetivo.z < 0: anguloObjetivo.z += 360
		orientacionObjetivo	= anguloObjetivo.z



		# Necesito hallar 2 angulos entre vector direccion y vector objetivo
		# 	angulo horizontal : se halla de la diferencia en la orientacion (eje z)
		#	angulo vertical	: hay que igualar el angulo de z y situarlo en norte, hallar el angulo de x


		''' Opcion 1: velocidad GPS como referencia de direccion '''
		if debug:
			print "Referencia VEL"
		# Calcular el angulo horizontal desde el vector velocidad GPS hacia el vector distancia
		vectorDireccion	= self.VEL		
		vectorDireccion.rotacionZ(- 180)

		anguloDireccion	= norte.angulo(vectorDireccion)
		anguloDireccion.z	= anguloDireccion.z % 360

		# angulo horizontal
		orientacionDireccion = anguloDireccion.z
		if debug:
			print "orientacion", orientacionObjetivo, orientacionDireccion
		anguloHorizontal1 = orientacionObjetivo - orientacionDireccion
		if debug:
			print "angulo H", anguloHorizontal1
		
		# angulo vertical
		vectorObjetivo.rotacionZ(- orientacionObjetivo)
		vectorDireccion.rotacionZ( - orientacionDireccion)
		anguloVertical1 = vectorObjetivo.angulo(vectorDireccion)
		# Al ser la diferencia entre vector distancia y velocidad hay que sumarle el pitch
		anguloVertical1 = anguloVertical1.x - self.IMU.y
		if debug:
			print "angulo V", anguloVertical1


		# Punto principal: 
		x1 	= self.interpolacionLineal(anguloHorizontal1) + ancho/2
		y1	= self.interpolacionLineal(anguloVertical1) + alto/2


		if debug:
			print
			print "Referencia IMU"

		''' Opcion 2: vector IMU como referencia de direccion '''
		distanciaMetros	= coord2metros(distanciaGPS)
		norte 		= Punto3(0,1,0)
		vectorObjetivo	= distanciaMetros

		# Hallar angulo hacia la pista
		anguloObjetivo		= norte.angulo(vectorObjetivo)
		if anguloObjetivo.z < 0: anguloObjetivo.z += 360
		orientacionObjetivo	= anguloObjetivo.z


		# Calcular el angulo desde el vector IMU hacia el vector distancia
		anguloDireccion		= self.IMU
		orientacionDireccion	= anguloDireccion.z
		vectorDireccion		= norte
		vectorDireccion.rotacionX(anguloDireccion.y)
		vectorDireccion.rotacionY(anguloDireccion.x)
		vectorDireccion.rotacionZ(orientacionDireccion)

		# angulo horizontal
		if debug:
			print "orientacion", orientacionObjetivo, orientacionDireccion
		anguloHorizontal2 = orientacionObjetivo - orientacionDireccion
		if debug:
			print "angulo H", anguloHorizontal2

		# angulo vertical
		vectorObjetivo.rotacionZ(- orientacionObjetivo)
		vectorDireccion.rotacionZ( - orientacionDireccion)
		anguloVertical2 = vectorObjetivo.angulo(vectorDireccion)
		anguloVertical2 = anguloVertical2.x
		if debug:
			print "angulo V", anguloVertical2

		# Punto secundario: 
		x2 	= self.interpolacionLineal(anguloHorizontal2) + ancho/2
		y2	= self.interpolacionLineal(anguloVertical2) + alto/2



		x3 	= self.interpolacionLineal(orientacionObjetivo - abs(self.orientacionPista-180)) + ancho/2
		if x3 < 0 or x3 > ancho:
			x3	= self.interpolacionLineal(orientacionObjetivo - self.orientacionPista) + ancho/2

		


		# Linea roja = x1
		# Linea azul = y2
		# Linea verde = x3

		# Condicion necesaria: 
		#	linea roja dentro de la imagen
		#	altura minima de 10 metros
		
		# Primer intento. Punto medio	
		# Segundo intento. Punto verde-azul (IMU)
		# Tercer intento. Punto rojo-azul	(VEL)
		

		punto1 = Punto(x3,y2)
		punto2 = Punto(x1, y2)
		punto3 = Punto((x1 + x3)/2, y2)

		# Rectificar ROLL
		centro = Punto(ancho/2, alto/2)
		roll = self.IMU.x
		punto1.giro(centro, roll)
		punto2.giro(centro, roll)
		punto3.giro(centro, roll)

		self.punto1 = punto1
		self.punto2 = punto2
		self.punto3 = punto3

		self.deteccion = punto3.x > 20 and punto3.x < ancho-20 and \
					punto3.y > 20 and punto3.y < alto-20 and \
					abs(distanciaGPS.z) > self.alturaUmbral and \
					distanciaGPS.norma() < self.distanciaMinima
		
		if not self.puntoAceptado(punto1):
			punto1 = None
		if not self.puntoAceptado(punto2):
			punto2 = None
		if not self.puntoAceptado(punto3):
			punto3 = None

		# Condiciones para la deteccion
		# El rumbo debe estar dentro del rango (solo medible mediante VEL)
		# La deteccion necesita realizarse a mas de 10 metros de altura
		self.deteccion = True if (punto2) and  abs(distanciaGPS.z) > 10 else False
		
		if debug:
			print "calculos", punto1, punto2, punto3
		return punto1, punto2, punto3





	# El sistema de referencia GPS es (lat, lon, alt)
	# Esto significa que 
	#	el eje y corresponde a latitud
	#	el eje x corresponde a longitud
	# 	el eje z corresponde a altitud
	

	def recogerMensajes(self, datos):
		# ATTITUDE
		msg 	= datos.msgs['ATTITUDE']
		roll 	= math.degrees(msg.roll)
		pitch	= math.degrees(msg.pitch) -1.875
		yaw 	= msg.yaw + math.radians(17.83)#+ math.radians(27.83)
		yaw 	= math.degrees(yaw) % 360
		#if yaw < 0: yaw += 360
		#pdb.set_trace()
		# GPS
		msg 	= datos.msgs['GLOBAL_POSITION_INT']
		lat	= msg.lat / 1.0e7 + 2.4e-05 # Con calibracion
		lon 	= msg.lon / 1.0e7 - 2.8e-05 # Con calibracion
		alt 	= msg.alt / 1.0e3
		vx 	= msg.vx / 100.0
		vy 	= msg.vy / 100.0
		
		# VFR_HUD
		msg 	= datos.msgs['VFR_HUD']
		climb = float(msg.climb)


		self.GPS 		= Punto3(lon, lat, alt)
		self.IMU 		= Punto3(roll, pitch, yaw)
		self.VEL 		= Punto3(-vy, -vx, climb) # vx y vy hacen referencia a lon y lat respectiv
		self.throttle 	= float(msg.throttle)
	


	def calculaEstimacion(self, puntos):
		puntoMedio1 = puntos[0] + (puntos[1] - puntos[0])/3
		puntoMedio2 = puntos[2] + (puntos[3] - puntos[2])/3
		tercio = (puntoMedio2 - puntoMedio1)/3
		puntoMedio1 = puntoMedio1 + tercio
		puntoMedio2 = puntoMedio2 - tercio
		self.puntoEstimacion1 = puntoMedio1
		self.puntoEstimacion2 = puntoMedio2

		self.puntoEstimacion1 = puntoMedio1 if self.puntoAceptado(puntoMedio1) else None
		self.puntoEstimacion2 = puntoMedio2 if self.puntoAceptado(puntoMedio2) else None

		if self.puntoEstimacion1 is not None or self.puntoEstimacion2 is not None:
			self.estimacionDisponible = True
		else:
			self.estimacionDisponible = False

		print "estimaciones", self.puntoEstimacion1, self.puntoEstimacion2



	def interpolacionLineal(self, y2):
		return ((y2 + self.anguloVision)*(ancho - 0) / (self.anguloVision * 2)) - ancho/2

	def puntoAceptado(self, punto):
		if punto is None:
			return False

		return punto.x > ancho/2 - self.margenX and punto.x < ancho/2 + self.margenX \
			and punto.y > alto/2 - self.margenY and punto.y < alto/2 + self.margenY


def coord2metros(coord):
	if coord.__class__.__name__ == 'Punto3':
		return Punto3(coord2metros(coord.x), coord2metros(coord.y), coord.z)
	return coord / 1.08904e-5






