import cv2
import numpy as np
from punto import *
from recta import *
from linea import *

''' ========================= VARIABLES GLOBALES ========================='''
debug = False

alto  = 480
ancho = 640


mascaraFlancos = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
mascaraMedias = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]], dtype="float")/9
motionBlur0 = np.zeros((9,9))
motionBlur0[4] = np.ones(9)
motionBlur90 = cv2.transpose(motionBlur0)/9


''' ========================= EXCEPCIONES ========================='''

class PistaNoEncontradaException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)





''' ========================= METODOS DEL ALGORITMO ============================= '''
def programa(imgOriginal, x, y):
	global alto, ancho

	#alto, ancho = imgOriginal.shape[:2]

	# Seleccionar punto origen 
	punto0 = Punto(x,y)
	if debug:
		print "encontrar pista", punto0

	# Preprocesado
	imgUmbralizada = preprocesado(imgOriginal)

	# Segmentacion
	recortes, puntos, angulos = segmentacion(imgUmbralizada, punto0)

	# Analisis
	puntosI = analisis(recortes[0], puntos[0], 127)
	puntosD = analisis(recortes[1], puntos[1], 127)

	#	Deshacer el giro
	puntosI[0].giro(puntos[0], - angulos[0])
	puntosI[1].giro(puntos[0], - angulos[0])
	puntosD[0].giro(puntos[1], - angulos[1])
	puntosD[1].giro(puntos[1], - angulos[1])


	# Posprocesado: chequeo cuadrialtero
	puntos = puntosI + puntosD
	return puntos


def preprocesado (imgOriginal):
	# Paso 0: Convertir a B&N 
	imgByn = cv2.cvtColor(imgOriginal, cv2.COLOR_BGR2GRAY)

	# Paso 1: Aplicar operador de Flancos
	imgFlancos = cv2.filter2D(imgByn, -1, mascaraFlancos)

	# Paso 2: Aplicar operador de Media Aritmetica
	imgMedias = cv2.filter2D(imgFlancos, -1, mascaraMedias)

	# Paso 3: Aplicar filtro Umbral (valor = 50)
	_, imgUmbralizada = cv2.threshold(imgMedias,50,255,cv2.THRESH_BINARY)

	return imgUmbralizada


def segmentacion (imgUmbralizada, punto0):
	# Paso 1: Deteccion de lados
	#	- Expansion Horizontal

	# Se hacen 3 intentos de encontrar los margenes
	puntoI, puntoD = ExpansionHorizontalRecursivo(imgUmbralizada, punto0)


	# 	- Expansion Vertical
	# 		Izquierda
	direccion = -1
	linea1 = ExpansionVerticalRecursivo(imgUmbralizada, puntoI, direccion)

	#		Derecha
	direccion = 1
	linea2 = ExpansionVerticalRecursivo(imgUmbralizada, puntoD, direccion)
	

	puntoI = linea1.punto
	puntoD = linea2.punto


	# Paso 2: Giro de lados
	angulo1 = calcularGiro(linea1)
	angulo2 = calcularGiro(linea2)

	anchura = 4
	imgGiradaI = girarImagen(imgUmbralizada, puntoI, angulo1)
	imgGiradaD = girarImagen(imgUmbralizada, puntoD, angulo2)


	# Paso 3: Recortar rectas
	# 	[col1:col2, fila1:fila2]
	imgRecorteI = imgGiradaI[0:alto, puntoI.x - anchura: puntoI.x + anchura + 1] 	
	imgRecorteD = imgGiradaD[0:alto, puntoD.x - anchura: puntoD.x + anchura + 1] 

	return [imgRecorteI, imgRecorteD], [puntoI, puntoD], [angulo1, angulo2]



def analisis(imgRecorte, punto, umbral):
	# Paso 1: Aplicar operador desenfoque de movimiento 90 grados
	imgRecorte = cv2.filter2D(imgRecorte, -1, motionBlur90)

	# Paso 2: Aplicar filtro Umbral
	_, imgRecorte = cv2.threshold(imgRecorte,umbral,255,cv2.THRESH_BINARY)
	
	# Paso 3: Aplicar 2 iteraciones de desenfoque de movimiento 0 grados
	imgRecorte = cv2.filter2D(imgRecorte, -1, motionBlur0)	
	imgRecorte = cv2.filter2D(imgRecorte, -1, motionBlur0)


	# Paso 4: Deteccion
	puntoAImagen, puntoBImagen = Punto(punto.x, 0), Punto(punto.x,ancho - 1)

	for fila in xrange(punto.y, -1, -1):
		if imgRecorte[fila, 4] == 0:
			puntoAImagen = Punto(punto.x, fila + 1)
			break

	for fila in xrange(punto.y, alto):
		if imgRecorte[fila, 4] == 0:
			puntoBImagen = Punto(punto.x, fila - 1)
			break
	
	return [puntoAImagen, puntoBImagen]
	



def chequeo(puntos):
	ladoV1 = puntos[0].distancia(puntos[1])
	ladoV2 = puntos[2].distancia(puntos[3])
	ladoH1 = puntos[0].distancia(puntos[2])
	ladoH2 = puntos[1].distancia(puntos[3])

	# Condicion 0: puntos posicion adecuada
	condicionX = puntos[0].x < puntos[2].x and puntos[1].x < puntos[3].x
	condicionY = puntos[0].y < puntos[1].y and puntos[2].y < puntos[3].y
	if not (condicionX and condicionY):
		raise PistaNoEncontradaException("El cuadrilatero no cumple la condicion 0")
	# Condicion 1: lados minimo de 30 y 100
	if not (ladoV1 > 60 and ladoV2 > 60 and ladoH1 > 20 and ladoH2 > 20):
		raise PistaNoEncontradaException("El cuadrilatero no cumple la condicion 1")
	# Condicion 2: lados horizontales crecientes
	if not (ladoH2 > ladoH1):
		raise PistaNoEncontradaException("El cuadrilatero no cumple la condicion 2")



''' ========================= METODOS UTILES ============================= '''


# Se establecen las estrategias de reintentos para Expansion Horizontal
def ExpansionHorizontalRecursivo(img, punto):
	punto1, punto2 = ExpansionHorizontal(img, punto)
	if punto1 is None or punto2 is None:
		if debug:
			print "Reintento 1 en ExpansionHorizontalRecursivo"
		punto1, punto2 = ExpansionHorizontal(img, punto + Punto(0,2))
		if punto1 is None or punto2 is None:
			if debug:
				print "Reintento 2 en ExpansionHorizontalRecursivo"
			punto1, punto2 = ExpansionHorizontal(img, punto - Punto(0,2))
			if punto1 is None or punto2 is None:
				raise PistaNoEncontradaException("No se han encontrado bordes")

	return punto1, punto2

# Test generacion de 10000000 numeros
# range 2.331088 segundos
# xrange 0.721298 segundos
# Tiempo para inicializar un for con xrange = 0,000214073 ms
# Tiempo de preparar un try/exception = 0,000025771 ms
# Se realiza la Expansion Horizontal
def ExpansionHorizontal(img, punto):
	_, w = img.shape[:2]
	puntoI, puntoD = (None, None)

	# Expansion hacia izquierda
	for x in xrange(punto.x - 1, 0, -1):
		if img[punto.y,x] == 255:
			puntoI = Punto(x,punto.y)
			break

	# Expansion hacia derecha
	for x in xrange( punto.x + 1, w - 1 ):
		if img[punto.y,x] == 255:
			puntoD = Punto(x,punto.y)
			break

	return puntoI, puntoD



# Se establecen las estrategias de reintentos para Expansion Vertical
def ExpansionVerticalRecursivo(img, punto, direccion):	
	ret, linea = ExpansionVertical(img, punto, direccion)
	
	# Estrategia de reintento
	if ret is False:
		if debug:
			print "No se ha encontrado borde a la 1 iteracion"

		# Coger los posteriores al primero y al ultimo
		nuevoPunto1 = linea.puntos[0] - Punto(0,1)
		nuevoPunto2 = linea.puntos[-1] + Punto(0,1)

		# Reintentar desde abajo
		try:
			punto1, punto2 = ExpansionHorizontalRecursivo(img, nuevoPunto1)
			punto = punto1 if direccion == -1 else punto2
			ret, linea = ExpansionVertical(img, punto, direccion)
		except:
			pass
		if ret is False:	
			if debug:
				print "No se ha encontrado borde a la 2a iteracion"

			# Reintentar desde arriba
			try:
				punto1, punto2 = ExpansionHorizontalRecursivo(img, nuevoPunto2)
				punto = punto1 if direccion == -1 else punto2
				ret, linea = ExpansionVertical(img, punto, direccion)
			except:
				pass
			if ret is False:
				raise PistaNoEncontradaException("Fallo en ExpansionVerticalRecursivo")

	return linea


def ExpansionVertical(img, punto, direccion):
	punto = Punto(punto.x, punto.y)
	puntos = []
	puntos += ExpansionVerticalSimple(img, punto, punto.y - 1, punto.y -23, direccion)[::-1] # invertida
	puntos += [punto]	
	puntos += ExpansionVerticalSimple(img, punto, punto.y + 1, punto.y +23, direccion)
	
	linea = Linea(punto)
	linea.puntos = puntos

	if debug:
		imagen = img.copy()
		imagen = cv2.cvtColor(imagen, cv2.COLOR_GRAY2BGR)
		for punto in puntos:
			cv2.circle(imagen,(punto.x,punto.y),1,(0,0,255),-1)
		cv2.imshow("debug",imagen)
		esperar()
		cv2.destroyWindow("debug")

	if len(puntos) < 35:
		# Supongo discontinuidad
		return False, linea
	else:
		linea.recta, linea.error = minimosCuadrados(puntos)
		if linea.error > 0.5:
			return False, linea

	return True, linea


def ExpansionVerticalSimple(img, punto, y1, y2, direccion):
	debug = False
	puntos = []
	salto = -1 if y2 < y1 else 1
	x = punto.x
	y = y1
	while y != y2:
		# Si es blanco necesito encontrar el blanco mas al interior
		if getPixel(img, x, y) == 255:
			# Blanco
			x -= direccion 
			while ( getPixel(img, x, y) == 255 ):
				x -= direccion 
			x += direccion
		# Si es negro necesito encontrar el blanco cercano
		else:
			# Intento 1: Usar 8 adyacencia
			if getPixel(img, x - direccion, y) == 255:
				x -= direccion
				continue
			elif getPixel(img, x + direccion, y) == 255:
				x += direccion
				continue
			# Intento 2: Retroceder hacia un blanco al lado del ultimo
			elif getPixel(img, x + direccion, y - salto) == 255:
				x += direccion
				continue
			else:
				# Error, discontinuidad
				break
				
		if debug:
			print "Punto encontrado en", Punto(x, y)
		puntos.append(Punto(x, y))
		y += salto
	return puntos



def getPixel(img, x, y):
	h,w = img.shape

	if x >= 0 and x < w and y >= 0 and y < h:
		return img[y, x]
	else:
		raise PistaNoEncontradaException("Fuera de indice")
		

''' ========================= UTILIDADES ========================= '''

def minimosCuadrados(puntos):
	if len(puntos) < 2:
		return None, 0
	
	# Experimental (invertir los puntos)
	puntos = [Punto(punto.y, punto.x) for punto in puntos]

	N = 0
	Sx  = 0.0
	Sy  = 0.0
	Sxy = 0.0
	Sxx = 0.0
	Syy = 0.0
	
	for punto in puntos:
		N += 1
		Sx += punto.x
		Sy += punto.y
		Sxy += punto.x * punto.y
		Sxx += punto.x * punto.x
		Syy += punto.y * punto.y
	try:	
		m = ( N*Sxy - Sx*Sy) / ( N*Sxx - Sx*Sx )
		n = ( Sxx*Sy - Sx*Sxy) / ( N*Sxx - Sx*Sx )
	except:
		return None, 0
	# Calcula la media del error
	recta = Recta(m,-1,n)

	errorNeto = 0.0
	for punto in puntos:
		errorNeto += recta.distanciaAPunto(punto)
	errorMedio = errorNeto / len(puntos)
	#pdb.set_trace()
	# y = mx + n

	# Deshacer la inversion
	recta = Recta(-1, m, n)
	return recta, errorMedio



# Sentido de las agujas del reloj = positivo
def girarImagen(img, puntoGiro, anguloGiro):
	rows,cols = img.shape[:2]
	M = cv2.getRotationMatrix2D((puntoGiro.x, puntoGiro.y), anguloGiro,1)
	return cv2.warpAffine(img,M,(cols,rows))

def calcularGiro(linea):
	r = linea.recta
	m = r.pendiente()
	if m != float('inf'):
		giro = math.atan(1/m)
		giro = math.degrees(giro)
	else:
		giro = 0
	return - giro
	


''' ================== DIBUJADO ================== '''

# Este metodo ofrece un dibujado de conjunto lineas de forma invertida (para lineas verticales)
def dibujarLineas(imagen, rectas):
	for color in rectas.iterkeys():
		for recta in rectas[color]:
			if recta != None:
				cv2.line(imagen, (int(recta.resolver(x=0)), 0), (int(recta.resolver(x=ancho)), ancho), color, 1, cv2.LINE_AA)

def dibujarRectangulo(img, puntos, color, grueso):
	cv2.line(img, (puntos[0].x, puntos[0].y), (puntos[1].x, puntos[1].y), color, grueso, cv2.LINE_AA)
	cv2.line(img, (puntos[2].x, puntos[2].y), (puntos[3].x, puntos[3].y), color, grueso, cv2.LINE_AA)
	cv2.line(img, (puntos[0].x, puntos[0].y), (puntos[2].x, puntos[2].y), color, grueso, cv2.LINE_AA)
	cv2.line(img, (puntos[1].x, puntos[1].y), (puntos[3].x, puntos[3].y), color, grueso, cv2.LINE_AA)

def esperar():
	k = cv2.waitKey(0)
	if k == 27:         # wait for ESC key to exit
		cv2.destroyAllWindows()
		exit(0)
