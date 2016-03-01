from server import Server, Client
import time
from imsolve import *
from astropy.io import fits
from astro.angles import *

class catcher(Client):
	def __init__( self, (client, address) ):
		Client.__init__( self, (client, address) )
		self.size = 1024
		self.count = 0
		self.headerData = False
		self.bytes = 0
		self.inData = False
		self.imgData = []
		self.x = 0
		self.y = 0
		self.dCount = 0
		#self.img = numpy.zeros((765, 510), dtype=numpy.int)
		self.ALL = ""
		
	def run(self):
		running = 1
		while running:
			data = self.client.recv( self.size )
			if data:
				running = self.handle( data )

			else:
				running = 0
				self.client.close()
				
				fname = '{0}.fits'.format( time.asctime().replace(' ','_') )
				print "writing fits file", fname
				f=open( fname, 'wb' )
				f.write( self.ALL )
				f.close()
				
				astro_params['ra'], astro_params['dec'] = getfl50radec( img )
				cmd = astrometry_cmd( fname, astro_params, astro_flags )
				
				#hdu = fits.PrimaryHDU(numpy.transpose(self.img))
				#hdulist = fits.HDUList([hdu])
				#hdulist.writeto('new.fits')
				#print self.img

	def handle( self, data ):
		if self.size == 256:

			self.infoStr = data
			print self.infoStr
			self.size = 1024

		else:
			self.ALL+=data
			

		return 1
		
	def getradec(self, img):
			ra,dec = Angle( img[0].header['apra'] ), Angle( img[0].header['apdec'] )
			
			
s=Server(9996, handler=catcher)

s.run()
