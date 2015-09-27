import numpy as np
import time
import sys
import cv2

from libreria import *
from libreriaDatos import *
from pymavlink.tools.mavplayback import *
import traceback




if len(sys.argv) != 3:
	print "\nSe recibieron", len(sys.argv), "argumentos\nUso: python principal.py <video> <datos>"
	exit()

tiempoTotal = 0
numero = 0
def detectar(img, punto):
	global ultimaDeteccion, tiempoTotal, numero
	puntos = None
	if punto is None:
		return False, None
	try:
		tk1 = cv2.getTickCount()
		puntos = programa(img, punto.x, punto.y)
		try:
			chequeo(puntos)
		except PistaNoEncontradaException as e1:
			tiempoTotal += (cv2.getTickCount() - tk1)/ cv2.getTickFrequency() * 1000
			numero += 1
			raise e1
		ultimaDeteccion = puntos
		return True, puntos
	except PistaNoEncontradaException as e1:
		print e1
		return False, None
	except:
		traceback.print_exc()
		exit()

def tiempoframe(tk1):
	if limitarFrame:
		return ((cv2.getTickCount() - tk1)/ cv2.getTickFrequency()) < (frametime - 0.016) # 16ms es el tiempo de deteccion exitosa
	return True
	

''' ================= PROGRAMA PRINCIPAL =================='''
# Recursos
video = cv2.VideoCapture(str(sys.argv[1])) # Ejemplo 'vuelo4.mp4'
datos=ReceptorDatos(str(sys.argv[2])) # Ejemplo 'pymavlink/tools/2014-07-30-13-34-12.tlog'
font = cv2.FONT_HERSHEY_SIMPLEX

# Parametros de inicio
framerate = 30.45
frametime = 1/framerate
saltarFrames = 0 #+ 1050 # Sirve para iniciar en un posterior a la sincronizacion
inicioVideo = 0 + 2092 + saltarFrames # en frames
inicioDatos = 0 + 546.92 + saltarFrames / framerate # en segundos

font = cv2.FONT_HERSHEY_SIMPLEX

numFrame = 0
saltarFrames = 0

startTime = 0.0
currentTime = 0.0 
elapsedTime = 0.0

limitarFrame = False

# Establecer configuracion
video.set(1, inicioVideo)
libd = libDatos()
libd.puntoEstimacion1 = None
libd.puntoEstimacion2 = None

puntos = None

errores = 0
detecciones = 0
aciertos = 0

ultimaDeteccion = None

ejeImagen = Recta(Punto(0, ancho/2), Punto(alto, ancho/2))
#fourcc = cv2.VideoWriter_fourcc('H','2','6','4')
#out = cv2.VideoWriter('output con eje bisectriz.avi',fourcc, 25.0, (640,480))

# Bucle principal
while(video.isOpened() and video.get(1) < 9470 + inicioVideo):
	tk1 = cv2.getTickCount()

	print "Frame", numFrame

	# Actualizar frame
	ret, frame = video.read()
	# Actualizar mensajes
	elapsedTime = (currentTime - startTime) + inicioDatos
	datos.updateMessages(elapsedTime)
	libd.recogerMensajes(datos)

	punto1, punto2, punto3 = libd.calculoPuntoOrigen()

	ejePista = None

	if libd.deteccion:
		print "DETECCION"
		detecciones += 1
		exito = False
		# Intento 1: Por estimaciones del frame anterior
		if libd.estimacionDisponible:
			print "Estimacion 1"
			exito, puntos = detectar(frame, libd.puntoEstimacion1)
			if not exito and tiempoframe(tk1):	
				print "Estimacion 2"
				exito, puntos = detectar(frame, libd.puntoEstimacion2)

		# Intento 2: Por los puntos calculados
		if not exito and tiempoframe(tk1):
			print "Punto 1"	
			exito, puntos = detectar(frame, punto1)
		if not exito and tiempoframe(tk1):
			print "Punto 2"	
			exito, puntos = detectar(frame, punto2)
		if not exito and tiempoframe(tk1):
			print "Punto 3"	
			exito, puntos = detectar(frame, punto3)

		if not exito and ultimaDeteccion is not None:
			print "UltimaDeteccion"
			puntos = ultimaDeteccion
			ultimaDeteccion = None # Liberar cuando se use
			exito = True			

		if exito:
			aciertos += 1
			print "DETECCION ACERTADA"
			libd.calculaEstimacion(puntos)
			dibujarRectangulo(frame, puntos, (0,255,0),2)

			# Dibujar el eje de la pista
			#	Por el punto medio
			#ejePista = Recta((puntos[0] + puntos[2])/2, (puntos[1] + puntos[3])/2)
			#	Por la bisectriz
			recta1 = Recta(puntos[0], puntos[1])
			recta2 = Recta(puntos[2], puntos[3])
			puntoCorte = recta1.puntoCorte(recta2)
			angulo1 = recta1.angulo(recta2)
			recta1.giro(puntoCorte, angulo1/2)
			ejePista = Recta(recta1.b, recta1.a, recta1.c)
			cv2.putText(frame, 'STATUS: DETECTED',(24,40), font, 0.8,(255,255,255),2,cv2.LINE_AA)
		else:
			print "DETECCION FALLIDA"
			#frame = cv2.copyMakeBorder(frame[10:480-10, 10:640-10],10,10,10,10,cv2.BORDER_CONSTANT,value=(0,0,255))
			cv2.putText(frame, 'STATUS: FAILED!!!',(24,40), font, 0.8,(255,255,255),2,cv2.LINE_AA)
			errores += 1
			ultimaDeteccion = None
			libd.estimacionDisponible = False

	else:
		ultimaDeteccion = None
		cv2.putText(frame, 'STATUS: OUT OF RANGE',(24,40), font, 0.8,(255,255,255),2,cv2.LINE_AA)
		print "No hay deteccion"
	cv2.circle(frame,(libd.punto1.x,libd.punto1.y),4,(0,255,0),-1, cv2.LINE_AA)
	cv2.circle(frame,(libd.punto2.x,libd.punto2.y),4,(0,0,255),-1, cv2.LINE_AA)
	cv2.circle(frame,(libd.punto3.x,libd.punto3.y),4,(255,0,0),-1, cv2.LINE_AA)
	dibujarRectangulo(frame, libd.cuadroAceptacion,(255,255,255), 1)
	
		
	
	dibujarLineas(frame, {(0,0,200) : [ejePista, ejeImagen]})
	cv2.imshow("frame", frame)
	#out.write(frame)
	print
	# Mecanismo de avance rapido
	
	if saltarFrames == 0:
		k = cv2.waitKey(0)
		if k == 27:  # ESC
			break
		if k == 65363:
			saltarFrames += 120 # 5 segundos
		
	else:
		saltarFrames -= 1
	'''
	# Saltar los cambios de rumbo
	if numFrame == 1470 - 1050:
		saltarFrames = 890

	if numFrame == 2845 - 1050:
		saltarFrames = 1145

	if numFrame == 4325 - 1050:
		saltarFrames = 845

	if numFrame == 5580 - 1050:
		saltarFrames = 755

	if numFrame == 6850 - 1050:
		saltarFrames = 810

	if numFrame == 8115 - 1050:
		saltarFrames = 715
	'''	


	# Avance de frame (NO COMENTAR)
	numFrame += 1
	currentTime += 1.0/framerate
	print (cv2.getTickCount() - tk1)/ cv2.getTickFrequency() * 1000, "ms","\n"

# Cierre
print numFrame
print "Detecciones:", detecciones
print "Errores:", errores
print "Aciertos:", aciertos
print tiempoTotal/numero
print numero
#out.release()
video.release()
cv2.destroyAllWindows()
