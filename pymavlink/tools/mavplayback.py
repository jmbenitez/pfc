#!/usr/bin/env python

'''
play back a mavlink log as a FlightGear FG NET stream, and as a
realtime mavlink stream

Useful for visualising flights
'''
import os
from pymavlink import mavutil

class ReceptorDatos():
	def __init__(self, filename):

		# Leer el tamanyo del archivo LOG
		self.filesize = os.path.getsize(filename)

		# Iniciarlizar la conexion con MAVlink
		self.mlog = mavutil.mavlink_connection(filename, planner_format=None, robust_parsing=True)
		
		# Diccionario que almacena los ultimos mensajes junto con sus nombres
		self.msgs = {'ATTITUDE': None, 'GLOBAL_POSITION_INT': None, 'VFR_HUD': None}
		self.bytes = {'ATTITUDE': 0, 'GLOBAL_POSITION_INT': 0, 'VFR_HUD': 0}
		self.nextMsgs = {'ATTITUDE': None, 'GLOBAL_POSITION_INT': None, 'VFR_HUD': None}

		# Recibir el primer mensaje para inicializar el tiempo
		while True:
			msg = self.mlog.recv_match(type=self.msgs.keys(),condition=None)
			if msg is None and self.mlog.f.tell() > self.filesize - 10:
				print "ERROR: Fin de finchero"
				raise
			if msg is not None:
				self.timestamp = msg._timestamp
				break

		# self.now = time.strftime("%H:%M:%S %d/%m/%Y", time.localtime(self.last_timestamp))
	

	# Se utiliza para buscar el proximo mensaje de algun tipo
	def findNext(self, mtype, elapsedTime):
		# Recibir proximo mensaje
		msg = self.mlog.recv_match(type=mtype,condition=None)
		if msg is None and self.mlog.f.tell() > self.filesize - 10:
			print "ERROR: Fin de finchero"
			print self.mlog.f.tell()
			print self.filesize
			print msg is None
			raise
	
		# Si no habia ningun mensaje se actualiza
		if self.msgs[mtype] is None:
			self.msgs[mtype] = msg
			self.bytes[mtype] = self.mlog.f.tell()

		# Comprobar si el nuevo es antiguo, si lo es devuelvo None para avanzar un mensaje mas
		if (msg._timestamp - self.timestamp) < elapsedTime:
			self.msgs[mtype] = msg
			self.bytes[mtype] = self.mlog.f.tell()
			return None
		
		# Si el mensaje es mas nuevo se pone en proximos mensajes
		self.nextMsgs[mtype] = msg

		return 0
		
				
	def getMessage(self, mtype, elapsedTime):
		# Se comprueba que no se ha llegado al proximo mensaje
		nextMsg = self.nextMsgs[mtype]
		if nextMsg is not None and (nextMsg._timestamp - self.timestamp) > elapsedTime:
			return

		# Sino, hay que actualizar. Se recuerda la posicion donde estuvo el mensaje actual
		currentPos = self.bytes[mtype]
		self.mlog.f.seek(currentPos)

		# Encontrar mensaje para el tiempo
		ret = None
		while( ret is None ):
			ret = self.findNext(mtype, elapsedTime) 



	def updateMessages(self, elapsedTime):
		#print time.strftime("%H:%M:%S %d/%m/%Y", time.localtime(self.timestamp + elapsedTime))
		for key in self.msgs.keys():
			self.getMessage(key, elapsedTime)
			#print self.msgs[key]

