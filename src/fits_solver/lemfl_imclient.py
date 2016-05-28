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

<<<<<<< HEAD
def main( imgname="subn4.fits", inDir='/home/apt/images', outDir="astrometry", extnum=0, port=9002, **headervals):
=======
example = {
                  "amp11Dec": "+85:05:02.77",
        "amp11RA": "08:21:46.83",
        "amp6Dec": "+84:34:01.54",
        "amp6RA": "08:58:31.27",
        "lst": "04:10:20",
        "midpointDec": "+84:49:32.15",
        "midpointRA": "08:40:09.05",
        "name": "pr0002",
        "obsDec": "+84:59:59.90",
        "obsHA": "-04:33:53",
        "obsRA": "08:41:13.24",
        "offsetDec": 359.82562633352575,
        "offsetRA": 359.7325301822657
}


def main( imgname="20160423_080719_n45.fits", inDir='/home/scott/data/lemfl50', outDir="astrometry", line=True ):
>>>>>>> 4754d2981c88a9f699945b80a3a60f888f70870a

	if inDir.endswith('/'): inDir = inDir[:-1]
	if outDir.endswith('/'): outDir = outDir[:-1]
<<<<<<< HEAD
	#tname = writetmpfits( "{0}/{1}".format(inDir, imgname ) )
	 
	if not os.path.exists(outDir):	
		os.mkdir( outDir )
	fitsfd = fits.open("{0}/{1}".format(inDir, imgname))
	telra, teldec = Angle( fitsfd[0].header['apra'] ).Format("hours"), Angle( fitsfd[0].header['apdec'] ).Format("degarc180")
	#width, height = fitsfd[0].header['naxis1'], fitsfd[0].header['naxis2']
	#f=open(tname, 'rb')
	
	telra, teldec = Angle( fitsfd[0].header['apra'] ).deg10, Angle( fitsfd[0].header['apdec'] ).deg10
	naxis1, naxis2 = fitsfd[0].header['naxis1'], fitsfd[0].header['naxis2']
	tblargs ={
		'ra':telra,
		'dec':teldec,
		'npix1':naxis1,
		'npix2':naxis2,
	}	
	
	sources = getobjects( fitsfd[0].data )
	fitstbl = mkfitstable( sources )
	for key, val in tblargs.iteritems():
		fitstbl.header[key] = val
	tname = "{0}/{1}_{2}.axy".format(outDir, imgname.replace(".fits", ''), extnum)
	print tname
	
	if os.path.exists(tname):
		os.remove(tname)
	
	fitstbl.writeto( tname )
	soc = scottSock( "nimoy", 9002  )
	f=open(tname, 'rb')
=======

		

	
	if not os.path.exists(outDir):	
		os.mkdir( outDir )


	fitsfd = fits.open("{0}/{1}".format(inDir, imgname ))
	telra, teldec = Angle( fitsfd[0].header['apra'] ).Format("hours"), Angle( fitsfd[0].header['apdec'] ).Format("degarc180")
	npix1, npix2 = fitsfd[0].header['naxis1'], fitsfd[0].header['naxis2']

	tblargs ={
		'ra':telra,
		'dec':teldec,
		'npix1':npix1,
		'npix2':npix2,
	}

		
	tname = writetmpfits( "{0}/{1}".format(inDir, imgname ), extnum=0, **tblargs )

	f=open(tname, 'rb')
	
	soc = scottSock( "nimoy", 9002  )
>>>>>>> 4754d2981c88a9f699945b80a3a60f888f70870a

	soc.send( f.read() )
	
	jd = fitsfd[0].header['BJD']
	f.close()
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
		if line:
			print "{iname} {ra} {dec} {telra} {teldec}".format( iname=imgname, telra=telra.Format("hours"), teldec=teldec.Format("degarc180"), **meta ), alt.deg10, az.deg10
	except KeyError:
		print "{iname}".format(iname=imgname)

	
	soc.close()
	
	try:
		output = {
			"midpointDec": meta['dec'],
		    "midpointRA": meta['dec'],
		    "obsDec": teldec.Format("degarc180"),
		    "obsRA": telra.Format("hours"),
			'lst':	mtlemmon(stardate=starDate(jd=jd)).LST.Format("hours"), 

		}
	except Exception:
		return False

	return output

def tpoint_json(inDir='.', outfile="lemfl50.json"):
	data = []
	for imgname in os.listdir(inDir):
		if imgname.endswith('fits'):
			datum = main(imgname, inDir, line=False)
			if datum:
				data.append( main(imgname, inDir, line=False) )
				print datum
	with open(outfile, 'w') as outfd:
		json.dump(data, outfd)

	

if __name__ == '__main__':
	for imfile in sys.argv[1:]:
		main(imfile, '.')


<<<<<<< HEAD
#for imfile in sys.argv[1:]:
	#main(imfile, '.')
main( "20160526_083730_n93.fits", "/home/sswindell/" ) 
=======
>>>>>>> 4754d2981c88a9f699945b80a3a60f888f70870a
	
