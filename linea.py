class Linea:
		def __init__(self, *args):
			if len(args) == 1: 		
				self.punto = args[0]
			self.recta = None
			self.puntos = []
			self.error = 0.0

		def vaciarPuntos(self):
			self.puntos = []

		def __str__( self ):
			return 'Punto: %s, Recta: %s, Puntos: %s, Error: %s' % (self.punto, self.recta, len(self.puntos), self.error)
