#!/usr/bin/python

from server import Server, Client
import time
from fits_solver.imsolve import *
from astropy.io import fits
from astro.angles import *
import tempfile
import shlex
import subprocess
import subprocess32
import os
import select
from astro.locales import mtlemmon
import sys


class catcher(Client):
	def __init__( self, (client, address) ):
		Client.__init__( self, (client, address) )
		print "Imclient connected"
		self.size = 1024
		self.count = 0
		self.headerData = False
		self.bytes = 0
		self.inData = False
		self.imgData = []
		self.x = 0
		self.y = 0
		self.dCount = 0
		self.client.settimeout( 0.5 )
		#self.img = numpy.zeros( ( 765, 510 ), dtype=numpy.int )
		self.ALL = ""
		
	def run(self):
		running = 1
		while running:
			try:
				data = self.client.recv( self.size )
			except Exception:
				data = None
			
			if data:
				running = self.handle( data )

			else:
				running = 0

				fname = "{0}.fits".format( tempfile.mktemp() )
				print "writing fits file", fname
				f=open( fname, 'wb' )
				f.write( self.ALL )
				f.close()
				resp = self.solve(fname)
				sentdata = 0
				buffsize = 1024
				while sentdata + buffsize < len(resp):
					self.client.send( resp[sentdata:sentdata+buffsize] )
					sentdata+=buffsize
					print sentdata, len(resp)
				self.client.send( resp[-(len(resp) - sentdata):] )
					
				self.client.close()
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
		
	def getradec( self, img ):
			return img[1].header['ra'] , img[1].header['dec'] 
			
	
	def solve(self, fname):
		odir = "/home/scott/data/imserver"
		bname = time.ctime().replace(" ", '_')
		fitsfile = fits.open(fname)
		ra,dec = self.getradec(fitsfile)
		naxes = ( fitsfile[1].header['npix1'], fitsfile[1].header['npix2'] )
		fitsfile.close()
		
		default_params = {
		
			'scale-units': 'app',
			'scale-low':0.1,
			'scale-high':2.0,
			'D':odir,
			'o':bname,
			'ra':ra,
			'dec':dec,
			'F': 1,
			'w':	naxes[0],
			'e':	naxes[1],
			'X': 	'x',
			'Y': 	'y',
			's':	'fwhm',
			'radius': 5,
		}

		default_flags =  ['overwrite', 'crpix-center']
		#astro_params['ra'], astro_params['dec'] = getfl50radec( img )
		cmd = astrometry_cmd( fname, default_params, default_flags )
		print cmd
		try:
			#subprocess.check_output( shlex.split( cmd ) )
			resp=subprocess32.check_output( shlex.split( cmd ), timeout=10 )
			
		except Exception as err:
			
			print err
		print "response is ",resp,'end resp'
		print 'bname is', bname
		metadata = {'solved':False}
		metadata['files']={}
		filedata = ""
		
		if os.path.exists( "{0}/{1}.solved".format( odir, bname ) ):
			#flist = ["wcs", "rdls", "corr", "match"]:
			flist = ['wcs']
			for ftype in flist:
				tmpfd = open("{0}/{1}.{2}".format(odir, bname, ftype ), "rb" )
				fdata = tmpfd.read()
				tmpfd.seek(0,0)
				if ftype == 'wcs':
					tmpfitsfd = fits.open(  tmpfd )
					metadata['ra'], metadata['dec'] = RA_angle( Deg10( tmpfitsfd[0].header['crval1'] ) ).Format("hours"), Dec_angle( Deg10( tmpfitsfd[0].header['crval2'] ) ).Format( "degarc180" )					
					
				
				tmpfd.close()
				print ftype, len(fdata)
				metadata['files'][ftype] = len( fdata )
				filedata+=fdata
				del fdata
			print "Solved"
			metadata['solved'] = True
		else:
			flist = []		

		metadata["forder"] = flist
		metajson = json.dumps( metadata )
		metajson = metajson+(256-len(metajson))*" "
		
		return metajson+filedata
		
if __name__ == "__main__":
	port = int(sys.argv[1])
	s=Server(port, handler=catcher)

	s.run()

