from scottSock import scottSock
import json
import time
from source_extraction import *
import tempfile
import sys
import os
import tempfile
from astropy.io import fits

def solvefitsfd( img=fits.open( 'imagep120.fits' ), extnum=0, port=9002 ):
	ra, dec = img[0].header['ra'] , img[0].header['dec']
	naxis1, naxis2 = img[extnum].header['naxis1'], img[extnum].header['naxis2']
	
	tblargs ={
		'ra':ra,
		'dec':dec,
		'npix1':naxis1,
		'npix2':naxis2,
	}
	
	objs = getobjects( img[0].data )
	
	fitstbl = mkfitstable( objs )
	for key, val in tblargs.iteritems():
		fitstbl.header[key] = val
		
	tname = tempfile.mktemp()
	fitstbl.writeto( tname )
	
	fitstbl_fd=open(tname, 'rb')
	
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
			print "The file {} was not downloaded error was {}".format( fname, err )



	for key, val in meta.iteritems():
		if str(key) != "files" and str(key) != "forder":
			outfits[key] = val
			
			
			
	return outfits		
	
	
	
def addwcs( imgfd, wcsfd, imgext=0, wcsext=0 ):
	#add wcs and try to save in place
	for key, value in wcsfd[wcsext].header.iteritems():
		
		print key, wcsfd[wcsext].header[key]
		
		if key == "COMMENT":
			imgfd[imgext].header.add_comment( value )
			
		elif key == "HISTORY":
			imgfd[imgext].header.add_history( value )
			
		else:
		
			if key in imgfd[imgext].header:
				imgfd[imgext].header[key+'_orig'] = imgfd[imgext].header[key]
			
			
			if key != 'HISTORY':
				imgfd[imgext].header[key] = ( wcsfd[wcsext].header[key], "From astrometry.net" )
	
	

			
			
			
	
	
if __name__ == '__main__':
	for img in sys.argv[1:]:
		
		fitsfd = fits.open( img, mode='update' )
		resp = solvefitsfd( fitsfd )
		
		if 'wcs' in resp.keys():
			addwcs( fitsfd, resp['wcs'] )
	
			fitsfd.flush( output_verify='ignore' )
				
		
		
	
