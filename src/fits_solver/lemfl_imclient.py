#!/usr/local/bin/python

from scottSock import scottSock
import json
import time
from source_extraction import *
import tempfile
from astropy.io import fits
import os
import sys
from astro.angles import RA_angle, Dec_angle, Deg10, Angle
from astro.locales import mtlemmon
from astro.astrodate import starDate

def main( imgname="subn4.fits", inDir='/home/apt/images', outDir="astrometry" ):

	if inDir.endswith('/'): endDir = endDir[:-1]
	if outDir.endswith('/'): outDir = outDir[:-1]
	tname = writetmpfits( "{0}/{1}".format(inDir, imgname ) )
	
	if not os.path.exists(outDir):	
		os.mkdir( outDir )
	fitsfd = fits.open(imgname)
	telra, teldec = Angle( fitsfd[0].header['apra'] ).Format("hours"), Angle( fitsfd[0].header['apdec'] ).Format("degarc180")
	#width, height = fitsfd[0].header['naxis1'], fitsfd[0].header['naxis2']
	f=open(tname, 'rb')
	
	soc = scottSock( "nimoy", 9996  )

	soc.send( f.read() )
	telra, teldec = Angle( fitsfd[0].header['apra'] ), Angle( fitsfd[0].header['apdec'] )
	jd = fitsfd[0].header['BJD']
	
	fitsfd.close()
	while 1:
		try:
			meta = soc.recv( 256 )
			break
		except Exception:
			pass#print "waiting"
		
	meta = json.loads( meta )





	data=""
	for key,val in meta['files'].iteritems():
		buffsize = 1024
		while 1:
			if val > buffsize:
				data+=soc.recv( buffsize )
				val-=buffsize
			else:
				data+=soc.recv(val)
				break
	
		tmpfd = open("table.{0}".format(key), 'wb')
		tmpfd.write( data )
		tmpfd.close()
	try:	
		calra, caldec = RA_angle( str(meta['ra']) ), Dec_angle( str(meta['dec']) )
	        alt, az = mtlemmon(starDate(jd=jd)).eq2hor(calra, caldec)
		print "{iname} {ra} {dec} {telra} {teldec}".format( iname=imgname, telra=telra.Format("hours"), teldec=teldec.Format("degarc180"), **meta ), alt.deg10, az.deg10
	except KeyError:
		print "{iname}".format(iname=imgname)

	soc.close()


for imfile in sys.argv[1:]:
	main(imfile, '.')
	
