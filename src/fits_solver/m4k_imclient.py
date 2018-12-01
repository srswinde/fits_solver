#!/usr/bin/python

from scottSock import scottSock
import json
import time
from .source_extraction import *
import tempfile
import sys
import os
import tempfile

def solvefitsfd( img, extnum=0, port=9002 ):
	objs = getobjects( img[extnum].data )
	#set up the tblargs
	ra, dec = img[0].header['ra'] , img[0].header['dec']
	naxis1, naxis2 = img[extnum].header['naxis1'], img[extnum].header['naxis2']

	tblargs ={
		'ra':ra,
		'dec':dec,
		'npix1':naxis1,
		'npix2':naxis2,
	}	
	

		
	fitstbl = mkfitstable( objs )
	for key, val in tblargs.items():
		fitstbl.header[key] = val
	tname = tempfile.mktemp()
	fitstbl.writeto( tname )


	fitstbl_fd=open(tname, 'rb')
	
	soc = scottSock( "nimoy", port  )

	soc.send( fitstbl_fd.read() )
	while 1:
		try:
			meta = soc.recv( 256 )
			break
		except Exception:
			pass

	try:
		meta = json.loads( meta )
	except Exception as err:
		return {}



	outfits = {}
	for fname in meta['forder']:
		fsize = meta['files'][fname]
		data = ''		
		buffsize = 128
		#print "File is {} filesize if {}".format(fname,fsize)
		while 1:

			if fsize > buffsize:
				newData = soc.recv( buffsize )
				
				if len(newData) == 0:
					#print "Soc recieved no data for file {}".format(fname)
					#print "Buffer size is {} file has {} bytes left, data is {} bytes".format(buffsize, fsize, len(data))
					break
				
				data+=newData
				
				fsize-=len(newData)
			else:
				data+=soc.recv(fsize)
				break
			
		tempname = tempfile.mktemp()

		tmpfd = open( tempname, 'wb' )
		
		tmpfd.write( data )
		tmpfd.close()
		try:
			outfits[fname] = fits.open( tempname )
		except Exception as err:
			print("The file {} was not downloaded error was {}".format( fname, err ))

		os.remove(tempname)

	for key, val in meta.items():
		if str(key) != "files" and str(key) != "forder":
			outfits[key] = val

	return outfits
		
		
def main( imgname="test0021.fits", inDir='/home/bigobs/data/scott/26april16', outDir=None, extnum=1, port=9002, **headervals):


	if inDir.endswith('/'): endDir = endDir[:-1]
	if outDir:	
		if outDir.endswith('/'): outDir = outDir[:-1]
	else:
		outDir = "{0}/astrometry".format(inDir)



	if not os.path.exists(outDir):
		os.makedirs(outDir)

	path2fitsdata = "{0}/{1}".format(inDir, imgname)
	img=fits.open(path2fitsdata)

	#set up the tblargs
	ra, dec = img[0].header['ra'] , img[0].header['dec']
	naxis1, naxis2 = img[1].header['naxis1'], img[1].header['naxis2']

	tblargs ={
		'ra':ra,
		'dec':dec,
		'npix1':naxis1,
		'npix2':naxis2,
	}	

	for key, val in headervals.items():
		tblargs[key] = val
	
	print(tblargs)
	sources = getobjects( img[extnum].data )
	fitstbl = mkfitstable( sources )
	
	for key, val in tblargs.items():
		fitstbl.header[key] = val

	tname = "{0}/{1}_{2}.axy".format(outDir, imgname.replace(".fits", ''), extnum)
	print(tname)
	fitstbl.writeto( tname )
		
	
	f=open(tname, 'rb')

	soc = scottSock( "nimoy", port  )

	soc.send( f.read() )


	while 1:
		try:
			meta = soc.recv( 256 )
			break
		except Exception:
			print("waiting")
		
	meta = json.loads( meta )





	data=""
	for key,val in meta['files'].items():
		buffsize = 1024
		while 1:
			if val > buffsize:
				data+=soc.recv( buffsize )
				val-=buffsize
			else:
				data+=soc.recv(val)
				break
	
		print("{0}/{1}_{2}.{3}".format(outDir, imgname, extnum, key))
		tmpfd = open("{0}/{1}_{2}.{3}".format(outDir, imgname, extnum, key), 'wb')
		tmpfd.write( data )
		tmpfd.close()

		
	print(meta)

	soc.close()
	
if __name__ == '__main__':
	port = int(sys.argv[1])
	main( port=port )



